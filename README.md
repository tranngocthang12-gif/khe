> Mã và tài liệu trong repo này do AI (Claude) tạo theo chỉ đạo, tiêu chí và nghiệm thu của chủ dự án.

# Khế v0.1

Luật chặn trong CI cho mã do AI viết: **mỗi thay đổi đi kèm một khối cam kết; trạng thái tính từ bằng chứng gắn đúng mã; phép kiểm và người rà không được là người viết mã.**

Không phụ thuộc gì ngoài Python 3.10+ và git.

```
khe/            bộ kiểm hợp lệ (parser, evidence, provenance, validator, attest, metrics, cli)
SPEC.md         đặc tả v0.1
schema/         JSON Schema của attestation, acceptance, ledger
templates/      mẫu PR có khối Khế
.github/        bước CI (chưa đưa lên repo này)
examples/       khối mẫu + demo.sh dựng repo thật và chạy đầu-cuối
tests/          20 kiểm thử (dựng repo git thật để kiểm provenance)
```

## Chạy thử trong 2 phút

```bash
python3 -m unittest tests.test_khe -v     # 20 test
bash examples/demo.sh                      # dựng repo demo, attest, validate, in báo cáo
```

## Dùng trong một PR

1. **Phía nhận** viết `KHE.khe` với `GOAL` và các `MUST`/`MUST_NOT` **trước khi** agent bắt đầu. Agent chỉ được thêm.
2. Agent làm việc, khai `ASSUME` — mặc định `[guard]` (máy kiểm lúc chạy). Chỉ giả định ảnh hưởng tính đúng mới `[human]`, tối đa 3.
3. CI chạy từng phép kiểm qua `khe attest` — kết quả do bộ chạy ghi, gắn với HEAD.
4. **Người khác producer** rà sổ CHƯA KIỂM, thêm `OPEN … CONSEQUENCE …` và dòng `REVIEWED_BY`, commit vào `KHE.khe`.
5. `khe validate` chặn merge nếu khối không hợp lệ hoặc bên gửi chưa xong.
6. Bên nhận commit `acceptance.json` khi nghiệm thu.

```bash
khe attest --claim M1 --type property --ref tests/test_open.py --runner github-ci --out attestations -- pytest tests/test_open.py -q
khe validate KHE.khe --root . --base origin/main --producer "$(git log --format=%ae origin/main..HEAD | tail -1)" --attestations attestations
```

Exit 0 = hợp lệ và bên gửi xong. Exit 1 = chặn. Báo cáo in ra là thứ người đọc.

## Thí nghiệm 90 ngày — một đội, một kho mã

Bốn nhánh, chia theo PR:

| Nhánh | Quy trình |
|---|---|
| **A** | AI + CI hiện tại |
| **T** | như A, thêm mẫu PR có các ô Khế nhưng **được để trống** (đối chứng của riêng câu "không rỗng") |
| **B** | tiêu chí nghiệm thu do phía nhận viết + bộ kiểm độc lập, **không** có Khế |
| **C** | như B + khối Khế + `khe validate` chặn merge |

Mỗi PR merge ghi một dòng vào `ledger.jsonl` (schema trong `schema/ledger.schema.json`), điền thêm khi lỗi lộ ra sau merge.

```bash
khe metrics ledger.jsonl --treat C --controls T B
```

### Bốn số sống còn

| # | Số | Đọc thế nào |
|---|---|---|
| 1 | `open_hit` — lỗi sau merge đã nằm sẵn trong sổ CHƯA KIỂM | = 0 nghĩa là sổ không bắt được gì |
| 2 | `false_pass` — lỗi rơi vào cam kết đã `pass` | phải **thấp hơn** T và B; không thì con trỏ là trang trí |
| 3 | `rubber_stamp` — giả định `[human]` duyệt < 5 giây, và tỷ lệ số đó sau sai | cả hai cao → cổng người đã chết → chuyển sang guard/policy |
| 4 | `cost` — tỷ lệ chặn sai, giờ chu trình | giá phải trả |

### Luật giết

`open_hit = 0` **và** `false_pass` không thấp hơn đối chứng → bỏ Khế.

`B ≈ C` → giá trị nằm ở kỷ luật B, không ở ký hiệu. Khi đó Khế chỉ còn sống nếu đội thứ hai tự làm được B nhờ nó mà không có người kèm.

Không công bố chuẩn, không mở rộng sang đầu ra khác, không bàn giao giữa hai agent khác hãng cho đến khi hai số giết đẹp.

## Khế không phải cái gì

Không phải ngôn ngữ để nói. Không phải ngôn ngữ lập trình. Không bảo đảm cam kết đã khai là đủ — việc đó thuộc người viết `MUST`. Không chấm "đúng ý người dùng". Không có token, không có phiếu.

Thứ duy nhất Khế thêm vào những gì đã có (tiêu chí nghiệm thu, test, attestation, vòng đời nhiệm vụ) là làm chúng **bắt buộc, cùng một lúc, dưới một bề mặt bốn câu**, với một luật không ai bắt buộc trước đó: *người làm ra sản phẩm không được là người viết tiêu chí chấm nó, viết phép kiểm cho nó, hay rà sổ rủi ro của nó — và điều đó được suy từ lịch sử, không từ lời khai.*
