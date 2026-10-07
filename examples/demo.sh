#!/usr/bin/env bash
# Demo đầu-cuối: dựng một repo thật với ba tác giả, attest, validate.
# Chạy từ gốc dự án Khế:  bash examples/demo.sh
set -euo pipefail
KHE_SRC="$(cd "$(dirname "$0")/.." && pwd)"
D="$(mktemp -d /tmp/khe-demo.XXXX)"
cd "$D"
git init -q -b main
git config commit.gpgsign false
c() { # c <email> <message>
  GIT_AUTHOR_NAME="${1%@*}" GIT_AUTHOR_EMAIL="$1" GIT_COMMITTER_NAME="${1%@*}" GIT_COMMITTER_EMAIL="$1" \
    git commit -q -m "$2"
}

# 0) Oracle có trước thay đổi — tác giả: oracle@x.vn
mkdir -p tests rules src
printf 'def check_rows(n): return n <= 50000\n' > src/export.py
printf 'import sys; sys.exit(0)\n' > tests/test_export_open.py
printf 'import sys; sys.exit(0)\n' > tests/test_export_sum.py
printf 'patterns: [email, phone]\n' > rules/pii.yml
printf 'import sys; sys.exit(0)\n' > rules/pii_scan.py
git add -A && c oracle@x.vn "oracles"
BASE="$(git rev-parse HEAD)"

# 1) Producer làm việc, viết khối (không có OPEN/REVIEWED_BY — phần đó không phải của producer)
cp "$KHE_SRC/examples/KHE.khe" KHE.khe
sed -i '/^CHƯA KIỂM/d;/^RÀ BỞI/d' KHE.khe
printf 'def check_rows(n): return n <= 50000\ndef export_excel(rows): ...\n' > src/export.py
git add -A && c dev@x.vn "feature: export excel"

# 2) Người rà (khác producer) thêm sổ CHƯA KIỂM và ký
cat >> KHE.khe <<'B'

CHƯA KIỂM O1: Ký tự tiếng Việt trên Excel macOS   ĐỔI LẠI: mất dấu ở header, kế toán đọc sai tên cột
RÀ BỞI: qa@x.vn
B
git add -A && c qa@x.vn "review: open ledger"

# 3) Bộ chạy attest từng cam kết trên HEAD hiện tại
export PYTHONPATH="$KHE_SRC"
python3 -m khe attest --claim M1 --type property --ref tests/test_export_open.py --runner demo-ci --out attestations -- python3 tests/test_export_open.py
python3 -m khe attest --claim M2 --type diff     --ref tests/test_export_sum.py  --runner demo-ci --out attestations -- python3 tests/test_export_sum.py
python3 -m khe attest --claim N1 --type scan     --ref rules/pii.yml             --runner demo-ci --out attestations -- python3 rules/pii_scan.py

echo; echo "================ VALIDATE (hợp lệ, bên gửi xong, bên nhận chờ) ================"
python3 -m khe validate KHE.khe --root . --base "$BASE" --producer dev@x.vn --attestations attestations || true

# 4) Bên nhận nghiệm thu — commit CHỈ chứa acceptance.json, artifact = HEAD trước đó.
#    Bộ kiểm chấm trên cha của commit nghiệm thu, nên attestation cũ vẫn khớp.
EVAL="$(git rev-parse HEAD)"
python3 - "$EVAL" <<'P'
import json,sys
json.dump({"receiver":"ops@x.vn","decision":"accepted","artifact":sys.argv[1],"reason":"đã mở thử trên Excel 2016 thật"},open("acceptance.json","w"),ensure_ascii=False)
P
git add acceptance.json && c ops@x.vn "accept"
echo; echo "================ VALIDATE (bên nhận đã nghiệm thu) ================"
python3 -m khe validate KHE.khe --root . --base "$BASE" --producer dev@x.vn --attestations attestations --acceptance acceptance.json || true

# 5) Phản ví dụ: producer tự viết test cho cam kết của mình → R06
echo; echo "================ PHẢN VÍ DỤ: producer tự viết phép kiểm → KHÔNG HỢP LỆ ================"
printf 'import sys; sys.exit(0)\n' > tests/test_layout.py
sed -i 's|PHẢI M3: Bố cục dễ đọc với kế toán           KIỂM: judgment|PHẢI M3: Bố cục dễ đọc với kế toán           KIỂM: property tests/test_layout.py|' KHE.khe
git add -A && c dev@x.vn "self-written test"
python3 -m khe validate KHE.khe --root . --base "$BASE" --producer dev@x.vn --attestations attestations || true

echo; echo "repo demo: $D"
