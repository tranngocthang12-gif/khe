# QĐ-0001 — AI không giữ khóa ký và không mượn danh tính Owner

**Ngày:** 2026-10-07 · **Trạng thái:** ghi nhận việc đã làm (PR #1); có hiệu lực từ commit merge đầu tiên chứa bản ghi này (Hiến pháp Điều 4) · **Tầng:** T1 (nội dung có thẩm quyền ở Hiến pháp Điều 3.3)

## Bối cảnh
Khi đưa gói v0.1 lên repo, Claude Code dừng ở bước ký commit: để commit hiện "Verified" dưới tên Owner, nó phải tạo khóa trong container tạm, đưa khóa lên tài khoản GitHub của Owner, và đổi `user.email` thành email của Owner. Cả ba việc đều khiến đầu ra của AI hiện ra như của người.

## Quyết định
AI commit dưới danh tính riêng của nó (ví dụ `claude`, có chữ ký của nền tảng). AI không bao giờ giữ khóa ký của Owner, không đặt tên/email của Owner vào cấu hình git, không được thêm khóa vào tài khoản của Owner. Thay đổi vào `main` do Owner merge; commit merge mang chữ ký của nền tảng dưới tên Owner.

## Hệ quả
- PR #1 merge bằng merge commit (không squash) để giữ nguyên hai commit AI đã ký trong lịch sử `main`.
- Ruleset `main` chỉ cho phép merge commit.
- Mọi agent AI tham gia sau này phải có danh tính riêng trên GitHub trước khi được giao gói.

## Nguồn
PR #1 — `https://github.com/tranngocthang12-gif/khe/pull/1`
