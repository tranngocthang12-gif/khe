# QĐ-0005 — Điều 1.0: Hiến pháp đứng đầu, Luật Nguồn nằm ngoài dự án Khế

**Ngày:** 2026-10-09 · **Trạng thái:** bản ghi quyết định; có hiệu lực từ commit merge đầu tiên chứa nó (Hiến pháp Điều 4) · **Tầng:** T1 · **Người quyết:** Owner (merge là quyết định) · **Người soạn:** Architect

## Bối cảnh
Điều 1.0 của Hiến pháp v0.4 để trống vị trí bộ Luật Nguồn của Owner so với Hiến pháp, và chặn trạng thái HIỆU LỰC. Owner đã quyết: Hiến pháp đứng đầu.

## Quyết định
Trong dự án Khế, Hiến pháp là luật cao nhất. Bộ Luật Nguồn của Owner không đứng trên Hiến pháp, cũng không ngang Hiến pháp: nó nằm ngoài thứ bậc của dự án Khế và không được viện dẫn như nguồn thẩm quyền trong dự án này.

## Hệ quả
- Không có tầng nào đứng trên T0. Điều 1 của Hiến pháp giữ nguyên.
- Điều 1.0 trong Hiến pháp chỉ còn là chữ chờ sửa. Việc sửa chữ Điều 1.0 làm cùng văn bản cuối, theo Điều 6 (hai Critic phản biện bản sửa). Từ lúc Owner đã quyết, Điều 1.0 không còn là câu hỏi mở.
- (Architect đề xuất) Muốn đưa Luật Nguồn hoặc một phần của nó vào dự án sau này, Owner ghi bằng một bản ghi quyết định mới, và phần được đưa vào nằm trong repo `khe` ở tầng không cao hơn T1.
- Đảo ngược được bằng một bản ghi quyết định mới, kèm sửa Hiến pháp.
