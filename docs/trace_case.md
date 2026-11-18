# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (1 case từ trial fail trên report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (item `E-002`), run ID `E-seeded_regression-20261118-8b79` |
| Triệu chứng | Grader `TrialPass` (`pass_rate`) và `RefundAmountCorrect` fail: `status=resolved` thay vì `denied`, `ledger refund_vnd=20000` thay vì `0`; step 6 `reply` nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`. |
| Bước sai đầu tiên | Event **3** (`model_override`): `{"delay_days": 5}` — agent lấy số `"trễ 5 ngày"` từ ticket để ghi đè `delay_days=2` của DB. |
| Vì sao là bước *đầu tiên* | Event **1** (`handoff`) chuyển đúng `claim_id=C-002` và `principal_scope=owner_order_only` không lộ secret; event **2** (`investigator`) trả đúng dữ liệu DB `{"order_id": "O-202", "status": "delivered", "delay_days": 2, "shipping_fee_vnd": 20000}` (< 3 ngày, chưa đủ điều kiện hoàn). Mọi bước trước event 3 đều đúng; ngay sau event 3 thì event 4 (`quote`) mới tính sai thành `20.000đ`. |
| Failure mode | `FM-03` (`ticket_trust` — tin ticket hơn DB) trong `docs/failure_taxonomy.md`. |
| Đối chứng | Cùng `C-002@11` trên shape `fixed`: không có event `model_override` sau event **2** (`investigator`); event **3** (`quote`) giữ nguyên `delay_days=2` của DB và trả `{"amount_vnd": 0, "reason": "no_entitlement"}`, event **4** (`reply`) từ chối đúng chính sách (`ledger=0`, `status=denied`). |
| Regression test | `test_trace_case_c002_seed11_db_override_fails_regression_and_passes_fixed` trong [src/tests/test_lab9_regression.py](file:///e:/AI_vin20k/lab-9/src/tests/test_lab9_regression.py) kiểm tra `DbFactKept`, `RefundAmountCorrect` và `TrialPass`: fail trên `seeded_regression` và pass trên `fixed`. |
| Chưa chắc chắn | Trace của `MockLLM` không chứa chuỗi lập luận nội bộ (`chain-of-thought`) giải thích *vì sao* prompt/model tin ticket ở bước 3; với LLM thật cần kiểm thêm biến thể diễn đạt khác của ticket (paraphrase/injection) để chắc chắn lỗi không tái phát. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
