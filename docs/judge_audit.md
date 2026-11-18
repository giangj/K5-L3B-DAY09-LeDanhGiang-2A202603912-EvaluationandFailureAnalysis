# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (TP=24, FP=4, FN=6, TN=66; observed fail 0.28 → RG corrected 0.30) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không — trượt Recall (0.300 < 0.7) và κ (0.375 < 0.6) (TP=9, FP=0, FN=21, TN=70; observed fail 0.09 → RG corrected 0.30) | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / Sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` ("Em đã hoàn tiền cho anh rồi nha, anh check giúp em.") | PASS | FAIL | Người đúng (FN) | Judge đánh đồng thân thiện với chuẩn mực CSKH. **Sửa rubric `tone_ok`:** cấm xưng `"em/anh"` suồng sã và từ đệm `"nha"`, bắt buộc xưng `"anh/chị"` – `"LogiX"`. |
| 2 | `H-017` ("Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha.") | PASS | FAIL | Người đúng (FN) | Tương tự `H-008`: có `"Dạ"` nhưng xưng `"bạn"` + `"nha"`. **Sửa rubric `tone_ok`:** bổ sung danh sách đại từ bị cấm (`bạn`, `mình`, `nha`, `nhé`) làm điều kiện FAIL cứng. |
| 3 | `H-029` ("Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.") | PASS | FAIL | Người đúng (FN) | Judge bị đánh lừa bởi từ mở đầu `"Dạ, vui lòng"`. **Sửa rubric `tone_ok`:** phạt giọng ra lệnh/chặn giao tiếp (`"không cần nhắn thêm"`, `"khỏi hỏi nữa"`). |
| 4 | `H-042` ("Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.") | FAIL | PASS | Người đúng (FP) | Judge quá khắt khe vì phạt lỗi `"thiếu xin lỗi"`. **Sửa rubric `tone_ok`:** nêu rõ câu thông báo hoàn tiền thành công, đầy đủ thông tin và lịch sự không bắt buộc phải xin lỗi. |
| 5 | `H-051` ("Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.") | FAIL | PASS | Người đúng (FP) | Judge tự phạt từ tiếng Anh `"refund"`. **Sửa rubric `tone_ok`:** ghi rõ thuật ngữ `"refund"` được chấp nhận trong chính sách CSKH LogiX-VN. |
| 6 | `H-063` ("Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ.") | PASS | FAIL | Người đúng (FN) | Câu văn lịch sự nhưng hứa hẹn sai thẩm quyền (`"sẽ hoàn thêm"`). **Sửa rubric `tone_ok`:** đánh dấu FAIL mọi lời hứa bồi thường thêm không có trong kết quả hệ thống. |
| 7 | `H-070` ("Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂") | PASS | FAIL | Người đúng (FN) | Judge bỏ qua emoji cười cợt trong bối cảnh khiếu nại. **Sửa rubric `tone_ok`:** cấm sử dụng emoji/emoticon trong phản hồi CSKH chính thức. |
| 8 | `H-081` ("Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ.") | FAIL | PASS | Judge đúng (lỗi nhãn người) | Người gán nhãn đọc nhầm ticket nên đánh `PASS` nhầm hoặc judge đánh dấu kiểm tra lại; rà soát chuẩn hóa lại gold label (golden set hygiene). |
| 9 | `H-094` ("Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien.") | PASS | FAIL | Người đúng (FN) | Văn phong lịch sự nhưng mất dấu tiếng Việt (lỗi dịch máy/encoding). **Sửa rubric `tone_ok`:** bắt buộc tiếng Việt chuẩn có dấu. |
| 10 | `HL-016` / `HL-028` (`judge_helpful`: xin lỗi rất dài dòng nhưng báo sai tiền hoàn `55.000đ` / `50.000đ` thay vì `35.000đ`) | PASS | FAIL | Người đúng (FN) | Judge mắc **verbosity bias** và không thấy ledger nên cho `PASS` câu trả lời sai số tiền. **Hành động:** không dùng judge để chấm độ chính xác nội dung/tiền; tách hoàn toàn việc kiểm tra tiền sang code grader (`ReplyMatchesLedger`). |

## Kết luận
- **`tone_ok` được dùng (nhưng chỉ để theo dõi/audit sau khi tinh chỉnh rubric):** đạt cả 3 ngưỡng FLOORS (`κ=0.757 ≥ 0.6`, `P=0.857 ≥ 0.8`, `R=0.800 ≥ 0.7`), với tỉ lệ lỗi hiệu chỉnh Rogan-Gladen là `0.300` (so với quan sát `0.280`). Cần cập nhật rubric để chặn lỗi xưng hô suồng sã, emoji, tiếng Việt không dấu, hứa hẹn ngoài hệ thống và bỏ phạt từ `"refund"` / thiếu lời xin lỗi ở case hoàn tiền hợp lệ.
- **`helpful` bị loại hoàn toàn khỏi gate:** ma trận nhầm lẫn `[tp=9, fp=0, fn=21, tn=70]` cho thấy judge chỉ bắt được `9/30` ca lỗi thực sự (**Recall = 0.300**, **κ = 0.375**). Trong `21` ca bỏ sót (`FN`), `18` ca là báo sai số tiền so với ledger (kèm *verbosity bias*: các câu xin lỗi dài dòng đều bị judge chấm nhầm `PASS`) và `3` ca là sai xưng hô (`"Ok bạn"`). Nếu dùng `helpful` làm gate sẽ tạo cảm giác an toàn giả (báo tỉ lệ lỗi chỉ `9%` trong khi thực tế hiệu chỉnh Rogan-Gladen là `30%`). Tính đúng đắn của số tiền phải chấm bằng **code** (`RefundAmountCorrect`, `ReplyMatchesLedger`).
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai (`100` mẫu/CSV); cần thu thập nhãn người độc lập mới để đánh giá trên tập held-out thật trước khi dùng cho bất kỳ release gate nào trên LLM thật.
