"""Khế v0.1 — CLI.

  khe validate KHE.khe --root . --base origin/main --producer dev@x.vn --attestations attestations [--acceptance acceptance.json] [--draft] [--json]
  khe attest   --claim M1 --type property --ref tests/test_open.py --runner github-ci --out attestations [--root .] -- pytest tests/test_open.py -q
  khe metrics  ledger.jsonl [--treat C] [--controls T B]
  khe json     KHE.khe

Exit: 0 = hợp lệ và bên gửi xong · 1 = không hợp lệ hoặc bàn giao bị chặn.
"""
from __future__ import annotations

import argparse
import json
import sys

from .parser import parse_file
from .validator import validate, render
from .attest import attest
from . import metrics as M


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="khe", description="Khế v0.1 — luật chặn trên cam kết có oracle")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="kiểm hợp lệ một khối Khế")
    v.add_argument("file")
    v.add_argument("--root", default=".", help="gốc repo git")
    v.add_argument("--base", help="ref gốc của thay đổi (vd origin/main)")
    v.add_argument("--producer", help="email tác giả thay đổi")
    v.add_argument("--attestations", help="thư mục attestation")
    v.add_argument("--acceptance", help="file acceptance của bên nhận")
    v.add_argument("--max-human", type=int, default=3)
    v.add_argument("--draft", action="store_true", help="chế độ nháp: thiếu provenance chỉ cảnh báo (KHÔNG dùng trong CI)")
    v.add_argument("--json", action="store_true")

    a = sub.add_parser("attest", help="chạy phép kiểm và phát hành attestation")
    a.add_argument("--claim", required=True)
    a.add_argument("--type", required=True, dest="ctype")
    a.add_argument("--ref", required=True)
    a.add_argument("--runner", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--root", default=".")
    a.add_argument("--timeout", type=int, default=1800)
    a.add_argument("command", nargs=argparse.REMAINDER)

    m = sub.add_parser("metrics", help="bốn số sống còn từ ledger.jsonl")
    m.add_argument("ledger")
    m.add_argument("--treat", default="C")
    m.add_argument("--controls", nargs="*", default=["T", "B"])
    m.add_argument("--json", action="store_true")

    j = sub.add_parser("json", help="in khối Khế dạng JSON chuẩn")
    j.add_argument("file")

    args = p.parse_args(argv)

    if args.cmd == "validate":
        block = parse_file(args.file)
        rep = validate(
            block, root=args.root, base=args.base, producer=args.producer,
            attest_dir=args.attestations, acceptance_path=args.acceptance,
            max_human=args.max_human, draft=args.draft,
        )
        if args.json:
            print(json.dumps({"block": block.to_dict(), "report": rep.to_dict()}, ensure_ascii=False, indent=2))
        else:
            print(render(rep, block))
        return 0 if (rep.valid and rep.handoff["sender_done"]) else 1

    if args.cmd == "attest":
        cmd = [c for c in args.command if c != "--"]
        if not cmd:
            p.error("thiếu lệnh kiểm sau «--»")
        data = attest(claim=args.claim, ctype=args.ctype, ref=args.ref, runner=args.runner,
                      out_dir=args.out, command=cmd, root=args.root, timeout=args.timeout)
        print(f"{data['claim']} → {data['result']} · artifact {data['artifact'][:10]} · {data['_path']}")
        return 0

    if args.cmd == "metrics":
        rows = M.load(args.ledger)
        res = M.compute(rows)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            for arm, r in res.items():
                print(f"[{arm}] PR={r['prs']} lỗi={r['bugs_total']} {r['bugs_by_severity']}")
                print(f"     open_hit={r['open_hit']}  false_pass={r['false_pass']}")
                print(f"     rubber_stamp={r['rubber_stamp']}")
                print(f"     cost={r['cost']}")
            print()
            print(M.verdict(res, treat=args.treat, controls=tuple(args.controls)))
        return 0

    if args.cmd == "json":
        print(json.dumps(parse_file(args.file).to_dict(), ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
