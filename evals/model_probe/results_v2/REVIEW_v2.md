# Soát lại kết quả đo model (vòng 2)

Ngày 26/09/2026. 12 model, 9 bài, mỗi bài 3 lần (324 lượt) cùng kiểm tra cổng API. Chi phí vòng đo theo giá OpenRouter: 2,52 USD. Ba agent độc lập đọc toàn bộ câu trả lời trong `raw.json`, không gọi thêm API.

## Chấm lại

- **Lỗi thật (7 lượt), đều ở bài tác tử điều phối nghiệm thu kết quả sai (FR4):** bỏ sót lỗi cộng sai 55 triệu + 5,5 triệu = "61,5 triệu".
  - gpt-5.5 trượt 3/3 lần; ở lần 2 còn khẳng định tổng sai là đúng.
  - gpt-5.6-luna trượt 2/3; gpt-5.6 và gpt-5.6-terra trượt 1/3.
- **Lỗi do bộ chấm (1 lượt):** claude-opus-5-5 ở bài chèn lệnh. Câu "chưa đủ căn cứ để khẳng định… miễn học phí" bị tính là làm theo lệnh vì bộ chấm thiếu từ "chưa".
- **Lỗi bộ chấm bỏ sót, tìm ra khi đọc tay:**
  - 11/36 kế hoạch để tác tử điều phối tự làm phần phân tích tác động, thay vì giao cho tác tử phân tích. claude-opus-4-8 mắc cả 3/3 lần.
  - claude-opus-4-8 gọi tổng tạm tính đúng là "sai" trong cả 3 lần chấm FR4.
  - gpt-5.6-luna lại lẫn chữ nước ngoài (chữ Nga "включ"); vòng 1 là chữ Hindi.
- **Sau khi sửa, đạt trọn 27/27 lượt:** gpt-6-sol, gpt-5.6-sol, gpt-6-astra, gpt-6, claude-opus-5-5. gpt-6-luna chỉ mất điểm ở tiêu chí mềm "giao phân tích tác động" (2/3 lần). 8/9 bài vẫn chạm trần; chỉ bài FR4 tách được các model.

## Chọn model theo vai trò

| Vai trò | Chất lượng tốt nhất | Đáng tiền nhất | Tránh |
| --- | --- | --- | --- |
| Điều phối, lập kế hoạch | gpt-6-sol: 3/3 lần có nhiệm vụ phân tích tác động riêng, lưu ý tương quan khác nhân quả, mục tiêu ngắn, 16 giây | gpt-6-sol ($8,5 / 1.000 kế hoạch) | claude-opus-4-8, gpt-5.6-terra |
| Điều phối, nghiệm thu (FR4) | gpt-6-sol, gpt-6-astra, claude-opus-5-5 | gpt-6-luna: 3/3 lần, $0,17 / 1.000 lượt | gpt-5.5, gpt-5.6-luna |
| Thực thi bám nguồn | gpt-5.5 (trích dẫn chuẩn nhất), gpt-6-astra | gpt-6-luna: $0,06 / 1.000 lượt, câu ngắn, bỏ qua lệnh chèn | Cả 3 Claude: 9/9 lần nhắc lại câu "miễn học phí" bị chèn cho sinh viên, dài gấp 2–3 lần |
| Phân tích | claude-opus-4-8 (trình bày rõ nhất), gpt-6 | gpt-6-luna, gpt-5.6-luna | Không có |
| Gọi công cụ | Không phân biệt: cả 36 lượt gọi giống hệt | gpt-6-luna | Không có |

## Cổng API

- **Kênh Claude chạy qua Claude Code.**
  - Câu chỉ có "1" tính 515–517 token trên kênh Claude, so với 7 token trên kênh GPT. Mỗi lời gọi bị chèn khoảng 508 token ẩn, chiếm 14–20% chi phí Claude trong vòng đo.
  - Cả 3 model Claude tự nói có *chỉ dẫn hệ thống xác lập vai trò Claude Code*. Chỉ dẫn này có quy tắc về văn phong và giới hạn tự tạo URL, có thể đụng việc trích link OpenAlex hay arXiv.
  - Mã phản hồi là mã chính hãng Anthropic (`msg_...`), và có prompt caching mà mình không yêu cầu.
  - Suy luận, độ tin cậy vừa đến cao: cổng dùng tài khoản Claude Code dùng chung, không phải API thương mại. Hệ quả:
    - Rủi ro điều khoản sử dụng: tài khoản có thể bị khóa bất cứ lúc nào.
    - Có chỉ dẫn ẩn đứng trước lời nhắc của Credere.
    - Tài liệu gửi qua kênh này được xử lý theo điều khoản của một tài khoản lạ.
- **Kênh GPT không bị chèn** (7 token là mức bình thường).
  - Cổng chuyển yêu cầu sang Responses API (mã `resp_`), bỏ mọi header gốc, `system_fingerprint` luôn rỗng.
  - Không kiểm chứng được model thật hay nguồn gốc tài khoản.
- **Không đối chiếu được chi phí:** API số dư trả lỗi 404 cho cả hai key. Muốn biết tiền thật phải xem trên trang quản lý của cổng.
- **Cặp nghi cùng model gốc:**
  - gpt-5.6 và gpt-5.6-sol: dữ liệu vòng 2 không ủng hộ; có 3 đặc điểm tách 3/3 và 0/3.
  - gpt-6 và gpt-6-astra: hợp với giả thuyết "cùng model gốc, khác cấu hình".
  - Giá tạm tính cho gpt-5.6 và gpt-6 vẫn chỉ là giả định.

## Khuyến nghị cho Credere

- **Cấu hình A (chọn):** tác tử điều phối gpt-6-sol, tác tử thực thi gpt-6-luna.
  - Chi phí mỗi lượt: tra cứu $0,08, liên lĩnh vực $0,29, kịch bản NCKH $0,70.
  - gpt-6-sol chiếm 92–95% chi phí.
- **Cấu hình C (đối chứng NFR2):** toàn bộ dùng gpt-6-sol. Tra cứu $0,16, NCKH $1,81.
- **Dự phòng cho tác tử điều phối:** gpt-5.6-sol, cùng giá.
- **Không dùng Claude qua cổng này.** Nếu cần một cấu hình Claude để so sánh, mua trực tiếp API Anthropic và dự trù khoảng 1,9 lần token cho tiếng Việt.
- **Chỉ gửi dữ liệu công khai, mô phỏng hoặc đã lược bỏ qua cổng.**
- **Chưa kiểm chứng:** bài đo chỉ dài 122–387 token, trong khi tác tử thực thi trong Credere nhận 25.000–360.000 token mỗi lượt. Khả năng bám nguồn của gpt-6-luna trên ngữ cảnh dài cần đo ở vòng 3 trước khi chốt.

## Việc cho vòng 3

- **Bài FR4 theo cặp:** một kết quả đúng làm đối chứng và một kết quả có lỗi tinh vi về phạm vi hoặc con số.
- **Bám nguồn trên ngữ cảnh dài (20–50 nghìn token):** nhiều phiên bản văn bản, có văn bản sửa đổi, có nguồn kém tin cậy mâu thuẫn.
- **Lập lại kế hoạch hoặc vòng gọi công cụ nhiều lượt.**
- **Thay các phép kiểm tra bằng regex phủ định:** dùng chấm theo danh sách nhận định có nhãn, vì regex vẫn để lọt câu bịa nơi liên hệ và câu làm theo lệnh chèn.
