# QĐ-0003 — Xử lý phản biện Hiến pháp

**Ngày:** 2026-10-08 · **Trạng thái:** bản ghi quyết định; có hiệu lực từ commit merge đầu tiên chứa nó · **Tầng:** T1 · **Người xử lý:** Architect; Owner xem lại khi phê chuẩn

## Bối cảnh
Hiến pháp qua hai vòng phản biện độc lập, mỗi vòng hai Critic, mỗi Critic chỉ đọc các văn bản được gửi. Điều 6 yêu cầu mỗi phát hiện mức cao có xử lý ghi lại. Mức trong bảng là mức Architect đánh giá lại theo tiêu chí: "cao" chỉ khi hai cách đọc hợp lệ dẫn tới hai kết luận khác nhau, hoặc một vai vượt được một kiểm soát. Nhãn A, B (vòng 1) và C, D (vòng 2) do Architect đặt, chưa gắn với mô hình nào.

## Vòng 1 (nháp v0)
| # | Phát hiện | Mức | Xử lý | Sửa ở |
|---|---|---|---|---|
| A1 | Mâu thuẫn giữa 1.0, Điều 0, 3.5, `STATE.md` | cao | nhận một phần; 1.0 chờ Owner | Điều 0, 3.6 |
| A2 | Architect soạn rồi sửa; "phá tầng dưới" chưa định nghĩa | vừa | nhận phần xác nhận bản sửa; vòng 1 ghi đã sửa nhưng Điều 6 chưa có bước đó (lỗi C6) | hoàn tất ở Điều 6, mục 2–3 |
| A3 | `STATE.md` ở T4 nhưng đọc trước T0 | cao | nhận | Điều 7 |
| A4 | "Người rà" không có trong bảng vai | vừa | nhận | PL-A.1 |
| A5 | Architect tự chấm; chồng vai | vừa | nhận phần chồng vai; bác "soạn là chấm" | Điều 2 |
| A6 | Evidence layer do Builder viết | cao | nhận; còn thiếu ở vòng 1 | hoàn tất ở PL-A.4 (C9, D3) |
| A7 | Hai số giết không kiểm được | cao | nhận | Điều 0, PL-A.7 |
| A8 | Điều 7 không vận hành được | cao | nhận; còn thiếu ở vòng 1 | hoàn tất ở PL-A.5 (C1, D1, D5, D9) |
| A9 | Provenance không có cơ chế | vừa | nhận một phần | Điều 3.1, PL-A.3 |
| A10 | "Oracle" chưa định nghĩa | vừa | nhận | PL-A.2 |
| A11 | Thiếu bản thiết kế tổng | cao | nhận; `KIEN_TRUC.md` đăng ký, chưa viết | Điều 1 |
| A12 | Thứ bậc chưa đóng vì 1.0 | cao | giữ; chờ Owner | Điều 1.0 |
| A13 | Thiếu quy trình đề xuất/duyệt T1, T2 | vừa | nhận | Điều 4, 6 |
| A14 | Phục hồi không đảm bảo | cao | trùng A8 | PL-A.5 |
| B1 | Điều 5 đảo Điều 1 | cao | nhận | Điều 5 |
| B2 | Oracle quyền và phạm vi | cao | trùng A10 | Điều 5, PL-A.2 |
| B3 | Luật Nguồn chưa xác định | cao | trùng A12 | Điều 1.0 |
| B4 | Hai thứ tự xây ngược nhau | cao | nhận; còn thiếu SPEC (C11) | Điều 3.6 |
| B5 | Bản thiết kế không có hiện vật thẩm quyền | cao | trùng A11 | Điều 1 |
| B6 | Nháp và hiệu lực không phân biệt được; ai đóng băng giao diện | cao | nhận; còn thiếu ở vòng 1 | hoàn tất ở Điều 4 (C2, D7), Điều 2 (C4) |
| B7 | Claude kiêm Architect và Builder | vừa | nhận; **chấp nhận giữ tổ hợp** Architect kiêm Builder, kèm hai kiểm soát (D10) | Điều 2 |
| B8 | 20/20 test không độc lập | cao | nhận; test do Claude viết, ghi "tự kiểm" | `STATE.md` |
| B9 | Ai kiểm bộ kiểm | cao | trùng A6 | PL-A.4 |
| B10 | Provenance mạnh hơn điều nó chứng minh | vừa | nhận | Điều 3.1, PL-A.2 |
| B11 | Điều 6 cho tầng dưới chặn ngược | vừa | nhận | Điều 6, mục 3 |
| B12 | Điều kiện dừng không kiểm được | cao | trùng A7 | PL-A.7 |
| B13 | Bài kiểm đo nhắc lại tài liệu | cao | nhận; còn thiếu ở vòng 1 | hoàn tất ở PL-A.5 |

## Vòng 2 (v0.1)
| # | Phát hiện | Mức | Xử lý | Sửa ở |
|---|---|---|---|---|
| C1, D1 | PL-A.5.3 và A.5.4 không thể cùng thỏa; `STATE.md` không chứa hash của chính commit nó | cao | nhận | PL-A.5.3–4: commit tham chiếu là tổ tiên, giữa hai commit chỉ `STATE.md` đổi; câu bẫy chạy trên bản sao, không đổi `main` |
| C2, D7 | Không biết văn bản nào đang hiệu lực; Phụ lục A thay tạm nhưng chưa có căn cứ | cao | nhận | Điều 4 (ba trạng thái); Điều 8; QĐ-0004 |
| C3, D2 | QĐ-0001/0002 vừa T0 vừa T1 | cao | nhận | Điều 1 (mọi bản ghi thuộc T1); sửa 0001, 0002 |
| C4 | Không biết ai đóng băng giao diện | vừa | nhận | Điều 2 |
| C5 | Sau khi có Inspector, ai nghiệm thu | vừa | nhận | Điều 2, 8 |
| C6 | Điều 6 đòi Inspector trước khi có; 0003 vòng 1 ghi đã sửa mà chưa sửa | vừa | nhận; đúng là lỗi của bản ghi vòng 1 | Điều 6, 8; bảng vòng 1 ở trên |
| C7 | 3.1 vừa nói suy được vừa nói không | vừa | nhận | Điều 3.1, PL-A.3 |
| C8 | Oracle vượt được: "chỉ nhận đặc tả" chỉ là lời khai, repo công khai | cao | nhận một phần; PL-A.2.2 thu hẹp đường qua repo công khai nhưng git không loại trừ được mã nhận ngoài repo (E1) | PL-A.2.2, A.3 |
| C9, D3 | A.4 chạy một lần; bộ đầu vào sai do người rà chọn | cao | nhận | PL-A.4 |
| C10 | Điều 5 gỡ khóa ngưỡng | cao | nhận | Điều 5; PL-A.7 |
| C11 | `SPEC.md` đứng trước thiết kế, lịch không xử lý | vừa | nhận | Điều 3.6; `STATE.md` |
| C12, D10 | Tổ hợp Architect kiêm Builder vẫn được phép mà bản xử lý không nói | vừa | nhận; ghi chấp nhận có điều kiện | Điều 2 |
| D4 | Phản biện không gắn với phiên bản cuối được phê chuẩn | cao | nhận | Điều 6, mục 2 (băm sha256) |
| D5 | Đầu vào bài kiểm có thể chứa `DAP_AN.md` | cao | nhận | PL-A.5.2; `STATE.md` mục "Cách phục hồi" |
| D6 | Điều 8 bỏ trống nhiệm vụ Inspector | vừa | nhận | Điều 8 |
| D8 | Bộ kiểm luôn FAIL vẫn qua A.4 | vừa | nhận | PL-A.4.2 (thêm bộ đúng) |
| D9 | "Qua bài kiểm" chưa có tiêu chí | vừa | nhận | PL-A.5.5–6 |

**Không đủ thông tin (ghi nhận, không xử lý):** bộ Luật Nguồn chưa được định danh (chờ Điều 1.0); nội dung `SPEC.md` R06/R09 không được cung cấp cho Critic nên không đánh giá được.

**Do Architect bổ sung, không từ Critic:** cổng Owner không được đo (PL-A.6); ngưỡng sửa T0 khác T1–T2, có lý do là T0 hiếm đổi và đắt khi sai (Điều 6).

## Vòng 3a (v0.2, Critic thứ nhất xác nhận)
Kết quả: 15 trên 17 dòng vòng 2 được xác nhận "đã giải quyết"; vòng 1 không dòng nào bị làm hỏng lại. Hai dòng chưa đóng và các lỗi mới:
| # | Phát hiện | Mức | Xử lý | Sửa ở |
|---|---|---|---|---|
| E1 (= C8) | Test author nhận mã chưa commit, viết test, commit trước Builder; thứ tự git không loại trừ | cao (tồn dư) | nhận một phần: không đóng được bằng văn bản; ghi là rủi ro tồn dư, mỗi gói khai ở mục CHƯA KIỂM | PL-A.3 |
| E2 (= C2, D7) | Bản ghi quyết định là T1 nên cũng cần trạng thái, nhưng trạng thái do bản ghi quyết định: tự tham chiếu | cao | nhận | Điều 4: bản ghi là hành vi của Owner, hiệu lực từ commit merge; QĐ-0001/0002/0004 |
| E3 | Test author sửa test rồi tự xác nhận bản sửa trong vai Critic để lấy lại tư cách oracle | cao | nhận | PL-A.2.2: người xác nhận khác Builder và khác tác giả bản sửa |
| E4 | Điều 6.2 cấm điều khoản ngoài phát hiện đã nhận, trong khi 0003 có hai bổ sung của Architect | vừa | nhận | Điều 6, mục 2 |
| E5 | Merge `DAP_AN.md` làm `STATE.md` không còn hợp lệ theo PL-A.5.3 | vừa | nhận | PL-A.5.3 cho phép `phuc_hoi/` đổi |

## Vòng 3b (v0.2, Critic thứ hai xác nhận)
Kết quả: 16 trên 17 dòng vòng 2 được xác nhận "đã giải quyết"; dòng C8 "tạo lỗi mới" trùng E3. Vòng 1 không dòng nào bị làm hỏng lại. Bản này xác nhận trên v0.2 nên một phần đã sửa ở v0.3.
| # | Phát hiện | Mức | Xử lý | Sửa ở |
|---|---|---|---|---|
| F1 | Phụ lục A nằm trong file T0 nhưng nội dung T1: khi `LUAT_TO_CHUC.md` ràng buộc với quy tắc oracle khác, không biết bên nào thắng | cao | nhận | Điều 1, Điều 8, tiêu đề Phụ lục A |
| F2 (= E3, C8) | Test author kiêm Critic tự xác nhận bản sửa | cao | đã sửa ở v0.3; hai Critic độc lập cùng nêu; nâng thành nguyên tắc chung | PL-A.2.2; Điều 3.1 |
| F3 | Điều 4 viện Điều 6 mục 1 trong khi Điều 6 không áp cho lần ÁP DỤNG TẠM đầu | vừa | nhận | Điều 4 |
| F4 | 0003 đòi xác nhận trước ÁP DỤNG TẠM; Điều 4 và QĐ-0004 đặt ở HIỆU LỰC | vừa | đã sửa ở v0.3 | 0003, mục Hệ quả |
| F5 | PL-A.5.4 không buộc dữ kiện đổi nằm trong đầu vào | vừa | nhận | PL-A.5.4 |
| F6 | Người viết bộ A.4 và người rà không bị buộc là hai chủ thể | vừa | nhận | PL-A.4.3 |
| F7 | "Gói" không có biên | vừa | nhận | Điều 2 |
| F8 | "Ghi nhận" không thuộc ba trạng thái Điều 4 | thấp | nhận | Điều 4 (bản ghi không có trạng thái); đầu 0003 |
| F9 | PL-A.6 và lệ hai Critic cho T0 là bổ sung ngoài phát hiện đã nhận | thấp | đã sửa ở v0.3 | Điều 6, mục 2 |
| F10 | Khai nhiều vai chỉ nằm ở `STATE.md` (không có thẩm quyền) | thấp | nhận | Điều 2 |

## Hệ quả
Hiến pháp v0.4 vào `main` qua PR #2 và ÁP DỤNG TẠM theo QĐ-0004. Xác nhận của Critic nêu băm nội dung nên làm một lần, trên văn bản cuối, sau bài kiểm phục hồi và trước khi phê chuẩn HIỆU LỰC. Phê chuẩn HIỆU LỰC dùng bản ghi riêng, ở PR riêng, sau Điều 1.0.
