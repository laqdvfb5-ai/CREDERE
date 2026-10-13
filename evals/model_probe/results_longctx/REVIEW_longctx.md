# Soát lại bài đo bám nguồn trên ngữ cảnh dài (điều kiện M-1)

Ngày 26/09/2026. Bộ văn bản quy chế mô phỏng (hạt giống 2026) gồm: quy chế cũ QĐ-105, quy chế hiện hành QĐ-620, quyết định sửa đổi QĐ-712, bài diễn đàn nói sai, nhiều văn bản gây nhiễu và một câu cần tìm ở cuối.

- **Ba lượt đo, tổng 158 câu trả lời, 0 lỗi cổng:**
  - [SUMMARY.md](./SUMMARY.md): 3 model × 8 câu × 2 lần ở ~21k và ~52k token (96 lượt).
  - [results_longctx_hard](../results_longctx_hard/SUMMARY.md): 3 câu bẫy mới × 3 model × 2 lần ở ~52k token (18 lượt).
  - [results_longctx_stress](../results_longctx_stress/SUMMARY.md): gpt-6-luna với 11 câu × 2 lần ở ~104k và ~202k token (44 lượt).
- **Chi phí theo giá OpenRouter:** 6,85 USD. Trong đó gpt-6-luna chỉ tốn 0,84 USD cho 82 lượt.
- **Soát lại:** bốn agent chấm tay từng câu, mỗi phát hiện được một agent khác kiểm lại, và một agent đánh giá độ tin cậy của chính bài đo. Không gọi thêm API.

## Kết quả

| Model | ~21k | ~52k | Bẫy khó ~52k | ~104k | ~202k | Chi phí mỗi lượt ở ~52k |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | 16/16 | 16/16 | 6/6 | 22/22 | 22/22 | ~0,005 USD |
| gpt-6-sol | 16/16 | 16/16 | 6/6 | — | — | ~0,105 USD |
| gpt-5.6-sol | 16/16 | 16/16 | 6/6 | — | — | ~0,105 USD |

- **Đọc tay xác nhận cả 158 đáp án cuối đều đúng.**
  - 235/235 cặp [văn bản, Điều] được trích đều có thật.
  - Không câu nào lấy bài diễn đàn làm căn cứ.
  - gpt-6-luna không kém đi khi văn bản dài tới ~202k token.
- **Cổng trả đúng tên model được gọi ở cả 158 lượt.**
- **Điểm trừ nhỏ của gpt-6-luna:**
  - 14/16 câu về giá trị đã sửa đổi trích kèm điều cũ, ví dụ `[QĐ-620, Điều 3; QĐ-712, Điều 1]`, mà không nói điều đó đã bị sửa. Hai agent soát bất đồng ở điểm này: một agent coi là cách dẫn điều đã sửa đổi thông thường, agent kia coi là lỗi nhỏ.
  - 1 lượt (câu `nhan_phi`, ~52k, lần 1) nêu thêm mức 66.000 đồng theo quy chế cũ QĐ-105 cho "khóa trước 2025". Bộ chấm cho qua chỉ vì câu có chữ "trước".
- **gpt-6-sol và gpt-5.6-sol cũng có lúc tách "khóa trước 2025" như vậy** (2 lượt ở câu `dien_dan`). Nguyên nhân nằm ở bộ văn bản: câu "áp dụng cho sinh viên tuyển sinh từ khóa 2025 và thay thế QĐ-105" có thể hiểu là QĐ-105 vẫn áp dụng cho các khóa trước. Đáp án mẫu lại bỏ qua cách hiểu đó.

## Vì sao không kết luận được

Bài đo đã **bão hòa**: cả ba model đều đạt 100%, nên bài đo không tách được model nào tốt hơn.
- **Một script chỉ dò từ khóa, không dùng model, cũng đạt 1,00** ở mọi câu và mọi cỡ.
- **Bộ văn bản quá dễ:**
  - Dòng nào cũng mở đầu bằng thẻ `[văn bản, Điều n]`, nên chép thẻ là có trích dẫn.
  - Văn bản cũ tự ghi "đã được thay thế", diễn đàn tự ghi "không chính thức", còn văn bản sửa đổi ghi rõ "Sửa đổi QĐ-620, Điều 3 … các hệ khác giữ nguyên".
  - Văn bản gây nhiễu không có từ nào trùng với câu hỏi. Văn bản dài thêm chỉ là phần đệm, không thêm ứng viên nào cạnh tranh.
  - Câu cần tìm luôn nằm ở cuối, là vị trí dễ nhất.
  - Chỉ có một hạt giống; tính ra thực chất chỉ khoảng 11 câu hỏi độc lập. Không lỗi trên 11 câu vẫn chưa loại được tỷ lệ lỗi tới khoảng 27%.
- **Bộ chấm dễ dãi:** 16/16 câu trả lời sai do agent cố ý viết đều được 1,00. Những điểm yếu chính:
  - `dung_dap_an` chỉ cần số đúng xuất hiện ở đâu đó. Số nhỏ như 6, 8, 10 còn khớp cả với "Điều 6".
  - `trich_dung_nguon` chỉ kiểm tra mã văn bản có mặt, không kiểm tra số điều. `QĐ-TC-1` còn khớp với `QĐ-TC-10`.
  - Danh sách chữ miễn trừ (`trước`, `sửa đổi`, `cũ`…) cho qua cả câu nêu sai hướng. `cũ` còn khớp với `cũng`.
  - Một số đáp án trùng giá trị khác trong văn bản: 23, 20.000, 25, 6. Trả lời nhầm hệ hoặc nhầm quy chế cũ nên không bị phát hiện.
  - Lượt lỗi cổng bị bỏ khỏi mẫu số thay vì tính là trượt. Đợt này không có lượt nào như vậy.
- **Lỗi nhỏ của bộ sinh văn bản:** ở cỡ 65k chỉ có 4 văn bản đệm, nên bài diễn đàn nằm sát QĐ-712 chứ không nằm giữa.

## Kết luận cho M-1

- **Chưa kết luận được.** Phép đo M-1 đã làm đúng như đã ghi: gpt-6-luna được đo ở 20–50k token, có nhiều phiên bản văn bản và nguồn mâu thuẫn, và không sai câu nào. Nhưng bài đo bão hòa, nên không đủ để khẳng định "đạt" hay "không đạt".
- **Điều bài đo chứng minh được:** gpt-6-luna không sụp khi tra cứu trên văn bản dài tới ~202k token, và làm theo đúng các nhãn thay thế, sửa đổi và nguồn không chính thức khi các nhãn đó được ghi rõ. Nếu trượt bài này thì gpt-6-luna đã bị loại.
- **Điều bài đo chưa chứng minh được:**
  - Suy ra văn bản nào còn hiệu lực từ ngày ban hành, ngày hiệu lực và khóa áp dụng.
  - Hai nguồn chính thức mâu thuẫn nhau.
  - Sửa đổi ở mức khoản, điểm.
  - Văn bản thật chuyển bằng Docling.
  - Tổng hợp từ 3 điều trở lên.
  - Trả kết quả dạng JSON claims có trích nguyên văn như backend cần.
- **Trong lúc chờ bài đo phân biệt:** mọi kết quả của Worker gpt-6-luna trong backend đều đã qua bước nghiệm thu của gpt-6-sol (FR4) và kiểm tra nguồn bằng code. Vì vậy có thể giữ cấu hình A khi phát triển, nhưng chưa dùng cấu hình A cho pilot trước khi có bài đo phân biệt.

## Bài đo tiếp theo (M-1b)

Chi phí ước tính theo giá OpenRouter, gồm luna và sol.

1. **Kiểm tra bộ chấm trước (miễn phí):** 16 câu sai ở trên phải bị chấm dưới 1. Script dò từ khóa phải đạt điểm thấp hơn hẳn các model; nếu không, bộ câu hỏi còn quá dễ.
2. **Văn bản thật của Trường chuyển bằng Docling, không gắn thẻ từng dòng.**
   - Gồm quy chế, quyết định sửa đổi, thông báo học phí và Thông tư 08/2021.
   - 40–60 câu, chấm cả giá trị lẫn trích dẫn tới Điều/khoản.
   - Chi phí: khoảng 0,65 USD cho luna và 13 USD cho sol, cộng 1–2 ngày công soạn đáp án.
3. **Mâu thuẫn khó trên bộ mô phỏng, dùng từ 5 hạt giống trở lên.**
   - Bỏ các nhãn "đã được thay thế" và "Sửa đổi Điều k".
   - Thêm hiệu lực theo ngày và theo khóa, bãi bỏ ở mức điểm/khoản, hai nguồn chính thức mâu thuẫn, và văn bản nhiễu cùng chủ đề đặt ở giữa.
   - Chi phí: khoảng 1,3 USD cho luna và 25 USD cho sol.
4. **Trả kết quả dạng JSON claims đúng schema backend:** mỗi claim có trích nguyên văn, và code kiểm tra đoạn trích có thật trong văn bản. Chi phí: khoảng 0,9 USD cho luna và 18 USD cho sol.
5. **Câu hỏi tổng hợp từ 3 điều trở lên, trong đó một phần thiếu căn cứ,** lặp 5 lần mỗi câu. Chi phí: khoảng 0,4–1,5 USD cho luna và 8–17 USD cho sol.
