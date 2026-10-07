"""Khế v0.1 — bộ kiểm hợp lệ (tất định, không dùng LLM).

Luật:
  R01 GOAL bắt buộc.
  R02 Ít nhất một MUST/MUST_NOT.
  R03 Mỗi cam kết có CHECK với loại thuộc từ vựng đóng.
  R04 Loại khác judgment phải có con trỏ (ref).
  R05 Con trỏ phải trỏ tới file có trong repo.
  R06 Phép kiểm không cùng tác giả với thay đổi (suy từ git). Cùng tác giả → KHÔNG HỢP LỆ.
  R07 Attestation phải khớp loại đã khai (mismatch → không hợp lệ).
  R08 Mỗi OPEN tự khai phải có CONSEQUENCE cụ thể (không rỗng, không trùng mô tả, không filler).
  R09 REVIEWED_BY bắt buộc, khác producer, và có commit vào file khối (suy từ git).
  R10 ASSUME có chế độ: guard cần REF; policy cần POLICY; human cần APPROVED bởi người khác producer.
  R11 Số ASSUME [human] ≤ giới hạn (mặc định 3) — quá thì phải chuyển sang guard/policy.
  R12 Attestation lỗi định dạng → không hợp lệ.
  R13 Sổ CHƯA KIỂM máy tính: mọi cam kết không pass tự động vào sổ; không được xóa.

Bàn giao:
  sender_done   = hợp lệ ∧ không có fail/inconclusive/mismatch ∧ không có ASSUME [human] chờ
  receiver      = pending | accepted | rejected  (từ file acceptance của bên nhận, khác producer, đúng artifact)
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .parser import Block, CHECK_TYPES, ASSUME_MODES
from .evidence import load_attestations, status_table
from .provenance import Git, ref_path, check_independence, review_evidenced

FILLER = (
    r"\bedge\s*cases?\b", r"trường hợp biên", r"\bmột số\b", r"có thể có lỗi", r"chưa rõ",
    r"\bunknown\b", r"\btbd\b", r"\bn/?a\b", r"\bminor\b", r"\bperformance\b", r"hiệu năng khi tải",
    r"\bcác vấn đề khác\b", r"\bv\.?v\.?\b",
)
_FILLER_RE = re.compile("|".join(FILLER), re.IGNORECASE)


@dataclass
class Finding:
    code: str
    message: str
    line: Optional[int] = None


@dataclass
class Report:
    valid: bool
    errors: List[Finding] = field(default_factory=list)
    warnings: List[Finding] = field(default_factory=list)
    statuses: Dict[str, dict] = field(default_factory=dict)
    ledger: List[dict] = field(default_factory=list)        # sổ CHƯA KIỂM: máy tính + tự khai
    handoff: Dict[str, Any] = field(default_factory=dict)
    head: Optional[str] = None
    evaluated: Optional[str] = None
    mode: str = "strict"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate(
    block: Block,
    *,
    root: Optional[str] = None,
    base: Optional[str] = None,
    producer: Optional[str] = None,
    attest_dir: Optional[str] = None,
    acceptance_path: Optional[str] = None,
    max_human: int = 3,
    draft: bool = False,
) -> Report:
    errors: List[Finding] = []
    warnings: List[Finding] = []
    E = lambda code, msg, line=None: errors.append(Finding(code, msg, line))      # noqa: E731
    W = lambda code, msg, line=None: warnings.append(Finding(code, msg, line))    # noqa: E731

    for pe in block.parse_errors:
        E("R00", pe)

    # --- provenance ---------------------------------------------------------
    git: Optional[Git] = None
    head: Optional[str] = None
    evaluated: Optional[str] = None      # mã sản phẩm được chấm (HEAD, hoặc cha của commit nghiệm thu)
    acc_commit: Optional[str] = None
    acc_rel: Optional[str] = None
    if root:
        g = Git(root)
        if g.ok:
            git = g
            head = g.head()
            evaluated = head
            if acceptance_path and os.path.exists(acceptance_path):
                acc_rel = os.path.relpath(os.path.abspath(acceptance_path), os.path.abspath(root))
                if git.tracked(acc_rel):
                    acc_commit = git.last_commit_for(acc_rel)
                    # Commit nghiệm thu phải là commit cuối và chỉ chạm file acceptance:
                    # khi đó thứ được chấm là cha của nó, không phải chính nó.
                    if acc_commit == head and git.files_in_commit(head) == {acc_rel}:
                        evaluated = git.parent(head) or head
    if git is None:
        msg = "không có repo git để suy provenance (độc lập tác giả, mã sản phẩm)"
        (W if draft else E)("R06", msg)
    if not producer:
        (W if draft else E)("R06", "thiếu --producer (email tác giả thay đổi)")

    # --- R01, R02 ---------------------------------------------------------
    if not block.goal:
        E("R01", "thiếu GOAL / MỤC ĐÍCH")
    if not block.claims:
        E("R02", "không có cam kết nào (MUST/MUST_NOT)")

    # --- R03–R06 per claim ------------------------------------------------
    for c in block.claims:
        if not c.check_type:
            E("R03", f"{c.id}: thiếu CHECK", c.line)
            continue
        if c.check_type not in CHECK_TYPES:
            E("R03", f"{c.id}: loại kiểm «{c.check_type}» ngoài từ vựng {list(CHECK_TYPES)}", c.line)
            continue
        if c.check_type == "judgment":
            continue
        if not c.check_ref:
            E("R04", f"{c.id}: loại «{c.check_type}» cần con trỏ (ref)", c.line)
            continue
        if git and producer:
            path = ref_path(c.check_ref)
            if not git.tracked(path):
                E("R05", f"{c.id}: con trỏ «{path}» không có trong repo", c.line)
                continue
            ind = check_independence(git, c.check_ref, producer, base)
            if ind == "same_author":
                E("R06", f"{c.id}: phép kiểm «{path}» do chính producer tạo/sửa trong thay đổi này — không độc lập", c.line)
        elif root and not git:
            pass  # đã báo ở trên

    # --- evidence / statuses (R07, R12, R13) --------------------------------
    atts, problems = load_attestations(attest_dir)
    for p in problems:
        E("R12", p)
    statuses = status_table(block, atts, evaluated)
    for cid, st in statuses.items():
        if st["status"] == "mismatch":
            E("R07", f"{cid}: attestation ghi loại «{st['evidence'] and _att_type(atts, cid)}» ≠ loại đã khai «{st['check_type']}»")

    ledger: List[dict] = []
    for cid, st in statuses.items():
        if st["status"] != "pass":
            ledger.append({
                "id": cid, "source": "computed", "status": st["status"],
                "text": st["text"], "consequence": None,
            })

    # --- R08 declared OPEN ---------------------------------------------------
    for o in block.open_items:
        cons = (o.consequence or "").strip()
        if not cons:
            E("R08", f"{o.id}: thiếu CONSEQUENCE / ĐỔI LẠI", o.line)
        elif cons.lower() == o.text.strip().lower():
            E("R08", f"{o.id}: hậu quả trùng với mô tả — chưa nói hỏng cái gì", o.line)
        elif _FILLER_RE.search(cons) or _FILLER_RE.search(o.text):
            E("R08", f"{o.id}: câu chung chung («{(cons or o.text)[:40]}») — nêu hậu quả cụ thể", o.line)
        ledger.append({
            "id": o.id, "source": "declared", "status": "declared",
            "text": o.text, "consequence": o.consequence,
        })

    # --- R09 review -----------------------------------------------------------
    if not block.reviewed_by:
        E("R09", "thiếu REVIEWED_BY / RÀ BỞI — khối chỉ hợp lệ sau khi tác giả khác đã rà sổ CHƯA KIỂM")
    elif producer and block.reviewed_by.lower() == producer.lower():
        E("R09", f"REVIEWED_BY «{block.reviewed_by}» trùng producer")
    elif git and producer and block.source_path:
        rel = os.path.relpath(os.path.abspath(block.source_path), os.path.abspath(root))
        if not review_evidenced(git, rel, block.reviewed_by, producer, base):
            (W if draft else E)("R09", f"REVIEWED_BY «{block.reviewed_by}» không có commit nào vào «{rel}» — rà không có bằng chứng")

    # --- R10, R11 assumptions -------------------------------------------------
    human_pending: List[str] = []
    n_human = 0
    for a in block.assumptions:
        if a.mode not in ASSUME_MODES:
            E("R10", f"{a.id}: thiếu chế độ [guard|policy|human]", a.line)
            continue
        if a.mode == "guard" and not a.ref:
            E("R10", f"{a.id}: [guard] cần REF trỏ tới chỗ kiểm lúc chạy", a.line)
        if a.mode == "guard" and a.ref and git and not git.tracked(ref_path(a.ref)):
            E("R10", f"{a.id}: REF «{ref_path(a.ref)}» không có trong repo", a.line)
        if a.mode == "policy" and not a.policy:
            E("R10", f"{a.id}: [policy] cần POLICY <mã chính sách đã duyệt>", a.line)
        if a.mode == "human":
            n_human += 1
            if not a.approved_by:
                human_pending.append(a.id)
            elif producer and a.approved_by.lower() == producer.lower():
                E("R10", f"{a.id}: producer tự duyệt giả định của mình", a.line)
    if n_human > max_human:
        E("R11", f"{n_human} giả định [human] > giới hạn {max_human} — chuyển bớt sang [guard]/[policy]")

    # --- handoff ----------------------------------------------------------------
    valid = not errors
    # "Xong" = mọi cam kết có oracle đều pass trên đúng HEAD này. not_run/stale/fail/inconclusive đều chặn.
    unresolved = {cid: st["status"] for cid, st in statuses.items() if st["status"] not in ("pass", "judgment")}
    sender_done = valid and not unresolved and not human_pending
    receiver = _receiver_state(acceptance_path, producer, evaluated, git, acc_commit, acc_rel, head)
    handoff = {
        "sender_done": sender_done,
        "blocking": {"errors": len(errors), "unresolved_claims": unresolved, "pending_human_assumptions": human_pending},
        "receiver": receiver,
    }

    return Report(
        valid=valid, errors=errors, warnings=warnings, statuses=statuses,
        ledger=ledger, handoff=handoff, head=head, evaluated=evaluated, mode="draft" if draft else "strict",
    )


def _att_type(atts: List[dict], cid: str) -> Optional[str]:
    xs = [a for a in atts if a.get("claim") == cid]
    return max(xs, key=lambda a: a["timestamp"])["type"] if xs else None


def _receiver_state(path: Optional[str], producer: Optional[str], evaluated: Optional[str],
                    git: Optional[Git], acc_commit: Optional[str], acc_rel: Optional[str], head: Optional[str]) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {"state": "pending", "reason": "chưa có file acceptance của bên nhận"}
    try:
        with open(path, encoding="utf-8") as f:
            acc = json.load(f)
    except Exception as e:  # noqa: BLE001
        return {"state": "pending", "reason": f"acceptance không đọc được: {e}"}
    for k in ("receiver", "decision", "artifact"):
        if k not in acc:
            return {"state": "pending", "reason": f"acceptance thiếu trường «{k}»"}
    if acc["decision"] not in ("accepted", "rejected"):
        return {"state": "pending", "reason": "decision phải là accepted|rejected"}
    receiver = str(acc["receiver"]).lower()
    if producer and receiver == producer.lower():
        return {"state": "pending", "reason": "bên nhận trùng producer — không phải nghiệm thu"}
    if git is None:
        return {"state": "pending", "reason": "không có git để suy bên nhận"}
    if acc_commit is None:
        return {"state": "pending", "reason": "acceptance chưa được bên nhận commit — không suy được danh tính"}
    if acc_commit != head:
        return {"state": "pending", "reason": f"có thay đổi sau commit nghiệm thu {acc_commit[:10]} — nghiệm thu lại"}
    if git.files_in_commit(head) != {acc_rel}:
        return {"state": "pending", "reason": "commit nghiệm thu chạm cả file khác — phải chỉ chứa acceptance"}
    if git.author_of(head) != receiver:
        return {"state": "pending", "reason": f"commit nghiệm thu do «{git.author_of(head)}» tạo, không phải «{receiver}»"}
    if evaluated and acc["artifact"] != evaluated:
        return {"state": "pending", "reason": f"acceptance thuộc artifact {acc['artifact'][:10]} ≠ mã được chấm {evaluated[:10]}"}
    return {"state": acc["decision"], "receiver": receiver, "artifact": evaluated, "reason": acc.get("reason")}


def render(report: Report, block: Block) -> str:
    out: List[str] = []
    tag = "HỢP LỆ" if report.valid else "KHÔNG HỢP LỆ"
    art = ""
    if report.evaluated:
        art = f" · chấm trên {report.evaluated[:10]}" + (f" (HEAD {report.head[:10]} = commit nghiệm thu)" if report.head != report.evaluated else "")
    out.append(f"KHẾ v0.1 — {tag} ({report.mode}){art}")
    if block.goal:
        out.append(f"MỤC ĐÍCH: {block.goal}")
    out.append("")
    out.append("CAM KẾT:")
    for cid, st in report.statuses.items():
        mark = {"pass": "✓", "fail": "✗", "inconclusive": "?", "not_run": "·", "stale": "↺", "mismatch": "≠", "judgment": "~"}[st["status"]]
        kind = "CẤM " if st["kind"] == "MUST_NOT" else "PHẢI"
        out.append(f"  {mark} {cid:<4}{kind} {st['text']}  [{st['check_type']} · {st['check_ref'] or '—'}] → {st['status']}")
    out.append("")
    out.append(f"CHƯA KIỂM ({len(report.ledger)} mục):")
    for item in report.ledger:
        if item["source"] == "computed":
            out.append(f"  · {item['id']} ({item['status']}): {item['text']}")
        else:
            out.append(f"  · {item['id']} (tự khai): {item['text']}  ĐỔI LẠI: {item['consequence']}")
    if not report.ledger:
        out.append("  (trống — mọi cam kết đã pass trên mã hiện tại)")
    pend = report.handoff["blocking"]["pending_human_assumptions"]
    if pend:
        out.append(f"GIẢ ĐỊNH CHỜ NGƯỜI: {', '.join(pend)}")
    if report.errors:
        out.append("")
        out.append("LỖI:")
        for e in report.errors:
            where = f" (dòng {e.line})" if e.line else ""
            out.append(f"  {e.code}{where}: {e.message}")
    if report.warnings:
        out.append("")
        out.append("CẢNH BÁO:")
        for w in report.warnings:
            where = f" (dòng {w.line})" if w.line else ""
            out.append(f"  {w.code}{where}: {w.message}")
    out.append("")
    h = report.handoff
    out.append(f"BÀN GIAO: bên gửi {'xong' if h['sender_done'] else 'CHƯA xong'} · bên nhận {h['receiver']['state']}"
               + (f" — {h['receiver']['reason']}" if h['receiver'].get('reason') else ""))
    return "\n".join(out)
