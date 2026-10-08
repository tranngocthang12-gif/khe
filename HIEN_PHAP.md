# Hiến pháp dự án Khế — v0.4

Văn bản này không tự khai trạng thái; trạng thái do bản ghi quyết định mới nhất về nó quyết (Điều 4). Xử lý phản biện: `decisions/0003-xu-ly-phan-bien-hien-phap.md`.

## Điều 0 — Công trình
Khế là luật chặn trong CI cho mã do AI viết: mỗi thay đổi kèm khối cam kết; trạng thái cam kết tính từ bằng chứng gắn đúng mã; phép kiểm và người rà không phải người viết mã. Khế không phải ngôn ngữ để nói, không phải ngôn ngữ lập trình. Giá trị của Khế được quyết bằng ngưỡng do Owner đăng ký trước thí nghiệm (PL-A.7); không đạt ngưỡng thì dự án dừng và ghi lý do.

## Điều 1 — Thứ bậc
| Tầng | Nội dung | Nơi ở |
|---|---|---|
| T0 | Hiến pháp | `HIEN_PHAP.md` |
| T1 | Kiến trúc và luật tổ chức; `KIEN_TRUC.md` là bản thiết kế tổng và là thước đo của Inspector | `KIEN_TRUC.md`, `LUAT_TO_CHUC.md`, `decisions/` |
| T2 | Luật sản phẩm | `SPEC.md` |
| T3 | Mã và bộ kiểm | `khe/`, `tests/`, `schema/`, `.github/`, `evidence/` |
| T4 | Bằng chứng và trạng thái | `attestations/`, `ledger.jsonl`, `STATE.md`, `phuc_hoi/` |

Tầng thấp không được trái tầng cao; trái thì tầng thấp sai và phải sửa, không viết thêm luật để hòa giải. Mọi bản ghi quyết định thuộc T1; điều khoản có thẩm quyền T0 nằm trong Hiến pháp, không nằm trong bản ghi. Điều chưa có ở tầng nào là chưa quyết: hỏi Owner. Phụ lục A thuộc T1 dù nằm trong file này (Điều 8).

**Điều 1.0 — [CHỜ OWNER]** Vị trí của bộ Luật Nguồn: trên T0, ngang T0, hay ngoài dự án. Điều này chặn trạng thái HIỆU LỰC của Hiến pháp, không chặn ÁP DỤNG TẠM.

## Điều 2 — Vai
- **Owner**: quyết cuối; viết MUST/MUST_NOT; đóng băng giao diện (bằng bản ghi quyết định); phê chuẩn; nghiệm thu mọi gói; phân công Inspector; đặt luật nhánh; dừng dự án.
- **Architect**: soạn nháp T0–T2; đề xuất chia gói và giao diện. Không đóng băng, không phê chuẩn, không nghiệm thu.
- **Builder**: làm gói được giao.
- **Test author**: viết phép kiểm cho gói theo PL-A.2.
- **Inspector**: được Owner phân công bằng bản ghi quyết định (có thể là một Critic); đối chiếu sản phẩm với `KIEN_TRUC.md`; lập danh sách tầng bị ảnh hưởng (Điều 6).
- **Critic**: tìm lỗi, mâu thuẫn, rủi ro. Không bỏ phiếu.
- **Evidence layer**: bộ chạy và CI phát hành attestation, tính trạng thái, chặn merge.

**Gói** là đơn giao việc có phạm vi (đường dẫn), giao diện và tiêu chí do Owner đóng băng bằng bản ghi quyết định.

Trên cùng một gói, không chủ thể nào giữ hai vai trong {Builder, Test author, Inspector}. Chủ thể là Architect của `KIEN_TRUC.md` không được là Inspector của gói đối chiếu với nó. `KIEN_TRUC.md` phải ràng buộc trước khi gói bắt đầu và không được sửa trong lúc gói chạy, trừ theo Điều 6. Architect kiêm Builder được phép với hai ràng buộc này. Tiêu chí của gói do Owner viết; Architect chỉ đề xuất. Chủ thể giữ nhiều vai ở các gói khác nhau khai trong bản ghi quyết định giao gói; `STATE.md` liệt kê lại.

## Điều 3 — Nguyên tắc nền (chỉ sửa theo Điều 6)
- **3.1** Tách tác giả, phép kiểm và nghiệm thu. Danh tính commit cho biết ai commit; đó là điều kiện cần, chưa đủ cho độc lập nội dung (PL-A.2). Dưới bất kỳ vai nào, không ai rà, xác nhận hoặc chấm hiện vật do chính mình viết hoặc sửa (quyết định của Owner theo Điều 2 không thuộc quy tắc này).
- **3.2** Bằng chứng đứng trên lời khai. Im lặng về chỗ chưa kiểm là lỗi.
- **3.3** AI commit dưới danh tính riêng; không giữ khóa ký hay danh tính của Owner. *(QĐ-0001 ghi lại sự kiện gốc)*
- **3.4** Luật ràng buộc AI do Owner đặt bằng quyền AI không có. *(QĐ-0002 ghi lại sự kiện gốc)*
- **3.5** Gốc tin cậy là Owner, ruleset và nền tảng. Evidence layer không tự kiểm: mỗi phiên bản của nó phải qua PL-A.4 trước khi chặn merge.
- **3.6** Thứ tự: thiết kế → luật → xây → giám sát → kiểm chứng → nghiệm thu → vận hành → thay đổi có kiểm soát. Ngoại lệ khởi động: Hiến pháp (luật nền tối thiểu) được soạn trước thiết kế; mã và `SPEC.md` v0.1 có trước Hiến pháp là baseline chưa kiểm độc lập; `SPEC.md` chỉ được phê chuẩn HIỆU LỰC sau khi `KIEN_TRUC.md` ràng buộc.
- **3.7** Không token, không phiếu, không công bố chuẩn, không mở rộng sang đầu ra khác trước khi đạt ngưỡng đã đăng ký.

## Điều 4 — Nguồn sự thật và hiệu lực
Nguồn sự thật là nhánh `main` của repo `tranngocthang12-gif/khe`. Cuộc trò chuyện, trí nhớ của AI và bản ngoài repo không có hiệu lực.

Văn bản T0–T2, trừ bản ghi quyết định, có ba trạng thái, do bản ghi quyết định mới nhất về nó quyết; không có bản ghi thì là NHÁP. Văn bản không tự khai trạng thái; `STATE.md` chỉ liệt kê lại, không có thẩm quyền.
- **NHÁP**: không ràng buộc.
- **ÁP DỤNG TẠM**: bản ghi do Owner merge tuyên; ràng buộc từ commit merge đầu tiên chứa bản ghi đó, không ràng buộc ngược PR chứa nó; thu hồi được bằng bản ghi. Lần ÁP DỤNG TẠM đầu tiên của một văn bản cần ít nhất một phản biện độc lập đã được xử lý (làm như Điều 6, mục 1; Điều 6 không áp cho lần này).
- **HIỆU LỰC**: bản ghi do Owner merge phê chuẩn ở một commit cụ thể, theo Điều 6.

"Ràng buộc" nghĩa là ÁP DỤNG TẠM hoặc HIỆU LỰC.

Bản ghi quyết định không thuộc ba trạng thái này: nó là hành vi của Owner, có hiệu lực từ commit merge đầu tiên chứa nó; bản ghi chưa được Owner merge không có hiệu lực.

## Điều 5 — Giải mâu thuẫn
Có hai loại, không lẫn:
- **Thẩm quyền** (văn bản nào đúng): tầng cao thắng; cùng tầng thì bản ghi mới hơn thắng, trừ bản ghi mang điều khoản khóa (PL-A.7) chỉ bị thay bằng bản ghi tuyên bắt đầu thí nghiệm mới; còn lại hỏi Owner.
- **Sự thật kỹ thuật** (hệ thống có làm điều X không): oracle theo PL-A.2 quyết. Oracle không quyết thẩm quyền.

Các AI bất đồng không bỏ phiếu: mỗi bên ghi lập luận vào PR, Owner quyết.

## Điều 6 — Sửa đổi
Áp dụng cho mọi thay đổi nội dung văn bản ràng buộc và mỗi lần phê chuẩn HIỆU LỰC. Bằng PR vào `main` kèm bản ghi quyết định:
1. **Phản biện.** Sửa T0 cần ít nhất hai Critic khác Architect; sửa T1–T2 cần ít nhất một. Mỗi phát hiện mức cao có xử lý ghi lại (nhận hoặc bác, kèm lý do).
2. **Xác nhận.** Sau khi sửa, một Critic khác Architect xác nhận bằng văn bản rằng bản sửa khớp các phát hiện đã nhận và các bổ sung của Architect đã ghi ở bản ghi xử lý, và không thêm điều khoản ngoài hai danh sách đó. Xác nhận nêu băm nội dung (sha256) của văn bản; bản ghi phê chuẩn chỉ hợp lệ nếu văn bản tại commit được nêu có đúng băm đó.
3. **Ảnh hưởng.** Inspector (Owner khi chưa có Inspector) lập danh sách văn bản tầng dưới bị ảnh hưởng, nghĩa là có điều khoản mà bản sửa làm đổi nghĩa hoặc làm trái, kèm kế hoạch chuyển tiếp; không có thì ghi "không ảnh hưởng" kèm lý do. Danh sách không có quyền phủ quyết.
4. **Owner merge.** Bản cũ giữ trong lịch sử.

## Điều 7 — Phục hồi
AI hoặc người mới đọc `STATE.md` để định hướng (không có thẩm quyền; trái `main` hoặc Hiến pháp thì `STATE.md` sai), rồi Hiến pháp, rồi việc được giao. Bài kiểm phục hồi theo PL-A.5.

## Điều 8 — Chuyển tiếp
Nghiệm thu mọi gói luôn thuộc Owner. Cho đến khi Owner phân công Inspector, Owner làm cả nhiệm vụ của Inspector. Phụ lục A ràng buộc theo trạng thái do bản ghi quyết định tuyên. Nó thuộc T1 dù nằm trong file này: không được trái thân Hiến pháp, và điều khoản nào `LUAT_TO_CHUC.md` quy định lại thì hết hiệu lực khi `LUAT_TO_CHUC.md` ràng buộc.

---

# Phụ lục A — luật tổ chức tạm (T1 đặt tạm trong file này; xem Điều 8)

**A.1 Người rà của khối Khế** là Inspector, hoặc Critic được Owner phân công cho PR đó. Không phải producer, Builder hay Test author của PR. Email người rà phải có commit vào file khối.

**A.2 Oracle.** Một phép kiểm là oracle khi:
1. danh tính commit của tác giả khác Builder của gói;
2. phép kiểm có trong lịch sử trước commit đầu tiên của Builder trên gói và không bị sửa sau đó (kiểm bằng git); nếu bị sửa, nó mất tư cách oracle cho đến khi một Critic khác Builder và khác tác giả của bản sửa xác nhận bản sửa;
3. giao diện nó dựa vào đã được Owner đóng băng bằng bản ghi quyết định;
4. kết quả do Evidence layer phát hành, gắn commit;
5. đã đăng ký trong khối Khế của PR.

PASS của test do Builder viết không phải oracle.

**A.3 Độc lập nội dung.** Mỗi PR ghi đầu vào mà Test author đã nhận (khai báo, bổ trợ cho A.2.2, không thay thế). Giới hạn đã biết: các mô hình AI chia sẻ nguồn huấn luyện nên độc lập không tuyệt đối; và git không loại trừ được việc Test author nhận mã ngoài repo trước khi commit phép kiểm. Rủi ro tồn dư này không đóng được bằng văn bản; mỗi gói khai nó ở mục CHƯA KIỂM của khối Khế, kèm hậu quả. Công cụ suy provenance hiện tại là `SPEC.md` R06, R09 (T2); hiệu lực của Điều 3.1 không dựa vào nó.

**A.4 Kiểm bộ kiểm.**
1. Mỗi phiên bản của Evidence layer (mọi commit đổi workflow, bộ chạy hoặc `evidence/`) phải qua A.4 trên chính commit đó trước khi được chặn merge; kết quả gắn commit.
2. A.4 chạy hai bộ đầu vào nằm trong `evidence/`: bộ sai (mỗi đầu vào phải ra không-pass) và bộ đúng (mỗi đầu vào phải ra pass). Bộ kiểm luôn từ chối hay luôn chấp nhận đều trượt.
3. Hai bộ do một Critic không phải Builder viết trước; Builder không được sửa; người rà A.4 là chủ thể khác người viết hai bộ.
4. Mọi PR đổi đường dẫn của Evidence layer cần Owner duyệt (CODEOWNERS). Owner bật required check bằng tay.

**A.5 Bài kiểm phục hồi.**
1. Câu hỏi ở `phuc_hoi/CAU_HOI.md`. Câu 1–6 bắt buộc; câu 7–9 tham khảo cho đến khi Owner duyệt bằng bản ghi quyết định. Đáp án do Owner viết ở `phuc_hoi/DAP_AN.md`; Architect không viết.
2. Đầu vào của mô hình kiểm chỉ gồm các file nêu ở mục "Cách phục hồi" của `STATE.md`, không gồm `DAP_AN.md`. Mô hình dùng phiên mới, không Project, không trí nhớ, không web, không repo.
3. `STATE.md` hợp lệ cho lần kiểm khi commit tham chiếu của nó là tổ tiên của HEAD `main` và giữa hai commit chỉ `STATE.md` và các file trong `phuc_hoi/` thay đổi.
4. Hai lượt, hai phiên riêng. Lượt 1 trên bản đúng HEAD: trả lời các câu hỏi. Lượt 2 trên một bản sao đã đổi một dữ kiện (không đổi `main`; Owner chọn dữ kiện nằm trong một file thuộc đầu vào ở mục 2, không báo trước), giữ nguyên `STATE.md`: mô hình phải nêu `STATE.md` lệch ở đúng dữ kiện đó.
5. Qua = đúng toàn bộ câu bắt buộc ở lượt 1 và phát hiện đúng dữ kiện ở lượt 2. Câu tham khảo sai được ghi, không loại. Sai là tài liệu sai: sửa tài liệu rồi kiểm lại bằng phiên mới.
6. Người chấm là Owner hoặc một mô hình thứ ba, không phải mô hình được kiểm, không phải Architect. Mỗi lần kiểm ghi vào `phuc_hoi/ket_qua/<ngày>.md`: commit, mô hình, câu trả lời, kết luận.
7. Hiến pháp chỉ được phê chuẩn HIỆU LỰC sau khi qua bài kiểm.

**A.6 Đo cổng Owner.** `ledger.jsonl` ghi thời gian từ mở PR đến merge và số PR Owner từ chối; báo cùng hai số sống còn.

**A.7 Ngưỡng dừng.** Một bản ghi quyết định riêng, Owner ký, trước khi thí nghiệm bắt đầu: nêu cách tính `open_hit` và `false_pass`, ngưỡng đạt, phạm vi mẫu, người xác nhận. Không đổi sau khi thấy số; đổi ngưỡng là bắt đầu thí nghiệm mới và bỏ số của thí nghiệm cũ. Chưa có bản ghi này thì thí nghiệm chưa được bắt đầu.
