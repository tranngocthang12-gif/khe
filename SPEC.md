# Khế v0.1 — đặc tả

Khế là **một luật chặn trong CI** cho mã do AI viết: mỗi thay đổi đi kèm một khối cam kết; trạng thái của từng cam kết được **tính từ bằng chứng** gắn với đúng mã sản phẩm, không được khai; khối chỉ hợp lệ khi phép kiểm và người rà **không cùng tác giả** với thay đổi, suy từ lịch sử git.

Khế không phải ngôn ngữ để nói, không phải ngôn ngữ lập trình, không áp cho mọi đầu ra của AI. Phạm vi là **câu có oracle**.

## 1. Bốn loại câu

Mã chuẩn là tiếng Anh, cố định. Bí danh tiếng Việt chỉ là bản địa hóa (như Gherkin). Nội dung trong ô viết bằng tiếng của người đọc.

| Mã | Bí danh | Ý nghĩa |
|---|---|---|
| `GOAL` | MỤC ĐÍCH | Ý định, văn tự do. Không kiểm. Giữ nguyên cho người đọc. |
| `ASSUME <id> [mode]` | GIẢ ĐỊNH | Điều AI lấp vào chỗ trống. Phải có chế độ. |
| `MUST <id>` / `MUST_NOT <id>` | PHẢI / CẤM | Cam kết có cực, do **phía nhận** viết trước; agent sản xuất chỉ được thêm. |
| `OPEN <id>` | CHƯA KIỂM | Rủi ro tự khai, buộc kèm hậu quả. Phần máy tính của sổ không cần viết. |
| `REVIEWED_BY` | RÀ BỞI | Email người đã rà sổ CHƯA KIỂM. Phải khác producer và có commit vào file khối. |

Thuộc tính trên cùng dòng:

| Thuộc tính | Bí danh | Dùng cho |
|---|---|---|
| `CHECK: <type> <ref>` | KIỂM | MUST / MUST_NOT |
| `REF: <path[::symbol]>` | THAM CHIẾU | ASSUME [guard] — chỗ kiểm lúc chạy |
| `POLICY: <id>` | CHÍNH SÁCH | ASSUME [policy] — mặc định đã duyệt sẵn |
| `APPROVED: <email> [date]` | DUYỆT | ASSUME [human] |
| `CONSEQUENCE: <text>` | ĐỔI LẠI | OPEN — nếu điều này sai thì hỏng cái gì |

Dòng trống và dòng bắt đầu bằng `#` bị bỏ qua. Dòng không nhận ra là lỗi.

## 2. Từ vựng đóng của loại kiểm

Con trỏ chỉ là tham số của loại. Loại là nghĩa chung giữa hai bên, kể cả hai hãng khác nhau.

| Loại | Oracle | Ví dụ ref |
|---|---|---|
| `property` | test khẳng định một tính chất | `tests/test_open.py` |
| `diff` | so lệch với nguồn sự thật khác | `tests/test_sum.py` |
| `proof` | chứng minh hình thức / kiểm kiểu | `proofs/Export.lean` |
| `scan` | bộ quét quy tắc | `rules/pii.yml` |
| `source` | trích dẫn trỏ được tới nguồn và nguồn chứa điều đã nói | `sources/decree-2026.json` |
| `human` | người làm một phép kiểm **kèm phương pháp** (không phải bấm duyệt) | `reviews/open-on-excel-2016.md` |
| `judgment` | **không có oracle** — không bao giờ `pass`, luôn nằm trong sổ | — |

## 3. Chế độ giả định

| Chế độ | Nghĩa | Yêu cầu |
|---|---|---|
| `guard` | máy kiểm lúc chạy, từ chối khi vi phạm (mặc định nên dùng) | `REF` trỏ tới chỗ kiểm có trong repo |
| `policy` | lựa chọn thường, đã nằm trong chính sách duyệt sẵn | `POLICY` |
| `human` | chỉ cho giả định ảnh hưởng tính đúng | `APPROVED` bởi người khác producer; tối đa 3 mỗi khối |

Giả định `[human]` chưa duyệt không làm khối sai, nhưng **chặn bàn giao**. Không có nút duyệt tất cả, và cũng không ép duyệt: quá ba thì phải chuyển sang `guard`/`policy`.

## 4. Bằng chứng

Attestation là JSON do **bộ chạy** phát hành (`khe attest`), không do agent viết:

```json
{"claim": "M1", "type": "property", "ref": "tests/test_open.py", "result": "pass",
 "artifact": "<git HEAD>", "runner": "github-ci", "config": "<sha256 16 ký tự>",
 "timestamp": "2026-10-06T10:00:00+00:00"}
```

`result` ∈ `pass | fail | inconclusive`. Exit code lệnh 0 → pass, khác 0 → fail, hết giờ → inconclusive.

## 5. Trạng thái — tính, không khai

| Trạng thái | Khi nào | Vào sổ CHƯA KIỂM | Chặn bàn giao |
|---|---|---|---|
| `pass` | kết quả đạt, `artifact == HEAD`, đúng loại | không | không |
| `fail` | kết quả phản bác | có | có |
| `inconclusive` | phép kiểm lỗi / hết giờ — **đếm như fail** | có | có |
| `not_run` | đã khai, chưa có attestation | có | có |
| `stale` | attestation thuộc mã khác | có | có |
| `mismatch` | loại trong attestation ≠ loại đã khai | có (và lỗi R07) | có |
| `judgment` | không có oracle | **luôn** | không |

Sổ CHƯA KIỂM = phần máy tính (mọi cam kết không `pass`) ∪ phần tự khai (`OPEN`). Phần máy tính không xóa được.

## 6. Luật hợp lệ

| Mã | Luật |
|---|---|
| R00 | Khối phải parse được. |
| R01 | `GOAL` bắt buộc. |
| R02 | Ít nhất một `MUST`/`MUST_NOT`. |
| R03 | Mỗi cam kết có `CHECK` với loại trong từ vựng đóng. |
| R04 | Loại khác `judgment` phải có con trỏ. |
| R05 | Con trỏ trỏ tới file có trong repo. |
| R06 | **Độc lập tác giả, suy từ git**: phép kiểm được tạo hoặc sửa trong thay đổi này mà mọi tác giả đều là producer → không hợp lệ. Không có repo git → không hợp lệ (trừ `--draft`, chỉ để soạn nháp). |
| R07 | Attestation phải đúng loại đã khai. |
| R08 | Mỗi `OPEN` phải có `CONSEQUENCE` không rỗng, không trùng mô tả, không thuộc danh sách câu chung chung ("edge cases", "một số trường hợp", "hiệu năng khi tải", "TBD", "v.v."…). |
| R09 | `REVIEWED_BY` bắt buộc, khác producer, và email đó phải có commit vào file khối trong phạm vi thay đổi. |
| R10 | `ASSUME` phải có chế độ; `guard` cần `REF` có trong repo; `policy` cần `POLICY`; `human` không được do producer tự duyệt. |
| R11 | Số `ASSUME [human]` ≤ 3. |
| R12 | Attestation sai định dạng → không hợp lệ. |
| R13 | Mọi cam kết không `pass` tự động vào sổ; không xóa được. |

Tính độc lập không bao giờ là một trường văn bản. `REVIEWED_BY: qa@x.vn` do producer gõ vào không có giá trị; phải có commit của `qa@x.vn` vào file khối.

## 7. Bàn giao — hai trạng thái, hai bên

```
sender_done  = hợp lệ ∧ mọi cam kết có oracle đều pass trên HEAD ∧ không có ASSUME [human] chờ
receiver     = pending | accepted | rejected
```

Bên nhận ghi quyết định vào `acceptance.json` và **tự commit** nó, trong một commit **chỉ chứa file này**:

```json
{"receiver": "ops@x.vn", "decision": "accepted", "artifact": "<HEAD trước commit nghiệm thu>", "reason": "..."}
```

Vì commit nghiệm thu làm HEAD đổi, bộ kiểm chấm trên **cha của commit nghiệm thu** (`evaluated`), không phải HEAD; attestation gắn với `evaluated` vẫn hợp lệ. Acceptance bị coi là `pending` nếu: chưa được commit; commit không phải cuối cùng (có thay đổi sau → nghiệm thu lại); commit chạm file khác; tác giả commit ≠ `receiver`; `receiver` trùng producer; `artifact ≠ evaluated`. Danh tính bên nhận suy từ tác giả commit, không từ chữ trong file. "Bên gửi báo xong" và "bên nhận đã nghiệm thu" không bao giờ gộp làm một.

## 8. Phần người đọc

Người đọc ba thứ: `GOAL`, các `ASSUME [human]` chờ mình, và sổ CHƯA KIỂM — mỗi dòng tự khai kèm hậu quả, cộng tổng số mục máy tính. Mọi thứ khác là của máy. Giao diện được rút gọn bản tóm tắt, không được giấu mục trong sổ.

## 9. Ngoài phạm vi (cố ý)

- Không bảo đảm cam kết đã khai là **đủ**. Khoảng trống này thuộc phía nhận — người viết `MUST`. Khế chỉ bảo đảm mọi cam kết **đã đăng ký** có trạng thái rõ.
- Không chấm "đúng ý người dùng". Câu như vậy là `judgment` và nằm trong sổ mãi.
- Không áp cho văn bản không có oracle. Câu có oracle trong một memo (con số, trích dẫn) vẫn dùng được từng câu; phần phán đoán mang nhãn `judgment`.
- Không có token, không có phiếu, không có chuẩn công bố cho đến khi bốn số sống còn (xem `README.md`) đẹp trên một đội thật.
