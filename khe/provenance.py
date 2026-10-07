"""Khế v0.1 — provenance.

Độc lập tác giả được SUY từ lịch sử git, không được khai bằng chữ.
Nếu không có repo git thì không suy được → khối không hợp lệ (trừ chế độ nháp).
"""
from __future__ import annotations

import subprocess
from typing import List, Optional, Set


class Git:
    def __init__(self, root: str):
        self.root = root
        self.ok = self._probe()

    def _run(self, *args: str) -> str:
        r = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} thất bại")
        return r.stdout

    def _probe(self) -> bool:
        try:
            return self._run("rev-parse", "--is-inside-work-tree").strip() == "true"
        except Exception:  # noqa: BLE001
            return False

    def head(self) -> str:
        return self._run("rev-parse", "HEAD").strip()

    def tracked(self, path: str) -> bool:
        try:
            self._run("ls-files", "--error-unmatch", path)
            return True
        except Exception:  # noqa: BLE001
            return False

    def changed_files(self, base: str) -> Set[str]:
        out = self._run("diff", "--name-only", f"{base}...HEAD")
        return {l.strip() for l in out.splitlines() if l.strip()}

    def last_commit_for(self, path: str) -> Optional[str]:
        out = self._run("log", "-1", "--format=%H", "--", path).strip()
        return out or None

    def parent(self, sha: str) -> Optional[str]:
        try:
            return self._run("rev-parse", f"{sha}^").strip()
        except Exception:  # noqa: BLE001
            return None

    def files_in_commit(self, sha: str) -> Set[str]:
        out = self._run("show", "--name-only", "--format=", sha)
        return {l.strip() for l in out.splitlines() if l.strip()}

    def author_of(self, sha: str) -> str:
        return self._run("log", "-1", "--format=%ae", sha).strip().lower()

    def authors(self, path: str, base: Optional[str] = None) -> List[str]:
        rng = [f"{base}..HEAD"] if base else []
        out = self._run("log", "--format=%ae", *rng, "--", path)
        return [l.strip().lower() for l in out.splitlines() if l.strip()]


def ref_path(ref: str) -> str:
    """'tests/x.py::test_a' -> 'tests/x.py'."""
    return ref.split("::", 1)[0].strip()


def check_independence(git: Git, ref: str, producer: str, base: Optional[str]) -> str:
    """Trả về: independent | same_author | missing.

    Quy tắc: oracle có trước thay đổi này (không nằm trong diff) là độc lập.
    Oracle được tạo/sửa trong diff này mà mọi tác giả đều là producer → same_author.
    """
    path = ref_path(ref)
    if not git.tracked(path):
        return "missing"
    producer = producer.lower()
    if base:
        if path not in git.changed_files(base):
            return "independent"
        authors = set(git.authors(path, base))
    else:
        authors = set(git.authors(path))
    if authors and authors <= {producer}:
        return "same_author"
    return "independent"


def review_evidenced(git: Git, block_path: str, reviewer: str, producer: str, base: Optional[str]) -> bool:
    """Người rà phải thực sự đã commit vào file khối (trong phạm vi thay đổi nếu có base)."""
    reviewer = reviewer.lower()
    if reviewer == producer.lower():
        return False
    if not git.tracked(block_path):
        return False
    authors = set(git.authors(block_path, base))
    return reviewer in authors
