# Kiểm thử reasoning effort của Credere

## Phạm vi và kết luận

- 60 lượt đầu-cuối: 20 câu x low/medium/auto, chạy cùng provider aigw và cùng dữ liệu.
- 18 request stress context: Sol/Luna x low/medium/high x ba kích thước kho văn bản.
- Tổng 78 lượt thử, 410 HTTP attempt, trong đó 7 attempt timeout không có usage để xác định phí.
- Tổng chi phí ước tính từ usage nhận được: **3,3993361 USD**, khoảng **88.995 đồng** theo tỷ giá cấu hình 26.180 đồng/USD. Không phải hóa đơn gateway; có thể thiếu phí 7 timeout và chưa điều chỉnh cache pricing.
- Không có bằng chứng cần bật high toàn hệ thống. Low có kết quả tốt với các câu nghiệp vụ được thử, nhưng không bảo đảm đúng mọi câu hoặc bám nguồn khi context dài.
- Ưu tiên sửa kiểm chứng nguồn và giữ tính toán bằng code. Không đổi cấu hình runtime trong đợt đo này; runtime vẫn auto như trước.

## 1. Bài đầu-cuối

Dữ liệu học vụ/tuyển sinh là giả lập; tài liệu là kho công khai đã lưu. Chạy app runtime thật, gồm lập kế hoạch, Worker, nghiệm thu, sửa và tổng hợp; không gọi API web/SSE. Hai AI con có client riêng, giữ cùng effort của lượt cha. Chỉ dùng provider đầu tiên đang có cấu hình, tránh đổi nhà cung cấp giữa ba chế độ.

Bộ câu gồm DT-01 đến DT-10, TH-01 đến TH-04 và TS-Q11/Q13/Q18/Q20/Q24/Q28. Trộn thứ tự các mode trong từng câu; chạy tối đa 3 lượt đồng thời. Giữ cap 2.000 completion token như ứng dụng, timeout mỗi HTTP attempt 90 giây và hạn bắt đầu lời gọi mới 600 giây/lượt. Timeout khác mặc định runtime 240 giây, nên số đo phục hồi không hoàn toàn tương đương môi trường phục vụ.

| Effort | Qua kiểm tra / tổng | Trung vị thời gian | HTTP attempt | Lượt sửa nhiệm vụ | Usage-cost USD | Trung bình đồng/câu |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| low | 20/20 | 22,34 giây | 120 | 6 | 0,601095 | 787 |
| medium | 20/20 | 41,39 giây | 134 | 5 | 0,913583 | 1.196 |
| auto | 19/20 | 41,12 giây | 138 | 4 | 0,840828 | 1.101 |

Auto: medium cho plan/review, low cho Worker và synthesis. Chi phí dựa trên bảng giá cấu hình, không phải số tiền đã đối soát thanh toán.

Kiểm tra gồm các số đáp án, mã nguồn, không có dữ liệu cá nhân trong báo cáo, trạng thái nhiệm vụ, lỗi hệ thống và completion bị cắt. Bộ chấm số cũ chỉ kiểm sự hiện diện của số: **đạt không chứng minh số được gắn đúng mọi đại lượng**. Đã đọc tay các báo cáo liên lĩnh vực, tư vấn tổ hợp và trường hợp dẫn nguồn bị trượt; chưa có nghiệm thu độc lập bởi chuyên viên.

### Lỗi và quan sát

1. **TS-Q18 / auto:** tính đúng ưu tiên 0,66 và tổng 24,06 nhưng báo cáo chỉ dẫn [T1], [T2], [T3], không dẫn mã văn bản TS. Trượt tiêu chí nguồn. Đây là lỗ hổng của lớp kiểm báo cáo hiện tại: mã nhiệm vụ được xem là mã dẫn hợp lệ, chưa bắt buộc liên kết tới văn bản gốc.
2. **DT-04 / auto:** chọn top=1000 trong khi catalog chỉ cho 1–40. Validator từ chối, lượt sửa thành công; đã tính cả lời gọi sửa.
3. **Timeout:** medium có 2, auto có 5, low không có trong lần đo này. DT-06/auto chờ hai lần timeout 90 giây ở bước review rồi thành công; TS-Q11/auto mất 352,29 giây. Không thể quy mọi chênh lệch độ trễ cho effort.
4. Câu liên lĩnh vực TH-01 trả đúng thiếu 265 chỉ tiêu Kế toán, đúng tỷ lệ rời trường từng khóa. TH-03 chuyển đúng 185 tân sinh viên đã xác nhận sang AI Đào tạo để tính 3 lớp/học phần; có lưu ý tham số sĩ số 70 là giả lập.
5. Prompt lớn nhất trong bài đầu-cuối: **65.764 ký tự**, không phải toàn bộ kho.

## 2. Stress context dài

Cùng một yêu cầu gồm bốn dữ kiện: học phí Marketing chính quy nhập học 2026, điểm chuẩn Ngôn ngữ Trung Quốc PT100 năm 2026, ưu tiên giảm cho điểm gốc 23,40 KV1, tổng điểm xét tuyển. Đáp án lần lượt 325.000; 23,25; 0,66; 24,06. Có tài liệu năm cũ và phương thức khác làm nhiễu; thứ tự tài liệu được trộn cố định.

| Kho | Số tài liệu | Ký tự văn bản | Ký tự toàn prompt |
| --- | ---: | ---: | ---: |
| Nhỏ | 12 | 59.766 | 63.775 |
| Vừa | 42 | 179.092 | 190.520 |
| Toàn bộ | 70 | 359.693 | 378.519 |

Prompt lớn nhất được gateway báo **94.631 input token**. Cả đợt context nhận tổng 949.248 input token. Đây là số gateway báo, không xác minh được tokenizer/backend thực. Cap completion 4.000 token, khác cap 2.000 của bài đầu-cuối. Mỗi request chỉ gửi một lần, không retry. 18/18 trả HTTP 200, không timeout.

### Kết quả sau đọc lại bằng chứng

| Model | Mode | Đúng cả 4 giá trị | Đạt đủ trích dẫn chặt |
| --- | --- | ---: | ---: |
| Sol | low | 3/3 | 0/3 |
| Sol | medium | 3/3 | 2/3 |
| Sol | high | 3/3 | 2/3 |
| Luna | low | 2/3 | 0/3 |
| Luna | medium | 3/3 | 0/3 |
| Luna | high | 3/3 | 0/3 |

Tiêu chí trích dẫn chặt: đúng source_id, quote là một đoạn nguyên văn có trong nguồn, quote chứa số liệu hoặc công thức liên quan tới trường trả lời. Đây là kiểm tra theo các mốc dữ kiện cố định của bài này, **không phải bộ chứng minh ngữ nghĩa tổng quát**. Kết quả thô của bộ kiểm ban đầu được giữ nguyên; bản chấm lại nằm trong reviewed-summary.json. Không gọi lại model khi chấm lại.

Các trường hợp đã kiểm tay:

- **Luna low / 190.520 ký tự:** trả ưu tiên **0,06** và tổng **23,46** thay vì 0,66 và 24,06, dù trích đúng công thức. Lỗi tính toán thực, không phải lỗi định dạng số.
- **Luna high / toàn bộ kho:** đúng số, nhưng quote ghép dấu ba chấm và thêm phép tính do model viết vào đoạn gắn nhãn nguyên văn. Tăng effort không sửa được yêu cầu trích nguyên văn.
- **Sol low / kho nhỏ:** đúng số, nhưng trích học phí chỉ tới tiêu đề, không chứa 325.000; hai quote công thức không khớp nguyên văn. Sol low/kho vừa, Sol high/kho vừa và Sol medium/toàn bộ kho cũng có quote học phí không chứa số tiền.
- **Sol low / toàn bộ kho:** quote mức KV1 0,75 là nguyên văn, nhưng thiếu quy tắc giảm để hỗ trợ kết quả 0,66. Không tính đạt đầy đủ bằng chứng.

Sol sử dụng 301/1.035/1.308 reasoning token cho low/medium/high trong đợt này. Luna báo 0/0/298 tương ứng. Chỉ là metadata từ gateway; việc không báo reasoning token không chứng minh model không suy luận.

Chi phí stress: Sol 0,995398 USD, Luna 0,0484319 USD.

## 3. Hướng xử lý

1. Không dùng high toàn hệ thống. Low là ứng viên cho truy vấn/soạn báo cáo đơn giản; cân nhắc medium ở lập kế hoạch, so nguồn mâu thuẫn. Cần lặp lại mẫu ghép cặp trước khi thay chính sách mặc định.
2. Không cho model tự tính các giá trị nghiệp vụ: giữ AST/Decimal và SQL. Lỗi Luna ở stress trực tiếp cho thấy vì sao cần lớp này; stress này cố ý không dùng bộ tính của ứng dụng.
3. Bắt buộc nhận định từ tài liệu có mã văn bản gốc và vị trí/đoạn trích. Không chỉ kiểm mã có tồn tại; kiểm đoạn trích thực sự hỗ trợ dữ kiện.
4. Không đẩy toàn bộ kho dài sang Luna chỉ vì API nhận được. Giữ truy xuất giới hạn context, thử Sol cho tác vụ bám nguồn khó sau khi kiểm chứng trên bộ độc lập.
5. Ghi nhận phí từng HTTP attempt, lỗi và thiếu usage; đối soát với gateway. Bài benchmark đã ghi riêng attempt, ứng dụng hiện vẫn chỉ ghi usage của response thành công.

## 4. Tái hiện và hồ sơ

Các lệnh sau gọi API và phát sinh phí, trừ lệnh review:

~~~powershell
cd backend
& "$env:USERPROFILE/.credere/venv/Scripts/python.exe" scripts/bench_effort_e2e.py --parallel 3
& "$env:USERPROFILE/.credere/venv/Scripts/python.exe" scripts/bench_effort_context.py
& "$env:USERPROFILE/.credere/venv/Scripts/python.exe" scripts/bench_effort_context.py --review "$env:USERPROFILE/.credere/runs/effort-context/20261106T183436Z"
~~~

- Đầu-cuối: C:/Users/laqdv/.credere/runs/effort-e2e/20261106T181339Z/
- Context: C:/Users/laqdv/.credere/runs/effort-context/20261106T183436Z/
- Manifest, kết quả từng case, ledger, HTTP attempt, checks và summary nằm trong các thư mục trên. Không có API key trong báo cáo.
- Mỗi case/mode mới có một mẫu; chưa đo độ ổn định qua nhiều lần lặp, chưa so provider khác hoặc xác minh danh tính model phía sau alias. Bộ dữ liệu từng dùng để chỉnh prompt, không phải holdout. Không suy từ 20/20 thành bảo đảm production.

