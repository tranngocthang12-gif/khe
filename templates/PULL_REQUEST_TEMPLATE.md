<!-- Khối Khế của PR nằm trong file KHE.khe ở gốc repo. Mẫu dưới chỉ để sao chép. -->
<!-- PHÍA NHẬN viết GOAL và MUST/MUST_NOT trước. Agent chỉ được thêm. -->

GOAL:

ASSUME A1 [guard]:                      REF:
ASSUME A2 [policy]:                     POLICY:
# ASSUME [human] chỉ cho giả định ảnh hưởng tính đúng, tối đa 3:
# ASSUME A3 [human]:                    APPROVED: <email khác producer> <ngày>

MUST M1:                                CHECK: property <path>
MUST M2:                                CHECK: diff <path>
MUST_NOT N1:                            CHECK: scan <path>
# Câu không có oracle:
# MUST M3:                              CHECK: judgment

# PHẦN DƯỚI DO NGƯỜI RÀ (khác producer) COMMIT, không phải agent:
# OPEN O1: <điều chưa kiểm>             CONSEQUENCE: <nếu sai thì hỏng cái gì — cụ thể>
# REVIEWED_BY: <email người rà>
