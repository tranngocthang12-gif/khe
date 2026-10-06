"""Khế v0.1 — attest.

Chạy một lệnh kiểm và phát hành attestation JSON. Kết quả do bộ chạy ghi,
không do agent viết «đạt». Attestation gắn với:
  artifact  = git HEAD lúc chạy
  config    = sha256(loại · ref · lệnh)
  runner    = danh tính bộ chạy (CI job, máy, người)
Exit code lệnh: 0 → pass; khác 0 → fail; hết giờ → inconclusive.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from typing import List, Optional

from .parser import CHECK_TYPES
from .provenance import Git


def attest(
    *,
    claim: str,
    ctype: str,
    ref: str,
    runner: str,
    out_dir: str,
    command: List[str],
    root: str = ".",
    timeout: Optional[int] = 1800,
) -> dict:
    if ctype not in CHECK_TYPES or ctype == "judgment":
        raise SystemExit(f"loại kiểm «{ctype}» không hợp lệ cho attest (từ vựng: {[t for t in CHECK_TYPES if t != 'judgment']})")
    git = Git(root)
    if not git.ok:
        raise SystemExit("attest cần repo git: bằng chứng phải gắn với mã sản phẩm (HEAD)")
    head = git.head()
    config = hashlib.sha256(("\n".join([ctype, ref, " ".join(command)])).encode("utf-8")).hexdigest()[:16]

    log_tail = ""
    try:
        r = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=timeout)
        result = "pass" if r.returncode == 0 else "fail"
        log_tail = (r.stdout + r.stderr)[-2000:]
        rc: Optional[int] = r.returncode
    except subprocess.TimeoutExpired as e:
        result, rc = "inconclusive", None
        log_tail = f"timeout sau {timeout}s"
    except FileNotFoundError as e:
        result, rc = "inconclusive", None
        log_tail = f"không chạy được lệnh: {e}"

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data = {
        "claim": claim, "type": ctype, "ref": ref, "result": result,
        "artifact": head, "runner": runner, "config": config, "timestamp": ts,
        "command": command, "returncode": rc, "log_tail": log_tail,
    }
    os.makedirs(out_dir, exist_ok=True)
    name = f"{claim}-{ts.replace(':', '').replace('+', 'Z')}.json"
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    data["_path"] = path
    return data
