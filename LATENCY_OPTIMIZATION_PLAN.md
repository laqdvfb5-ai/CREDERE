# Kế hoạch tối ưu tốc độ Credere

Cập nhật 29/09/2026 từ 36 bản ghi đã lưu; không gọi lại model.

## Kết luận hiện tại

Các Run hiện tại quá lâu nếu coi là câu hỏi tương tác cần trả ngay:

| Luồng | Số bản ghi | Trung vị | Khoảng |
| --- | ---: | ---: | ---: |
| AI Tổng hợp | 6 | 168,7 giây | 119,5–287,2 giây |
| AI Tuyển sinh | 15 | 103,5 giây | có lượt 432,1 giây |
| AI Đào tạo | 5 | 78,7 giây | tối đa 121 giây |

Lượt liên lĩnh vực đại diện mất 287,2 giây: lập kế hoạch 39,5 giây; AI Đào tạo hoàn tất khoảng 90 giây; AI Tuyển sinh khoảng 214 giây; Phân tích 19,2 giây; tổng hợp 14,8 giây. Một lượt có 18 lời gọi. Câu hỏi đơn cũng có median 79–104 giây theo lĩnh vực, nên còn chậm cho thao tác hàng ngày.

Nguyên nhân chính:

- Mỗi AI con chạy graph đầy đủ: lập kế hoạch, worker, nghiệm thu và tổng hợp.
- Kết quả AI con lại được AI Tổng hợp nghiệm thu lần nữa.
- Worker văn bản nhận tối đa 60.000 ký tự nguồn ở bước thực thi/review; một lời gọi đã mất 63,6 giây với khoảng 14.315 token đầu vào.
- Worker dữ liệu gọi model để chọn truy vấn rồi lại gọi model review, dù SQL và tổng đã do code kiểm tra.
- Khi lỗi provider, client có thể thử ba lần và chờ giữa các lần thử.

### API/gateway có phải nút thắt không?

Có dấu hiệu rõ, nhưng chưa đủ để kết luận gateway hay model backend chậm hơn. Trong 80 lời gọi của các Run Tổng hợp đã lưu, mọi lời gọi đều đi qua provider aigw; chưa có mẫu chạy cùng request qua OpenAI trực tiếp để đối chứng. Median latency mỗi lời gọi là 15,1 giây, p95 là 39,3 giây và tối đa 63,6 giây.

Latency tăng theo output rõ hơn theo input:

| Output token | Số lời gọi | Median latency |
| ---: | ---: | ---: |
| 0–300 | 40 | 9,7 giây |
| 300–700 | 22 | 14,1 giây |
| 700–1.200 | 14 | 25,6 giây |
| 1.200–2.000 | 3 | 40,9 giây |
| 2.000 trở lên | 1 | 63,6 giây |

Một lời gọi có 14.315 input token và 2.778 output token mất 63,6 giây. Một lời gọi khác có 19.306 input token nhưng 22,8 giây. Điều này cho thấy độ dài câu trả lời/model decoding và hàng đợi provider có ảnh hưởng lớn; input token vẫn làm tăng thời gian, nhưng không giải thích toàn bộ chênh lệch.

Không dùng tổng latency của các lời gọi để cộng thành thời gian người dùng chờ: hai AI con chạy song song nên tổng đó lớn hơn critical path. Cần đo từng request với cùng model/prompt qua aigw và provider trực tiếp, ghi time-to-first-byte, time-to-last-byte, input/output token, retry, HTTP status và provider. Chỉ sau phép đo đó mới nói được phần trăm chậm do gateway.

Benchmark không cần chạy toàn bộ bài: ba prompt cố định với output giới hạn 256/1.024/2.048 token, mỗi prompt lặp năm lần ở từng provider, ghi p50/p95. Tạm dừng nếu chi phí vượt ngân sách đã duyệt. Trong lúc chưa có đối chứng, tối ưu prompt và số lượt gọi đồng thời với việc đặt trần output; không kết luận đổi provider sẽ giải quyết toàn bộ độ trễ.

## Mục tiêu đề xuất

- Câu hỏi dữ liệu đơn: p50 dưới 30 giây, p95 dưới 60 giây.
- Câu hỏi một lĩnh vực: p50 dưới 60 giây, p95 dưới 120 giây.
- Câu hỏi Tổng hợp hai lĩnh vực: p50 dưới 90 giây, p95 dưới 180 giây.
- Báo cáo NCKH dài: chạy nền, hiển thị kết quả từng phần, không bắt người dùng chờ một request.

## Vòng 1 — giảm prompt và đo đúng critical path

1. Ghi latency từng bước: plan, mỗi AI con, worker, review, analysis, synthesize; kèm token/provider.
2. Chia tài liệu thành đoạn có mã/trang/mục. Chọn top-k đoạn liên quan thay vì đưa 60.000 ký tự vào hai prompt. Bắt đầu 6.000–12.000 ký tự, rồi đo recall.
3. Cache xếp hạng/chunk theo phiên bản nguồn và mục tiêu trong cùng Run.
4. Chạy 30 câu mới: 10 dữ liệu, 10 văn bản, 10 liên lĩnh vực.

Mục tiêu vòng 1: giảm ít nhất 30% p50 mà không giảm recall nguồn hoặc tăng lỗi schema.

## Vòng 2 — đường nhanh cho câu hỏi rõ

1. Router nhận diện câu hỏi khớp một truy vấn đã duyệt; code lấy tên truy vấn và tham số, vẫn kiểm quyền, mốc dữ liệu và schema.
2. Câu dữ liệu đơn bỏ model review nội dung; dùng kiểm tra định lượng/schema. Câu mơ hồ quay về đường nghiêm ngặt.
3. AI con có thể trả cấu trúc đã nghiệm thu trực tiếp cho Master; bỏ lượt tổng hợp văn bản bên trong khi không cần.
4. Cấp trên kiểm source IDs, trạng thái và phạm vi bằng code; chỉ gọi review model khi báo cáo con mâu thuẫn/thiếu nguồn.
5. Đặt hai chế độ:
   - Quick: một domain hoặc một truy vấn, tối đa một lần sửa, mục tiêu 10–30 giây.
   - Verified: full graph, review đủ, mục tiêu 1–3 phút và chạy nền nếu cần.

Mục tiêu vòng 2: dữ liệu đơn p50 dưới 30 giây; Tổng hợp p50 dưới 90 giây; không có ca đọc/xuất trái quyền.

## Vòng 3 — xử lý nền và vận hành

- Thêm checkpoint/resume trước các lời gọi bên ngoài.
- Chạy báo cáo dài ở background, SSE đọc lại và có nút hủy thật.
- Giới hạn đồng thời theo token/provider, chống hai Run trùng và giữ ngân sách theo Run.
- Retry theo loại lỗi: lỗi tạm thời mới retry; lỗi auth/model không retry.
- Đo ba Run đồng thời, p50/p95, tỷ lệ lỗi/retry, chi phí Run đạt và thời gian phục hồi.

## Quy tắc không được hy sinh

Tối ưu không được bỏ kiểm quyền, làm mất mã nguồn, cho phép model tự viết SQL, hoặc tự fallback dữ liệu hạn chế sang cloud. Quick chỉ dùng cho mục tiêu rõ và đầu ra có schema; báo cáo lãnh đạo/NCKH dùng Verified. Khi chưa đủ nguồn, trả thiếu dữ liệu thay vì chạy nhanh bằng suy đoán.

## Đánh giá

Task hiện tại quá lâu cho câu hỏi tương tác phức tạp, nhưng chưa cần tối ưu bằng cách hạ model ngay. Bắt đầu bằng prompt ngắn hơn, đường nhanh dữ liệu và bỏ review trùng; sau đó mới A/B model nhẹ cho plan/review. Mọi thay đổi phải đo cùng bộ câu mới và chấm cùng rubric.
