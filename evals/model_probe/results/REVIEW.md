# Soát lại kết quả đo model (vòng 1)

Ngày 26/09/2026. Dữ liệu: `bench.json`, 12 model (9 GPT qua key OpenAI, 3 Claude Opus qua key Claude), mỗi bài chạy 1 lần. Ba agent độc lập đọc toàn bộ câu trả lời gốc; không gọi thêm API.

## Chấm lại

| Model | Điểm tự động | Điểm sau soát | Vì sao đổi |
| --- | --- | --- | --- |
| gpt-5.5, gpt-5.6, gpt-5.6-sol, gpt-6-sol | 1,00 | 1,00 | Đúng |
| gpt-6, gpt-6-luna, gpt-6-astra | 0,97 | 1,00 | Lỗi "không có nhánh song song" do bộ chấm: kế hoạch có 3–5 nhiệm vụ gốc chạy song song nhưng bộ chấm chỉ xét nhiệm vụ không phải gốc |
| gpt-5.6-luna | 1,00 | 1,00, có lỗi ngoài bộ chấm | Lọt một từ tiếng Hindi (“तथा”) vào mục tiêu nhiệm vụ tiếng Việt |
| claude-opus-4-8 | 1,00 | 0,95 | Câu bẫy: tự thêm “bộ phận hỗ trợ kỹ thuật” không có trong nguồn, không ghi chú |
| claude-opus-5-5 | 1,00 | 0,95 | Câu thiếu nguồn: tự nêu “Phòng Kế hoạch – Tài chính” không có trong nguồn |
| claude-opus-5 | 0,95 | 0,85 | Hai câu từ chối đều thêm nơi liên hệ không có nguồn; dài dòng; viết câu tiếng Anh; “3 năm qua” thành 2022–2025 |
| gpt-5.6-terra | 0,87 | 0,90 nhưng loại | Tính đúng từng bước rồi ghi tổng sai: 60.000.000 thay vì 60.500.000 |

Cả 9 model GPT trả lời bám nguồn sạch: từ chối ngắn gọn, không bịa nơi liên hệ. Cả 3 model Claude đều ít nhất một lần thêm nơi liên hệ không có trong nguồn.

## Phù hợp theo vai trò

| Vai trò | Nên dùng | Lý do |
| --- | --- | --- |
| Tác tử điều phối (lập kế hoạch) | claude-opus-5-5; thay thế gpt-6-sol | opus-5-5 có kế hoạch tốt nhất: 3 nhánh gốc, có nhánh tìm đơn giá cho phần chi phí, JSON thuần. gpt-6-sol tách dữ liệu công bố và dữ liệu dùng AI, lưu ý tương quan khác nhân quả |
| Tác tử thực thi bám nguồn | gpt-6-sol, gpt-5.5 | Trích dẫn đúng, câu ngắn (58–180 token), không thêm thông tin ngoài nguồn. gpt-5.5 đúng định dạng trích dẫn nhất |
| Tính toán | claude-opus-4-8; gpt-6 | Trình bày công thức rõ; opus-4-8 nhanh nhất (3,1 giây) |
| Không nên dùng | gpt-5.6-terra (tính sai), claude-opus-5 (dài, thêm thông tin ngoài nguồn), gpt-5.6-luna (lọt chữ Hindi) | |

Bài gọi công cụ không phân biệt được: cả 12 model gọi giống hệt nhau.

## Bất thường của cổng API

- **Kênh Claude bị chèn khối ẩn:** mỗi lời gọi Claude bị tính thêm khoảng 510–530 token đầu vào cố định mà nội dung không có. Kênh GPT không có. Độ tin cậy cao là có khối thêm này; mức vừa rằng đó là chỉ dẫn model thực sự đọc được.
- **Tokenizer Claude tốn gấp đôi với tiếng Việt:** khoảng 1,7 ký tự/token so với 3,0–3,6 của GPT.
- **Claude 5-series tính thêm token đầu ra không trả về:** opus-5 và opus-5-5 tính thêm 15–25% token đầu ra, nhiều khả năng là phần suy luận (thinking) bị bật sẵn.
- **Không kiểm chứng được danh tính model:** tên model trả về luôn trùng tên đã gọi.
- **Nghi cùng một model gốc:** gpt-5.6 và gpt-5.6-sol trả lời giống hệt từng byte ở 2/6 bài; gpt-6 và gpt-6-astra trùng một đoạn kế hoạch 287 ký tự.
- **Hệ quả:**
  - Bảng token trong COST_ESTIMATE.md không dùng nguyên được cho kênh Claude.
  - Chỉ dẫn ẩn có thể bị đổi mà mình không biết, ảnh hưởng tính tái lập khi nghiệm thu.
  - Chỉ gửi dữ liệu công khai, mô phỏng hoặc đã lược bỏ qua cổng này. Nếu định gửi tài liệu nội bộ, phải ghi rõ tên cổng trong phiếu xin phép của DATA_PLAN.md.

## Giới hạn của vòng 1 và việc tiếp theo

- **Giới hạn:** mỗi bài chạy 1 lần, nhiều model cùng đạt điểm tối đa nên chưa tách được. Bộ chấm có 3 lỗi:
  - kiểm tra nhánh song song bỏ qua nhiệm vụ gốc;
  - không bắt nơi liên hệ không có trong nguồn;
  - chấp nhận JSON bọc trong khối markdown.
- **Vòng 2 cần:**
  - bài khó hơn: nhiều tài liệu có phiên bản mâu thuẫn, bẫy thông tin ngoài nguồn, tác tử điều phối đánh giá một kết quả sai (FR4);
  - lặp mỗi bài 3 lần;
  - sửa bộ chấm;
  - ghi thêm `system_fingerprint`, `reasoning_tokens` và header phản hồi.
- **Kiểm tra cổng rẻ (dưới 0,01 USD):**
  1. Gửi một ký tự “1” tới từng model Claude và một model GPT, so số token đầu vào.
  2. Gửi 20 lời gọi rồi đối chiếu số dư tài khoản để biết có đang trả tiền cho khối ẩn không.
  3. Hỏi thử xem có chỉ dẫn nào đứng trước lời nhắc của mình không.
  4. Ghi header và dữ liệu `usage` gốc.
  5. Chạy nhiều lần để kiểm tra các cặp nghi cùng model gốc.
