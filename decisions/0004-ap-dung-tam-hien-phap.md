# QĐ-0004 — ÁP DỤNG TẠM Hiến pháp và Phụ lục A

**Ngày:** 2026-10-08 · **Trạng thái:** bản ghi quyết định; có hiệu lực từ commit merge đầu tiên chứa nó (Hiến pháp Điều 4) · **Tầng:** T1 · **Người đề xuất:** Architect · **Người quyết:** Owner (merge là quyết định)

## Bối cảnh
Hiến pháp v0.4 chưa thể HIỆU LỰC: còn Điều 1.0, xác nhận của Critic và bài kiểm phục hồi. Dự án vẫn cần luật ràng buộc ngay từ PR #2 để phân biệt nháp với luật đang áp dụng (Điều 4).

## Quyết định
Từ commit merge của PR chứa bản ghi này, `HIEN_PHAP.md` v0.4 (T0), kể cả Phụ lục A, ở trạng thái **ÁP DỤNG TẠM**. Văn bản này không ràng buộc ngược PR chứa nó. Các bản ghi quyết định 0001–0004 có hiệu lực từ cùng commit merge, theo Điều 4; chúng không có trạng thái riêng. `SPEC.md` giữ trạng thái NHÁP. Thu hồi bằng một bản ghi quyết định khác.

## Điều kiện để HIỆU LỰC
Điều 1.0 được Owner quyết; một Critic khác Architect xác nhận bản sửa khớp phát hiện đã nhận (Điều 6, mục 2); bài kiểm phục hồi qua (PL-A.5); bản ghi phê chuẩn riêng nêu commit và băm nội dung.

## Hệ quả
Từ thời điểm này PL-A.2 và A.4 ràng buộc các gói sau. Mã v0.1 có trước nên không bị truy ngược (Điều 3.6, ngoại lệ khởi động).
