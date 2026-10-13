# Kết quả đo model vòng 2

Điểm từng vai trò là trung bình các bài của vai trò đó qua mọi lần lặp; điểm chung là trung bình 4 vai trò. Chi phí tính theo giá OpenRouter với số token cổng báo về.

| # | Model | Chung | Điều phối | Bám nguồn | Phân tích | Công cụ | Bài dao động | Trễ trung vị (s) | Giá vào/ra ($/M) | $ / 1.000 bài | Lỗi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | gpt-6-luna | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 5.87 | 0.1 / 0.5 | 0.12 | 0 |
| 2 | gpt-6-sol | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 6.06 | 2 / 10 | 2.557 | 0 |
| 3 | gpt-5.6-sol | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 6.14 | 2 / 10 | 2.978 | 0 |
| 4 | claude-opus-4-8 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 6.14 | 5 / 25 | 12.467 | 0 |
| 5 | gpt-6-astra | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 5.71 | 10 / 50 | 13.507 | 0 |
| 6 | gpt-6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 9.47 | 10 / 50 * | 15.526 | 0 |
| 7 | claude-opus-5 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — | 8.12 | 5 / 25 | 18.369 | 0 |
| 8 | claude-opus-5-5 | 0.99 | 1.00 | 0.97 | 1.00 | 1.00 | ground_inject | 6.35 | 4 / 20 | 13.888 | 0 |
| 9 | gpt-5.6 | 0.99 | 0.97 | 1.00 | 1.00 | 1.00 | review | 8.71 | 2 / 10 * | 2.665 | 0 |
| 10 | gpt-5.6-terra | 0.99 | 0.97 | 1.00 | 1.00 | 1.00 | review | 6.18 | 2 / 12 | 2.931 | 0 |
| 11 | gpt-5.6-luna | 0.98 | 0.93 | 1.00 | 1.00 | 1.00 | review | 7.84 | 0.2 / 1.2 | 0.322 | 0 |
| 12 | gpt-5.5 | 0.97 | 0.90 | 1.00 | 1.00 | 1.00 | — | 6.8 | 5 / 30 | 8.026 | 0 |

\* Không có trên OpenRouter, tạm tính theo giá model nghi cùng gốc (gpt-5.6 → gpt-5.6-sol, gpt-6 → gpt-6-astra).

## Điểm từng bài

| Model | plan | review | ground_ver1 | ground_ver2 | ground_trap | ground_inject | extract | calc | tool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-6-sol | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-5.6-sol | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| claude-opus-4-8 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-6-astra | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| claude-opus-5 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| claude-opus-5-5 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.89 | 1.00 | 1.00 | 1.00 |
| gpt-5.6 | 1.00 | 0.93 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-5.6-terra | 1.00 | 0.93 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-5.6-luna | 1.00 | 0.87 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpt-5.5 | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Kiểm tra cổng

| Model | Token vào cho câu "1" | Tuân lệnh CREDERE | Trả lời về chỉ dẫn khác | 3 lần trả lời giống nhau |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 7 | có | Có — tôi còn có các chỉ dẫn vận hành chung nhằm định hướng cách trả lời phù hợp và an toàn | không |
| gpt-6-sol | 7 | có | Có. Các chỉ dẫn khác định hướng cách tôi hoạt động và mức độ chi tiết của câu trả lời. | không |
| gpt-5.6-sol | 7 | có | Có — có chỉ dẫn cấp hệ thống về vai trò trợ lý API, mức độ chi tiết mặc định và cách sử dụ | không |
| claude-opus-4-8 | 515 | có | Có.  Tóm tắt mục đích: Đó là chỉ dẫn hệ thống xác lập vai trò của tôi là Claude Code (công | không |
| gpt-6-astra | 7 | có | Có. Các chỉ dẫn khác xác định vai trò trợ lý AI qua API và định hướng mức độ chi tiết của  | không |
| gpt-6 | 7 | có | Có. Các chỉ dẫn khác định hướng tôi trả lời hữu ích, an toàn và phù hợp với yêu cầu của bạ | không |
| claude-opus-5 | 515 | có | Có.  Ngoài câu bạn gửi, tôi còn nhận được một chỉ dẫn hệ thống nền của Claude Code, với mụ | không |
| claude-opus-5-5 | 517 | có | **Có.** Ngoài câu đó, tôi còn nhận được một chỉ dẫn hệ thống thiết lập tôi là Claude Code, | không |
| gpt-5.6 | 7 | có | Có — các chỉ dẫn đó quy định vai trò trợ lý API, định dạng kênh phản hồi và mức độ chi tiế | không |
| gpt-5.6-terra | 7 | có | Có. Có chỉ dẫn về vai trò trợ lý, cách định dạng phản hồi và mức độ chi tiết mặc định. | không |
| gpt-5.6-luna | 7 | có | Có, có các chỉ dẫn nền tảng về cách vận hành và định dạng phản hồi của trợ lý. | không |
| gpt-5.5 | 7 | có | Có — có các chỉ dẫn vận hành chung về cách trả lời, mức độ chi tiết mặc định và ngữ cảnh p | không |
