"""Khế v0.1 — parser.

Đọc một khối Khế dạng văn bản (mỗi dòng một câu, từ khóa + thuộc tính)
và trả về cấu trúc Block. Chỉ thư viện chuẩn.

Bốn loại câu + một dòng rà:
    GOAL        | MỤC ĐÍCH
    ASSUME      | GIẢ ĐỊNH     [guard|policy|human]   REF: / POLICY: / APPROVED:
    MUST        | PHẢI                                 CHECK: <type> <ref>
    MUST_NOT    | CẤM                                  CHECK: <type> <ref>
    OPEN        | CHƯA KIỂM                            CONSEQUENCE: <hậu quả>
    REVIEWED_BY | RÀ BỞI       <email người rà>
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

KEYWORDS: Dict[str, tuple] = {
    "GOAL": ("GOAL", "MỤC ĐÍCH", "MUC DICH"),
    "ASSUME": ("ASSUME", "GIẢ ĐỊNH", "GIA DINH"),
    "MUST_NOT": ("MUST_NOT", "MUST NOT", "CẤM", "CAM"),
    "MUST": ("MUST", "PHẢI", "PHAI"),
    "OPEN": ("OPEN", "CHƯA KIỂM", "CHUA KIEM"),
    "REVIEWED_BY": ("REVIEWED_BY", "REVIEWED BY", "RÀ BỞI", "RA BOI"),
}
ATTRS: Dict[str, tuple] = {
    "CHECK": ("CHECK", "KIỂM", "KIEM"),
    "REF": ("REF", "THAM CHIẾU", "THAM CHIEU"),
    "APPROVED": ("APPROVED", "DUYỆT", "DUYET"),
    "CONSEQUENCE": ("CONSEQUENCE", "ĐỔI LẠI", "DOI LAI"),
    "POLICY": ("POLICY", "CHÍNH SÁCH", "CHINH SACH"),
}

# Từ vựng đóng của loại kiểm. "judgment" = câu không có oracle, không bao giờ "pass".
CHECK_TYPES = ("property", "diff", "proof", "scan", "source", "human", "judgment")
ASSUME_MODES = ("guard", "policy", "human")

_ID_PREFIX = {"MUST": "M", "MUST_NOT": "N", "ASSUME": "A", "OPEN": "O"}


def _alt(table: Dict[str, tuple]) -> str:
    names = sorted((a for aliases in table.values() for a in aliases), key=len, reverse=True)
    return "|".join(re.escape(n) for n in names)


def _canon(table: Dict[str, tuple], name: str) -> str:
    up = name.strip().upper()
    for canon, aliases in table.items():
        if up in (a.upper() for a in aliases):
            return canon
    raise KeyError(name)


_KW_RE = re.compile(
    rf"^(?P<kw>{_alt(KEYWORDS)})"
    rf"(?:\s+(?P<id>[A-Za-z][\w-]*))?"
    rf"(?:\s*\[(?P<mode>[^\]]*)\])?"
    rf"\s*:\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
_ATTR_RE = re.compile(rf"\s+(?P<attr>{_alt(ATTRS)})\s*:\s*", re.IGNORECASE)


@dataclass
class Claim:
    id: str
    kind: str                      # MUST | MUST_NOT
    text: str
    check_type: Optional[str] = None
    check_ref: Optional[str] = None
    line: int = 0


@dataclass
class Assumption:
    id: str
    text: str
    mode: Optional[str] = None     # guard | policy | human
    ref: Optional[str] = None
    policy: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    line: int = 0


@dataclass
class OpenItem:
    id: str
    text: str
    consequence: Optional[str] = None
    line: int = 0


@dataclass
class Block:
    goal: Optional[str] = None
    assumptions: List[Assumption] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)
    open_items: List[OpenItem] = field(default_factory=list)
    reviewed_by: Optional[str] = None
    parse_errors: List[str] = field(default_factory=list)
    source_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def _split_attrs(rest: str) -> tuple[str, Dict[str, str]]:
    parts = _ATTR_RE.split(rest)
    text = parts[0].strip()
    attrs: Dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        attrs[_canon(ATTRS, parts[i])] = parts[i + 1].strip()
    return text, attrs


def parse(text: str, source_path: Optional[str] = None) -> Block:
    block = Block(source_path=source_path)
    counters = {k: 0 for k in _ID_PREFIX}

    def next_id(kind: str) -> str:
        counters[kind] += 1
        return f"{_ID_PREFIX[kind]}{counters[kind]}"

    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _KW_RE.match(line)
        if not m:
            block.parse_errors.append(f"dòng {n}: không nhận ra câu — «{line[:60]}»")
            continue
        kw = _canon(KEYWORDS, m.group("kw"))
        sid = m.group("id")
        mode = (m.group("mode") or "").strip().lower() or None
        body, attrs = _split_attrs(m.group("rest"))

        if kw == "GOAL":
            if block.goal is not None:
                block.parse_errors.append(f"dòng {n}: GOAL khai hai lần")
            block.goal = body

        elif kw in ("MUST", "MUST_NOT"):
            c = Claim(id=sid or next_id(kw), kind=kw, text=body, line=n)
            if "CHECK" in attrs:
                toks = attrs["CHECK"].split(None, 1)
                c.check_type = toks[0].lower() if toks else None
                c.check_ref = toks[1].strip() if len(toks) > 1 else None
            block.claims.append(c)

        elif kw == "ASSUME":
            a = Assumption(id=sid or next_id(kw), text=body, mode=mode, line=n)
            a.ref = attrs.get("REF")
            a.policy = attrs.get("POLICY")
            if "APPROVED" in attrs:
                toks = attrs["APPROVED"].split(None, 1)
                a.approved_by = toks[0] if toks else None
                a.approved_at = toks[1].strip() if len(toks) > 1 else None
            block.assumptions.append(a)

        elif kw == "OPEN":
            o = OpenItem(id=sid or next_id(kw), text=body, line=n)
            o.consequence = attrs.get("CONSEQUENCE")
            block.open_items.append(o)

        elif kw == "REVIEWED_BY":
            block.reviewed_by = body.strip() or None

    # trùng id
    seen: set = set()
    for item in [*block.claims, *block.assumptions, *block.open_items]:
        if item.id in seen:
            block.parse_errors.append(f"dòng {item.line}: id «{item.id}» trùng")
        seen.add(item.id)
    return block


def parse_file(path: str) -> Block:
    with open(path, encoding="utf-8") as f:
        return parse(f.read(), source_path=path)
