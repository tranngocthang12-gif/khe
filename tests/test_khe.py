"""Kiểm thử Khế v0.1 — dựng repo git thật để kiểm provenance.

Kịch bản gốc:
  commit 0 (oracle@x.vn):   tests/test_open.py, tests/test_sum.py, rules/pii.yml, src/export.py  ← oracle có trước
  commit 1 (dev@x.vn):      sửa src/export.py + thêm KHE.khe                                   ← producer
  commit 2 (qa@x.vn):       thêm dòng OPEN vào KHE.khe                                          ← người rà
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from khe.parser import parse, parse_file  # noqa: E402
from khe.validator import validate  # noqa: E402
from khe.attest import attest  # noqa: E402
from khe import metrics  # noqa: E402

PRODUCER = "dev@x.vn"
REVIEWER = "qa@x.vn"
ORACLE = "oracle@x.vn"

BLOCK = """GOAL: Thêm nút xuất Excel.
ASSUME A1 [guard]: Không quá 50.000 dòng.   REF: src/export.py::check_rows
ASSUME A2 [human]: Khách dùng Excel.         APPROVED: lan@x.vn 2026-10-06
MUST M1: Mở được trên Excel 2016+            CHECK: property tests/test_open.py
MUST M2: Tổng khớp màn hình                  CHECK: diff tests/test_sum.py
MUST_NOT N1: PII trong log                   CHECK: scan rules/pii.yml
MUST M3: Bố cục dễ đọc                       CHECK: judgment
"""
REVIEW_LINE = "OPEN O1: Tiếng Việt trên Excel macOS   CONSEQUENCE: mất dấu ở header\nREVIEWED_BY: qa@x.vn\n"


def git(root, *args, author=None):
    env = dict(os.environ)
    if author:
        env.update(GIT_AUTHOR_NAME=author.split("@")[0], GIT_AUTHOR_EMAIL=author,
                   GIT_COMMITTER_NAME=author.split("@")[0], GIT_COMMITTER_EMAIL=author)
    r = subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Repo:
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="khe-")
        git(self.dir, "init", "-q", "-b", "main")
        git(self.dir, "config", "commit.gpgsign", "false")
        write(self.dir, "tests/test_open.py", "def test_open(): assert True\n")
        write(self.dir, "tests/test_sum.py", "def test_sum(): assert True\n")
        write(self.dir, "rules/pii.yml", "patterns: [email]\n")
        write(self.dir, "src/export.py", "def check_rows(n): return n <= 50000\n")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "oracles", author=ORACLE)
        self.base = git(self.dir, "rev-parse", "HEAD")

    def producer_commit(self, block=BLOCK, extra=None):
        write(self.dir, "src/export.py", "def check_rows(n): return n <= 50000\ndef export(): ...\n")
        write(self.dir, "KHE.khe", block)
        if extra:
            for rel, text in extra.items():
                write(self.dir, rel, text)
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "feature", author=PRODUCER)

    def review_commit(self, line=REVIEW_LINE, author=REVIEWER):
        with open(os.path.join(self.dir, "KHE.khe"), "a", encoding="utf-8") as f:
            f.write(line)
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "review", author=author)

    def head(self):
        return git(self.dir, "rev-parse", "HEAD")

    def attest(self, claim, ctype, ref, result="pass", artifact=None):
        d = os.path.join(self.dir, "attestations")
        os.makedirs(d, exist_ok=True)
        data = {"claim": claim, "type": ctype, "ref": ref, "result": result,
                "artifact": artifact or self.head(), "runner": "test-runner",
                "config": "abc", "timestamp": now()}
        with open(os.path.join(d, f"{claim}-{len(os.listdir(d))}.json"), "w") as f:
            json.dump(data, f)
        return d

    def validate(self, **kw):
        block = parse_file(os.path.join(self.dir, "KHE.khe"))
        return validate(block, root=self.dir, base=self.base, producer=PRODUCER,
                        attest_dir=os.path.join(self.dir, "attestations"), **kw)


def codes(rep):
    return sorted({e.code for e in rep.errors})


class TestParser(unittest.TestCase):
    def test_vietnamese_aliases(self):
        b = parse("MỤC ĐÍCH: x\nPHẢI: y KIỂM: scan r.yml\nCẤM N9: z KIỂM: proof p.lean\nCHƯA KIỂM: q ĐỔI LẠI: hỏng\nRÀ BỞI: a@b")
        self.assertEqual(b.goal, "x")
        self.assertEqual([c.kind for c in b.claims], ["MUST", "MUST_NOT"])
        self.assertEqual(b.claims[0].id, "M1")
        self.assertEqual(b.claims[1].id, "N9")
        self.assertEqual(b.claims[1].check_type, "proof")
        self.assertEqual(b.open_items[0].consequence, "hỏng")
        self.assertEqual(b.reviewed_by, "a@b")

    def test_unknown_line_is_error(self):
        b = parse("GOAL: x\nđây là văn tự do\n")
        self.assertEqual(len(b.parse_errors), 1)


class TestValidator(unittest.TestCase):
    def test_happy_path_valid_but_judgment_in_ledger(self):
        r = Repo(); r.producer_commit(); r.review_commit()
        for c, t, ref in [("M1", "property", "tests/test_open.py"), ("M2", "diff", "tests/test_sum.py"), ("N1", "scan", "rules/pii.yml")]:
            r.attest(c, t, ref)
        rep = r.validate()
        self.assertTrue(rep.valid, [e.message for e in rep.errors])
        self.assertEqual(rep.statuses["M3"]["status"], "judgment")
        ids = {(x["id"], x["source"]) for x in rep.ledger}
        self.assertIn(("M3", "computed"), ids)          # judgment không bao giờ rời sổ
        self.assertIn(("O1", "declared"), ids)
        self.assertTrue(rep.handoff["sender_done"])
        self.assertEqual(rep.handoff["receiver"]["state"], "pending")

    def test_R06_same_author_check_is_invalid(self):
        r = Repo()
        blk = BLOCK.replace("tests/test_open.py", "tests/test_new.py")
        r.producer_commit(block=blk, extra={"tests/test_new.py": "def test_new(): assert True\n"})
        r.review_commit()
        rep = r.validate()
        self.assertFalse(rep.valid)
        self.assertIn("R06", codes(rep))

    def test_R06_producer_editing_existing_oracle_is_invalid(self):
        r = Repo()
        r.producer_commit(extra={"tests/test_open.py": "def test_open(): assert 1 == 1  # nới\n"})
        r.review_commit()
        rep = r.validate()
        self.assertIn("R06", codes(rep))

    def test_R13_not_run_and_stale_go_to_ledger(self):
        r = Repo(); r.producer_commit()
        r.attest("M1", "property", "tests/test_open.py")           # thuộc HEAD cũ
        r.review_commit()                                           # HEAD đổi → stale
        rep = r.validate()
        st = {k: v["status"] for k, v in rep.statuses.items()}
        self.assertEqual(st["M1"], "stale")
        self.assertEqual(st["M2"], "not_run")
        self.assertTrue(rep.valid, [e.message for e in rep.errors])
        self.assertFalse(rep.handoff["sender_done"])                # stale/not_run chặn bàn giao dù khối hợp lệ
        self.assertEqual(rep.handoff["blocking"]["unresolved_claims"], {"M1": "stale", "M2": "not_run", "N1": "not_run"})

    def test_R07_type_mismatch_invalid(self):
        r = Repo(); r.producer_commit(); r.review_commit()
        r.attest("M1", "scan", "tests/test_open.py")               # khai property, chứng scan
        rep = r.validate()
        self.assertIn("R07", codes(rep))
        self.assertEqual(rep.statuses["M1"]["status"], "mismatch")

    def test_fail_blocks_handoff_but_block_valid(self):
        r = Repo(); r.producer_commit(); r.review_commit()
        r.attest("M1", "property", "tests/test_open.py", result="fail")
        rep = r.validate()
        self.assertTrue(rep.valid)
        self.assertFalse(rep.handoff["sender_done"])
        self.assertEqual(rep.handoff["blocking"]["unresolved_claims"]["M1"], "fail")

    def test_R08_filler_consequence_invalid(self):
        r = Repo(); r.producer_commit()
        r.review_commit(line="OPEN O1: hiệu năng khi tải cao   CONSEQUENCE: một số trường hợp biên\nREVIEWED_BY: qa@x.vn\n")
        rep = r.validate()
        self.assertIn("R08", codes(rep))

    def test_R08_missing_consequence_invalid(self):
        r = Repo(); r.producer_commit()
        r.review_commit(line="OPEN O1: Tiếng Việt trên macOS\nREVIEWED_BY: qa@x.vn\n")
        rep = r.validate()
        self.assertIn("R08", codes(rep))

    def test_R09_review_line_written_by_producer_is_invalid(self):
        r = Repo(); r.producer_commit()
        r.review_commit(author=PRODUCER)                            # producer tự viết RÀ BỞI: qa
        rep = r.validate()
        self.assertIn("R09", codes(rep))

    def test_R09_missing_review_invalid(self):
        r = Repo(); r.producer_commit()
        rep = r.validate()
        self.assertIn("R09", codes(rep))

    def test_R10_human_pending_blocks_handoff(self):
        r = Repo()
        r.producer_commit(block=BLOCK.replace("APPROVED: lan@x.vn 2026-10-06", ""))
        r.review_commit()
        rep = r.validate()
        self.assertTrue(rep.valid, [e.message for e in rep.errors])
        self.assertEqual(rep.handoff["blocking"]["pending_human_assumptions"], ["A2"])
        self.assertFalse(rep.handoff["sender_done"])

    def test_R10_producer_self_approval_invalid(self):
        r = Repo()
        r.producer_commit(block=BLOCK.replace("APPROVED: lan@x.vn", f"APPROVED: {PRODUCER}"))
        r.review_commit()
        self.assertIn("R10", codes(r.validate()))

    def test_R11_too_many_human_assumptions(self):
        extra = "".join(f"ASSUME H{i} [human]: g{i}\n" for i in range(4))
        r = Repo(); r.producer_commit(block=BLOCK + extra); r.review_commit()
        self.assertIn("R11", codes(r.validate()))

    def test_receiver_acceptance(self):
        r = Repo(); r.producer_commit(); r.review_commit()
        for c, t, ref in [("M1", "property", "tests/test_open.py"), ("M2", "diff", "tests/test_sum.py"), ("N1", "scan", "rules/pii.yml")]:
            r.attest(c, t, ref)
        evaluated = r.head()
        acc = os.path.join(r.dir, "acceptance.json")

        def put(d, author):
            with open(acc, "w", encoding="utf-8") as f:
                json.dump(d, f)
            git(r.dir, "add", "acceptance.json")
            git(r.dir, "commit", "-q", "-m", "accept", author=author)

        # chưa commit → pending
        with open(acc, "w", encoding="utf-8") as f:
            json.dump({"receiver": "ops@x.vn", "decision": "accepted", "artifact": evaluated}, f)
        self.assertEqual(r.validate(acceptance_path=acc).handoff["receiver"]["state"], "pending")

        # bên nhận commit đúng artifact → accepted, và các pass vẫn giữ (chấm trên cha của commit nghiệm thu)
        put({"receiver": "ops@x.vn", "decision": "accepted", "artifact": evaluated}, "ops@x.vn")
        rep = r.validate(acceptance_path=acc)
        self.assertEqual(rep.handoff["receiver"]["state"], "accepted")
        self.assertEqual(rep.evaluated, evaluated)
        self.assertNotEqual(rep.head, evaluated)
        self.assertTrue(rep.handoff["sender_done"], rep.handoff)

        # file nói receiver=ops nhưng do producer commit → pending
        put({"receiver": "ops@x.vn", "decision": "accepted", "artifact": rep.head}, PRODUCER)
        self.assertIn("không phải", r.validate(acceptance_path=acc).handoff["receiver"]["reason"])

        # sai artifact → pending
        put({"receiver": "ops@x.vn", "decision": "accepted", "artifact": "deadbeef"}, "ops@x.vn")
        self.assertEqual(r.validate(acceptance_path=acc).handoff["receiver"]["state"], "pending")

        # bên nhận = producer → pending
        put({"receiver": PRODUCER, "decision": "accepted", "artifact": r.head()}, PRODUCER)
        self.assertIn("trùng producer", r.validate(acceptance_path=acc).handoff["receiver"]["reason"])

    def test_no_git_is_invalid_unless_draft(self):
        d = tempfile.mkdtemp()
        write(d, "KHE.khe", BLOCK + REVIEW_LINE)
        b = parse_file(os.path.join(d, "KHE.khe"))
        self.assertFalse(validate(b, root=d, producer=PRODUCER).valid)
        rep = validate(b, root=d, producer=PRODUCER, draft=True)
        self.assertEqual(rep.mode, "draft")
        self.assertTrue(any(w.code == "R06" for w in rep.warnings))


class TestAttest(unittest.TestCase):
    def test_attest_binds_head_and_records_result(self):
        r = Repo(); r.producer_commit()
        out = os.path.join(r.dir, "att")
        ok = attest(claim="M1", ctype="property", ref="tests/test_open.py", runner="t", out_dir=out,
                    command=[sys.executable, "-c", "import sys; sys.exit(0)"], root=r.dir)
        bad = attest(claim="M2", ctype="diff", ref="tests/test_sum.py", runner="t", out_dir=out,
                     command=[sys.executable, "-c", "import sys; sys.exit(3)"], root=r.dir)
        self.assertEqual(ok["result"], "pass")
        self.assertEqual(bad["result"], "fail")
        self.assertEqual(ok["artifact"], r.head())
        with self.assertRaises(SystemExit):
            attest(claim="M3", ctype="judgment", ref="", runner="t", out_dir=out, command=["true"], root=r.dir)


class TestMetrics(unittest.TestCase):
    def test_kill_rule(self):
        rows = [
            {"pr": 1, "arm": "C", "claims": [{"id": "M1", "status": "pass"}], "open": [],
             "human_assumptions": [], "bugs": [{"id": "B1", "severity": "high", "linked_claim": "M1"}], "blocked": False},
            {"pr": 2, "arm": "T", "claims": [{"id": "M1", "status": "pass"}], "open": [],
             "human_assumptions": [], "bugs": [], "blocked": False},
        ]
        m = metrics.compute(rows)
        self.assertEqual(m["C"]["false_pass"]["ratio"], 1.0)
        self.assertEqual(m["T"]["false_pass"]["ratio"], 0.0)
        self.assertIn("GIẾT", metrics.verdict(m))

    def test_alive_when_open_catches_bug(self):
        rows = [{"pr": 1, "arm": "C", "claims": [], "open": [{"id": "O1"}],
                 "human_assumptions": [{"id": "A1", "approve_seconds": 2, "later_wrong": True}],
                 "bugs": [{"id": "B1", "severity": "med", "linked_open": "O1"}], "blocked": True, "false_block": False}]
        m = metrics.compute(rows)
        self.assertEqual(m["C"]["open_hit"]["count"], 1)
        v = metrics.verdict(m)
        self.assertIn("SỐNG", v)
        self.assertIn("CỔNG NGƯỜI", v)


if __name__ == "__main__":
    unittest.main(verbosity=2)
