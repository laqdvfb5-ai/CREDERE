# Dự toán chi phí thực hiện đề tài Credere

Cập nhật: 26/09/2026, theo kết quả đo model vòng 2 ([REVIEW_v2.md](./evals/model_probe/results_v2/REVIEW_v2.md)) và giá OpenRouter. Đây là chi phí thực tế nhóm phải chi để làm đề tài 3 tháng (10–12/2026), không phụ thuộc định mức hay mức hỗ trợ của trường. Không tính công lao động của nhóm, điện và internet sẵn có. Giả định kỹ thuật theo [PLAN.md](./PLAN.md), dữ liệu theo [DATA_PLAN.md](./DATA_PLAN.md).

**Tỷ giá.** Vietcombank bán ra 26.180 đồng/USD ngày 25/09/2026. Thanh toán API bằng thẻ còn chịu phí giao dịch ngoại tệ khoảng 2–3%, nên dự toán dùng **27.000 đồng/USD**.

## Tóm tắt

| Khoản | Tối thiểu | Đầy đủ |
| --- | --- | --- |
| API mô hình AI (đã gồm 20% dự phòng) | 3,8 triệu | 7,2 triệu |
| SSD 1 TB (nếu không giải phóng được ổ C, D) | 0 | 3–5 triệu |
| USB hoặc ổ ngoài để sao lưu mã hóa | 0,3–0,5 triệu | 0,3–0,5 triệu |
| VPS 4 vCPU / 8 GB cho demo, nghiệm thu, 3 tháng | 0 (chạy trên máy) | 1–2 triệu |
| In ấn phiếu, báo cáo, đóng quyển | 0,3–0,5 triệu | 0,3–0,5 triệu |
| Phần mềm (toàn bộ mã nguồn mở), tên miền (dùng tên miền phụ có sẵn), OpenAlex/Crossref/arXiv | 0 | 0 |
| **Tổng** | **khoảng 4,4–4,8 triệu** | **khoảng 12–15 triệu** |

Khoản lớn nhất là API mô hình. Các khoản thiết bị chỉ phát sinh nếu không đủ dung lượng máy; ngày 26/09/2026 ổ C đã được dọn, còn trống khoảng 30 GB.

## 1. API mô hình AI

**Model được chọn** sau hai vòng đo (xem REVIEW_v2.md): gpt-6-sol và gpt-6-luna, gọi qua cổng API của nhóm. Giá theo OpenRouter ngày 26/09/2026, USD cho mỗi 1 triệu token:

| Model | Đầu vào | Đầu ra | Vai trò |
| --- | --- | --- | --- |
| gpt-6-sol | 2 | 10 | Tác tử điều phối |
| gpt-6-luna | 0,10 | 0,50 | Tác tử thực thi |
| gpt-5.6-sol | 2 | 10 | Dự phòng cho tác tử điều phối |
| claude-opus-4.8 (tham khảo) | 5 | 25 | Không dùng qua cổng này (xem REVIEW_v2.md) |

**Hai cấu hình** (NFR2 yêu cầu so sánh):

- Cấu hình A (chính): gpt-6-sol điều phối, gpt-6-luna thực thi.
- Cấu hình C (đối chứng): toàn bộ dùng gpt-6-sol.

**Token và chi phí mỗi lượt chạy.** Token vẫn là ước tính cũ, sẽ thay bằng số đo ở M-1. Khi chạy qua cổng, gpt-6-sol chiếm 92–95% chi phí của cấu hình A.

| Loại lượt chạy | Điều phối (vào / ra) | Thực thi (vào / ra) | Cấu hình A | Cấu hình C |
| --- | --- | --- | --- | --- |
| Tra cứu, thiếu dữ liệu, sai quyền (1 nhiệm vụ) | 18k / 4k | 25k / 3k | $0,08 | $0,16 |
| Tổng hợp liên lĩnh vực (3–4 nhiệm vụ) | 70k / 13k | 100k / 12k | $0,29 | $0,59 |
| Kịch bản NCKH T0–T6 (khoảng 40 lời gọi) | 170k / 30k | 360k / 45k | $0,70 | $1,81 |

**Số lượt chạy và chi phí.** Phần lớn kiểm thử khi phát triển dùng mô hình giả lập, không tốn tiền; bảng chỉ tính các lượt gọi mô hình thật. Chấm tự động dùng gpt-6-sol, khoảng $0,02 mỗi lượt. Chưa trừ prompt caching vì chưa kiểm chứng được cách cổng tính tiền phần cache.

| Giai đoạn | Đầy đủ | Tiết kiệm |
| --- | --- | --- |
| Phát triển, gỡ lỗi | 300 tra cứu, 50 tổng hợp, 30 NCKH, chia đều hai cấu hình: $95 | 200 tra cứu, 30 tổng hợp, 15 NCKH, chỉ cấu hình A: $35 |
| Thử nghiệm 20 câu | Lặp 3 lần × 2 cấu hình: $14 | Lặp 2 lần × 2 cấu hình: $9 |
| Nghiệm thu 60 tình huống | Lặp 3 lần × 2 cấu hình: $62 | Lặp 2 lần × 2 cấu hình: $41 |
| Kịch bản NCKH | 10 lần × 2 cấu hình: $25 | 6 lần × 2 cấu hình: $15 |
| Đo lại sau khi sửa | $10 | $6 |
| Demo, nghiệm thu trực tiếp | $5 | $5 |
| Chấm tự động | 480 lượt: $11 | 320 lượt: $7 |
| **Cộng** | **$222** | **$118** |
| **+20% dự phòng** (kết quả dài hơn dự kiến, chạy lại khi lỗi) | **$266 ≈ 7,2 triệu** | **$142 ≈ 3,8 triệu** |

Phương án tiết kiệm vẫn giữ đủ 2 cấu hình, bộ 60 tình huống và kịch bản NCKH như phiếu đề xuất; chỉ giảm số lần lặp từ 3 xuống 2 và gỡ lỗi chủ yếu bằng cấu hình A.

**Lưu ý về giá.** Đây là giá niêm yết của OpenRouter; cổng API nhóm đang dùng có thể tính khác và không có API xem số dư, nên cần đối chiếu trên trang quản lý của cổng sau tuần đầu. Nếu cần cấu hình Claude để đối chứng, mua trực tiếp từ Anthropic và dự trù khoảng 1,9 lần token cho tiếng Việt so với GPT.

## 2. Các khoản khác

- **Máy tính:** dùng máy hiện có (63,8 GB RAM, 18 lõi). Embedding và reranker chạy tại máy bằng model mã nguồn mở, không tốn phí API.
- **SSD 1 TB:** chỉ mua nếu không giải phóng được khoảng 20 GB trở lên cho WSL2, Docker và model. Giá SSD năm 2026 tăng mạnh do thiếu chip nhớ; nên dự trù 3–5 triệu và kiểm tra giá lúc mua.
- **Sao lưu:** DATA_PLAN.md yêu cầu bản sao mã hóa trên thiết bị riêng; một USB khoảng 128 GB là đủ cho dữ liệu tài liệu.
- **VPS:** chỉ cần nếu muốn hệ thống chạy liên tục cho người thẩm định dùng thử. VPS 4 vCPU / 8 GB ở Việt Nam khoảng 300–700 nghìn đồng/tháng. Có thể dùng lại VPS của NAU-AI nếu còn đủ tài nguyên.
- **Nguồn dữ liệu ngoài:** OpenAlex cấp miễn phí 1 USD/ngày; lượng truy vấn của đề tài nằm trong mức này. Crossref và arXiv miễn phí.

## 3. Kiểm soát chi phí

1. Đặt giới hạn chi tiêu trong trang quản trị API, ví dụ $90/tháng cho phương án đầy đủ hoặc $50/tháng cho phương án tiết kiệm.
2. Tuần đầu tháng 10 đo token thật của 5–10 lượt mỗi loại, rồi thay số vào bảng mục 1 để tính lại. Đây cũng là số liệu cho chỉ tiêu NFR2.
3. Kiểm thử tự động luôn dùng mô hình giả lập; chỉ gọi mô hình thật khi đo chất lượng.
4. Bật prompt caching cho phần cố định (system prompt, định nghĩa công cụ); tác tử thực thi dùng mức effort thấp nếu chất lượng vẫn đạt.
5. Nếu đổi nhà cung cấp hoặc cổng API, đo lại token trên chính kênh đó trước khi dùng bảng này: kênh Claude của cổng hiện tại chèn khoảng 508 token ẩn mỗi lời gọi, và Claude tốn khoảng 1,9 lần token tiếng Việt so với GPT.
