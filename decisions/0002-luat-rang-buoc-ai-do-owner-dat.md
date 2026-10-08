# QĐ-0002 — Luật ràng buộc AI do người AI không giả danh được đặt

**Ngày:** 2026-10-07 · **Trạng thái:** ghi nhận việc đã làm (ruleset `main`); có hiệu lực từ commit merge đầu tiên chứa bản ghi này (Hiến pháp Điều 4) · **Tầng:** T1 (nội dung có thẩm quyền ở Hiến pháp Điều 3.4)

## Bối cảnh
Owner yêu cầu giao việc tạo ruleset khóa nhánh cho Claude Code. Token của Claude Code không có quyền quản trị repo (đã bị từ chối 403 cả khi mở PR). Nếu AI có quyền đặt luật khóa nhánh thì AI cũng có quyền gỡ nó.

## Quyết định
Mọi luật ràng buộc hành vi của AI trên repo — ruleset, quyền truy cập, required checks, CODEOWNERS — do Owner đặt bằng quyền quản trị mà AI không có và không được cấp. AI chỉ được soạn sẵn nội dung luật (ví dụ file ruleset để nhập); việc áp dụng là của Owner.

## Hệ quả
- Bypass list của ruleset trống, kể cả Owner, để không có đường tắt nào cho bất kỳ ai.
- Khi gói 2 thêm required status check, việc bật check trong ruleset vẫn do Owner làm tay.
- Nếu một ngày AI có quyền admin trên repo này, Hiến pháp bị vi phạm và dự án phải dừng để xét lại.

## Nguồn
Ruleset `main` — Settings → Rules → Rulesets; file nhập `khe-ruleset-main.json`.
