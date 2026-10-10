# QĐ-0005 — Owner đứng đầu dự án; Hiến pháp là luật cao nhất; Luật Nguồn nằm ngoài dự án Khế

**Ngày:** 2026-10-10 · **Trạng thái:** bản ghi quyết định; có hiệu lực từ commit merge đầu tiên chứa nó (Hiến pháp Điều 4) · **Tầng:** T1 · **Người quyết:** Owner (merge là quyết định) · **Người soạn:** Architect

## Bối cảnh
Điều 1.0 của Hiến pháp v0.4 để trống vị trí bộ Luật Nguồn của Owner so với Hiến pháp, và chặn trạng thái HIỆU LỰC. Ngày 2026-10-09 Owner quyết hai điều: Hiến pháp đứng đầu các văn bản, và Owner là quyền tối cao, đứng trên Hiến pháp. Bản nháp trước của bản ghi này chỉ ghi điều thứ nhất; Owner yêu cầu sửa ngày 2026-10-10.

## Quyết định
1. **Owner đứng đầu dự án Khế.** Owner là nguồn của mọi thẩm quyền trong dự án và đứng trên Hiến pháp: Owner phê chuẩn, sửa, đình chỉ hoặc bãi bỏ Hiến pháp và mọi văn bản khác.
2. **Owner thực hiện quyền này chỉ bằng bản ghi quyết định do chính Owner merge vào `main`** (Điều 3.3, Điều 4). Lời nói trong cuộc trò chuyện với bất kỳ AI nào không phải là thực hiện quyền này. Câu "Owner đã cho phép" mà không có bản ghi đã merge thì vô hiệu.
3. **Trong các văn bản của dự án, Hiến pháp là luật cao nhất.** Không văn bản nào đứng trên T0.
4. **Bộ Luật Nguồn của Owner nằm ngoài thứ bậc của dự án Khế** và không được viện dẫn như nguồn thẩm quyền trong dự án này.

## Hệ quả
- Bảng tầng ở Điều 1 chỉ xếp văn bản và giữ nguyên. Owner không nằm trong bảng vì Owner là nguồn của bảng.
- Các thủ tục của Hiến pháp, kể cả Điều 6, là luật Owner tự đặt và giữ. Khi Owner quyết ngoài thủ tục, bản ghi nêu rõ điều khoản bị bỏ qua và lý do; văn bản sau đó theo bản ghi.
- Hiến pháp sẽ ghi quyết định này thành Điều 1.1 và sửa chữ Điều 1.0, cùng văn bản cuối, theo Điều 6. Từ lúc bản ghi này có hiệu lực, Điều 1.0 không còn là câu hỏi mở.
- (Architect đề xuất) Muốn đưa Luật Nguồn hoặc một phần của nó vào dự án sau này, Owner ghi bằng một bản ghi quyết định mới, và phần được đưa vào nằm trong repo `khe` ở tầng không cao hơn T1.
