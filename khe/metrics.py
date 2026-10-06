"""Khế v0.1 — bốn số sống còn.

Đầu vào: ledger.jsonl — mỗi dòng một PR đã merge, điền dần khi lỗi lộ ra sau merge.
    {
      "pr": 12, "arm": "C",                      # A = CI hiện tại · B = tiêu chí+bộ kiểm độc lập · C = B + Khế · T = mẫu ô trống
      "claims": [{"id": "M1", "status": "pass"}, ...],
      "open":   [{"id": "O1", "source": "declared"}, ...],
      "human_assumptions": [{"id": "A2", "approve_seconds": 3, "later_wrong": true}],
      "bugs":   [{"id": "B1", "severity": "high", "linked_open": "O1", "linked_claim": null}],
      "blocked": true, "false_block": false, "cycle_hours": 5.2
    }

Bốn số (theo nhánh):
  1. open_hit      — lỗi sau merge đã nằm sẵn trong sổ CHƯA KIỂM / tổng lỗi
  2. false_pass    — lỗi rơi vào cam kết đã «pass» / tổng cam kết pass   (phải THẤP hơn đối chứng)
  3. rubber_stamp  — tỷ lệ giả định [human] duyệt < 5s; và tỷ lệ số đó sau hóa ra sai
  4. cost          — tỷ lệ chặn sai; giờ chu trình trung bình

Luật giết (nhánh C so với T/B): open_hit = 0 VÀ false_pass không thấp hơn đối chứng → bỏ.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, List

STAMP_SECONDS = 5


def load(path: str) -> List[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{n}: JSON lỗi — {e}")
    return rows


def _ratio(a: int, b: int) -> float | None:
    return None if b == 0 else round(a / b, 3)


def compute(rows: List[dict]) -> Dict[str, dict]:
    by_arm: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_arm[r.get("arm", "?")].append(r)

    out: Dict[str, dict] = {}
    for arm, prs in sorted(by_arm.items()):
        bugs = [b for r in prs for b in r.get("bugs", [])]
        open_ids = {(r["pr"], o["id"]) for r in prs for o in r.get("open", [])}
        bug_in_open = sum(1 for r in prs for b in r.get("bugs", []) if b.get("linked_open") and (r["pr"], b["linked_open"]) in open_ids)
        passed = [(r["pr"], c["id"]) for r in prs for c in r.get("claims", []) if c.get("status") == "pass"]
        bug_in_pass = sum(1 for r in prs for b in r.get("bugs", []) if b.get("linked_claim") and (r["pr"], b["linked_claim"]) in set(passed))
        ha = [h for r in prs for h in r.get("human_assumptions", [])]
        stamped = [h for h in ha if h.get("approve_seconds") is not None and h["approve_seconds"] < STAMP_SECONDS]
        stamped_wrong = [h for h in stamped if h.get("later_wrong")]
        blocked = [r for r in prs if r.get("blocked")]
        false_block = [r for r in blocked if r.get("false_block")]
        hours = [r["cycle_hours"] for r in prs if isinstance(r.get("cycle_hours"), (int, float))]
        sev = defaultdict(int)
        for b in bugs:
            sev[b.get("severity", "?")] += 1

        out[arm] = {
            "prs": len(prs),
            "bugs_total": len(bugs),
            "bugs_by_severity": dict(sev),
            "open_hit": {"count": bug_in_open, "ratio": _ratio(bug_in_open, len(bugs))},
            "false_pass": {"count": bug_in_pass, "passed_claims": len(passed), "ratio": _ratio(bug_in_pass, len(passed))},
            "rubber_stamp": {
                "human_assumptions": len(ha),
                "stamped_lt5s_ratio": _ratio(len(stamped), len(ha)),
                "stamped_later_wrong_ratio": _ratio(len(stamped_wrong), len(stamped)),
            },
            "cost": {
                "blocked": len(blocked),
                "false_block_ratio": _ratio(len(false_block), len(blocked)),
                "mean_cycle_hours": round(sum(hours) / len(hours), 2) if hours else None,
            },
        }
    return out


def verdict(m: Dict[str, dict], treat: str = "C", controls=("T", "B")) -> str:
    if treat not in m:
        return f"chưa có dữ liệu nhánh {treat}"
    t = m[treat]
    lines = []
    oh = t["open_hit"]["count"]
    fp = t["false_pass"]["ratio"]
    lines.append(f"[{treat}] open_hit = {oh} · false_pass = {fp}")
    worse_or_equal = []
    for c in controls:
        if c in m and m[c]["false_pass"]["ratio"] is not None and fp is not None:
            lines.append(f"[{c}] false_pass = {m[c]['false_pass']['ratio']}")
            if fp >= m[c]["false_pass"]["ratio"]:
                worse_or_equal.append(c)
    rs = t["rubber_stamp"]
    if rs["stamped_lt5s_ratio"] is not None and rs["stamped_later_wrong_ratio"] is not None:
        if rs["stamped_lt5s_ratio"] > 0.5 and rs["stamped_later_wrong_ratio"] > 0.2:
            lines.append("CỔNG NGƯỜI ĐÃ CHẾT: >50% duyệt <5s và >20% số đó sai — chuyển giả định sang guard/policy")
    if oh == 0 and worse_or_equal:
        lines.append(f"GIẾT: CHƯA KIỂM không bắt lỗi nào và false_pass không thấp hơn {worse_or_equal} → bỏ Khế")
    elif oh == 0:
        lines.append("CẢNH BÁO: CHƯA KIỂM chưa bắt lỗi nào — giá trị (nếu có) nằm ở false_pass, chưa ở sổ")
    else:
        lines.append("SỐNG: sổ CHƯA KIỂM đã bắt lỗi thật")
    return "\n".join(lines)
