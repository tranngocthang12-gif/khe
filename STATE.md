# STATE — trạng thái hiện hành của dự án Khế

Chỉ để định hướng, không có thẩm quyền. Nếu điều gì ở đây trái `main` hoặc Hiến pháp, `STATE.md` sai và phải sửa. Trạng thái của từng văn bản do bản ghi quyết định mới nhất về nó quyết; bảng dưới chỉ liệt kê lại.

**Commit tham chiếu:** `3384ad8` (merge PR #2 vào `main`). **Cập nhật:** 2026-10-10.

## Văn bản có thẩm quyền
| Văn bản | Tầng | Trạng thái |
|---|---|---|
| `HIEN_PHAP.md` v0.4 | T0 | ÁP DỤNG TẠM từ commit `3384ad8` (QĐ-0004); HIỆU LỰC cần Điều 1.0, bài kiểm phục hồi, xác nhận của Critic trên văn bản cuối |
| Phụ lục A (trong `HIEN_PHAP.md`) | T1 tạm | như trên |
| `KIEN_TRUC.md` | T1 | chưa có |
| `LUAT_TO_CHUC.md` | T1 | chưa có |
| `decisions/0001`–`0004` | T1 | bản ghi quyết định: có hiệu lực từ commit `3384ad8` (Điều 4) |
| `decisions/0005` | T1 | bản ghi quyết định: có hiệu lực từ commit merge của PR chứa nó (Điều 4) |
| `SPEC.md` | T2 | v0.1 trên `main`, chưa có bản ghi nào, nên là NHÁP |

## Vai hiện tại
- Owner: Trần Ngọc Thắng (`tranngocthang12-gif`), đứng đầu dự án, trên Hiến pháp (QĐ-0005).
- Architect: Claude. Builder và Test author của mã v0.1: Claude. Vì thế 20/20 test của v0.1 là **tự kiểm của tác giả**, không phải kiểm chứng độc lập; mã và `SPEC.md` v0.1 là baseline chưa kiểm độc lập.
- Critic: bốn bản phản biện nháp Hiến pháp (hai vòng, hai bản mỗi vòng) và hai bản xác nhận vòng 3; trước đó GPT và Grok đã phản biện thiết kế Khế.
- Inspector: chưa phân công. Owner làm cả nhiệm vụ Inspector (Điều 8).

## Đã khóa
- Repo công khai, Apache-2.0; `main` khóa bằng ruleset: chỉ qua PR, chỉ commit ký, chỉ merge commit, không xóa, không force push, không ai được miễn.
- Sự kiện gốc của Điều 3.3 và 3.4: QĐ-0001, QĐ-0002.

## Đang mở
- Điều 1.0: Owner quyết (QĐ-0005): Owner đứng đầu dự án, trên Hiến pháp; Hiến pháp là luật cao nhất trong các văn bản; Luật Nguồn nằm ngoài dự án Khế. Còn lại: sửa chữ Điều 1.0 và thêm Điều 1.1 vào Hiến pháp, cùng văn bản cuối (Điều 6).
- Xác nhận của Critic (Điều 6, mục 2): làm sau bài kiểm phục hồi, trên văn bản cuối, vì xác nhận gắn băm nội dung. Không cần cho ÁP DỤNG TẠM.
- `phuc_hoi/DAP_AN.md`: **Owner viết.**
- QĐ ngưỡng dừng (PL-A.7): chưa có, Owner ký trước thí nghiệm.
- Inspector chưa phân công. `KIEN_TRUC.md`, `LUAT_TO_CHUC.md` chưa viết.
- `.github/` workflow và `evidence/` chưa có; kiểm độc lập mã v0.1 chưa làm.

## Việc kế tiếp
1. PR nhỏ chỉ sửa `STATE.md`: commit tham chiếu = commit merge mới nhất của `main` (PL-A.5.3), làm ngay trước bài kiểm phục hồi.
2. Owner viết `DAP_AN.md`; chạy bài kiểm phục hồi hai lượt (PL-A.5). Nếu phải sửa tài liệu, sửa rồi kiểm lại bằng phiên mới.
3. Sửa Hiến pháp một lần, qua Điều 6 (hai Critic phản biện bản sửa): chữ Điều 1.0 theo QĐ-0005; thêm Điều 1.1 về quyền của Owner theo QĐ-0005; các chỗ bài kiểm chỉ ra. Sau đó kiểm phục hồi lại bằng phiên mới.
4. Văn bản cuối: một Critic xác nhận, nêu băm (Điều 6, mục 2).
5. Phê chuẩn HIỆU LỰC bằng bản ghi riêng, nêu commit và băm.
6. `KIEN_TRUC.md` → `SPEC.md` rà lại → `LUAT_TO_CHUC.md` → mới giao gói.

## Cách phục hồi
Đầu vào cho bài kiểm phục hồi (PL-A.5.2): `STATE.md`, `HIEN_PHAP.md`, `decisions/*.md`. Không gồm `phuc_hoi/DAP_AN.md`.
Phiên làm việc thường: Sync repo → đọc `STATE.md` → đọc `HIEN_PHAP.md` → nêu lại trạng thái và việc đang mở trước khi làm gì.
