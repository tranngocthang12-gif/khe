"""Khế v0.1 — bằng chứng và trạng thái.

Attestation là file JSON do *bộ chạy* (khe attest / CI) phát hành, không phải
do agent soạn khối viết. Trạng thái của mỗi cam kết được TÍNH từ attestation
và mã sản phẩm hiện tại, không được khai.

Trạng thái:
    pass          có kết quả đạt, gắn đúng mã sản phẩm hiện tại
    fail          có kết quả phản bác
    inconclusive  phép kiểm lỗi / hết giờ — tính như fail trong chỉ số
    not_run       đã khai phép kiểm, chưa có attestation
    stale         attestation thuộc mã sản phẩm khác
    mismatch      loại kiểm trong attestation khác loại đã khai
    judgment      câu không có oracle — không bao giờ pass
"""
from __future__ import annotations

import glob
import json
import os
from typing import Dict, List, Optional, Tuple

RESULTS = ("pass", "fail", "inconclusive")
REQUIRED = ("claim", "type", "ref", "result", "artifact", "runner", "config", "timestamp")
NOT_PASS = ("fail", "inconclusive", "not_run", "stale", "mismatch", "judgment")


def load_attestations(directory: Optional[str]) -> Tuple[List[dict], List[str]]:
    atts: List[dict] = []
    problems: List[str] = []
    if not directory or not os.path.isdir(directory):
        return atts, problems
    for p in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{p}: không đọc được JSON ({e})")
            continue
        missing = [k for k in REQUIRED if k not in data]
        if missing:
            problems.append(f"{p}: thiếu trường {missing}")
            continue
        if data["result"] not in RESULTS:
            problems.append(f"{p}: result «{data['result']}» không hợp lệ")
            continue
        data["_path"] = p
        atts.append(data)
    return atts, problems


def latest_for(claim_id: str, atts: List[dict]) -> Optional[dict]:
    xs = [a for a in atts if a.get("claim") == claim_id]
    return max(xs, key=lambda a: a["timestamp"]) if xs else None


def compute_status(claim, atts: List[dict], head_sha: Optional[str]) -> Tuple[str, Optional[dict]]:
    if claim.check_type == "judgment":
        return "judgment", None
    a = latest_for(claim.id, atts)
    if a is None:
        return "not_run", None
    if a["type"] != claim.check_type:
        return "mismatch", a
    if head_sha and a["artifact"] != head_sha:
        return "stale", a
    return a["result"], a


def status_table(block, atts: List[dict], head_sha: Optional[str]) -> Dict[str, dict]:
    table: Dict[str, dict] = {}
    for c in block.claims:
        st, a = compute_status(c, atts, head_sha)
        table[c.id] = {
            "kind": c.kind,
            "text": c.text,
            "check_type": c.check_type,
            "check_ref": c.check_ref,
            "status": st,
            "evidence": None if a is None else {
                "path": a["_path"],
                "artifact": a["artifact"],
                "runner": a["runner"],
                "config": a["config"],
                "timestamp": a["timestamp"],
            },
        }
    return table
