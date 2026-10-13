# Kịch bản trình bày AI Tuyển sinh (15 phút)

Người nghe: thầy Hiệu trưởng và lãnh đạo các khoa, phòng.

**Thông điệp chính:** AI Tuyển sinh là **trợ lý cho cán bộ Trung tâm Tuyển sinh và Truyền thông**, không phải chatbot cho thí sinh.
- Mục tiêu: trợ lý nắm được **văn bản và số liệu** mà cán bộ Trung tâm làm việc hằng ngày.
- **Giai đoạn 1: văn bản công khai.** Đã chạy được. Cán bộ dùng AI để tra cứu, soạn tin trả lời phụ huynh, lập bảng, báo cáo và rà soát văn bản.
- **Giai đoạn 2: số liệu của Trung tâm.** Gồm nguyện vọng, lọc ảo, xác nhận nhập học, chỉ tiêu còn lại, danh sách gọi nhắc, rà soát danh sách trúng tuyển.
  - Đã có **bản thử trên dữ liệu giả lập**. Ngành, chỉ tiêu, điểm chuẩn là số thật công khai; còn thí sinh là giả.
  - Muốn nối dữ liệu thật thì cần Nhà trường cho phép. Dữ liệu cá nhân không ra khỏi Trường.
- Cán bộ đọc lại, sửa rồi mới gửi đi. Thí sinh không hỏi AI trực tiếp.
- Cơ sở cho giai đoạn 2 là `..\NGHIEN_CUU_NGUOI_DUNG_TUYEN_SINH.md`: 50 câu hỏi cán bộ sẽ hỏi, trong đó chỉ 8 câu cần văn bản.

Lãnh đạo quan tâm ba điều: có ích gì cho Trường, có an toàn không, tốn bao nhiêu và cần Trường làm gì.
- Nói ít kỹ thuật. Tránh các từ "token", "API", "LLM", "SQL"; thay bằng "dịch vụ AI", "nhân viên AI", "truy vấn đã duyệt".
- Lời nói chi tiết cho từng slide nằm trong phần Notes của `AI_Tuyen_sinh_trinh_bay.pptx`. Trong PowerPoint, bật Presenter View để chỉ mình nhìn thấy.

## Phân bổ thời gian

| Slide | Nội dung | Thời lượng | Mốc |
| --- | --- | --- | --- |
| 1 | Tiêu đề, chào | 0:40 | 0:40 |
| 2 | Vấn đề: nhiều văn bản, nhiều số liệu, dồn vào tháng 7–9 | 1:20 | 2:00 |
| 3 | Giải pháp: trợ lý cho cán bộ, ba cam kết | 0:45 | 2:45 |
| 4 | Bên trong: các "nhân viên AI", có tác tử Dữ liệu | 1:15 | 4:00 |
| 5 | **Trình diễn phần văn bản** (em đóng vai cán bộ Trung tâm) | 3:30 | 7:30 |
| 6 | Dự phòng phần văn bản: chỉ chiếu nếu trình diễn hỏng | 0 | 7:30 |
| 7 | Kết quả thử nghiệm | 0:45 | 8:15 |
| 8 | **Cán bộ sẽ hỏi gì**, kèm **trình diễn phần số liệu** trên dữ liệu giả lập | 2:15 | 10:30 |
| 9 | Dự phòng phần số liệu: chỉ chiếu nếu trình diễn hỏng | 0 | 10:30 |
| 10 | Nguyên tắc an toàn | 0:35 | 11:05 |
| 11 | Chi phí | 0:40 | 11:45 |
| 12 | Lộ trình hai giai đoạn, sáu lĩnh vực | 0:45 | 12:30 |
| 13 | Đề nghị Nhà trường | 1:05 | 13:35 |
| 14 | Cảm ơn, hỏi đáp | 0:20 | 13:55 |

Còn khoảng 1 phút dự phòng. Nếu bị hỏi giữa chừng, rút ngắn slide 10 và 12.

## Chuẩn bị trước buổi trình bày (sáng hôm đó)

1. Sạc đầy máy. Chuẩn bị mạng dự phòng: phát 4G từ điện thoại.
2. Mở cửa sổ lệnh rồi chạy:
   ```
   cd C:\Users\laqdv\OneDrive\Desktop\credere\backend
   C:\Users\laqdv\.credere\venv\Scripts\python.exe -m app.web
   ```
   - Cửa sổ phải in dòng "Dữ liệu: Cơ sở dữ liệu tuyển sinh 2026 (GIẢ LẬP)…"; trên trang, góc phải có nhãn cam "Dữ liệu giả lập".
   - Nếu không có nhãn này thì chưa có cơ sở dữ liệu giả lập. Khi đó chạy `C:\Users\laqdv\.credere\venv\Scripts\python.exe scripts\make_gia_lap.py` trong thư mục backend.
   - Mở trình duyệt vào `http://127.0.0.1:8000`, phóng to 125–150% (Ctrl +) để người ngồi cuối phòng đọc được.
3. **Ghi lại 8 việc mẫu** bằng lệnh `C:\Users\laqdv\.credere\venv\Scripts\python.exe scripts\record_demo.py`, chạy trong thư mục backend.
   - Mất khoảng 20 phút và khoảng 20 nghìn đồng.
   - Nếu lúc trình bày dịch vụ AI lỗi, trang tự phát lại bản ghi của sáng hôm đó.
4. Tắt thông báo, tắt các cửa sổ khác, để sẵn trình duyệt cạnh PowerPoint (Alt+Tab để chuyển).

**Cách dùng trang:** trên trang có 8 thẻ "Việc thường làm": 4 thẻ văn bản và 4 thẻ số liệu.
- Bấm thẻ là chạy thật.
- **Giữ Shift rồi bấm** là phát lại bản ghi gần nhất; khi đó trang hiện nhãn "Bản ghi chạy thật lúc …".

## Trình diễn phần văn bản (slide 5)

Mở đầu bằng câu: *"Em đóng vai cán bộ Trung tâm Tuyển sinh."*
1. **Soạn tin trả lời phụ huynh: phát lại.** Chạy thật mất khoảng 3 phút.
   - Nói: "Để tiết kiệm thời gian, em phát lại bản chạy thật lúc … sáng nay."
   - Chỉ vào khung bên phải: tác tử điều phối lập kế hoạch, tác tử Tuyển sinh đọc tài liệu, tác tử Phân tích tính, tác tử điều phối nghiệm thu.
   - Chỉ vào tin nhắn: tin nhắn gọn, gửi được ngay; các mã nguồn nằm ở cuối. Học phí "khoảng 12 triệu đồng/năm" là ước tính do tác tử Phân tích tính (129 tín chỉ trong 3,5 năm), và tin nhắn có ghi rõ là ước tính.
   - **Bấm một mã nguồn** để mở văn bản gốc. Đây là điểm ăn tiền nhất: cán bộ kiểm tra được trước khi gửi.
2. **Báo cáo Ban Giám hiệu: phát lại.** Bảng các ngành tăng, giảm điểm chuẩn 2026 so với 2025; tác tử Phân tích tính chênh lệch bằng máy.
3. **Lập bảng chỉ tiêu: phát lại.**
   - Mỗi dòng ghi nguồn: ba ngành đào tạo giáo viên dùng số cập nhật tháng 7, các dòng khác vẫn là số tháng 2.
   - AI nhắc thông báo tháng 6 ghi tổng 2.356 để cán bộ đối chiếu, tránh dùng nhầm số cũ.
4. Nếu còn thời gian: phát lại thẻ "Kiểm tra văn bản". Ví dụ này cho thấy tổ hợp ngành Ngôn ngữ Trung ghi khác nhau giữa hai văn bản.

**Nếu trình diễn hỏng** (mất điện, máy treo): chuyển sang slide 6 rồi nói tiếp. Khi trình diễn chạy được thì bỏ qua slide 6.

## Slide 8: nối sang giai đoạn 2 và trình diễn phần số liệu

**Câu chuyển:** *"Phần vừa xem mới là văn bản. Nhưng cán bộ Trung tâm hỏi nhiều nhất về số liệu của chính mình."* Đọc lướt ba cột, rồi nói: *"Nhóm em đã làm bản thử trên dữ liệu giả lập: ngành, chỉ tiêu, điểm chuẩn là số thật công khai, còn thí sinh là giả."*

1. **Thẻ "Số liệu: xác nhận nhập học".** Chạy thật mất khoảng 1–2 phút; nếu muốn nhanh thì phát lại.
   - Chỉ vào khung bên phải: có thêm tác tử Dữ liệu (DL), tác tử này chọn truy vấn đã duyệt và cơ sở dữ liệu đếm.
   - Chỉ vào câu trả lời: bảng theo ngành, ghi rõ "dữ liệu giả lập lúc 17:00 ngày 18/08/2026". Ngành thiếu nhiều nhất là Kế toán.
2. **Thẻ "Danh sách gọi nhắc".** Chạy thật mất khoảng 1 phút.
   - **Điểm quan trọng nhất về an toàn:** câu trả lời của AI chỉ có số lượng theo mã cán bộ tư vấn.
   - Bảng danh sách bên dưới (tên, số điện thoại giả) lấy thẳng từ cơ sở dữ liệu tới màn hình này, không gửi cho dịch vụ AI.
   - Chỉ vào dòng "137 dòng · từ cơ sở dữ liệu, không qua AI" và nút "Tải CSV".
3. Nếu còn thời gian: thẻ **"Rà soát danh sách"**.
   - Nhóm cài sẵn 4 lỗi trong dữ liệu giả lập: 2 thí sinh trúng tuyển ngành giáo viên nhưng không thường trú Nghệ An, 1 thí sinh ở nguyện vọng lớn hơn 5, 1 thí sinh dưới điểm chuẩn.
   - AI tìm đủ cả 4 lỗi.
   - Liên hệ: năm 2025 có 16 trường sai sót khi công bố kết quả.

**Có thể nêu, nếu thấy phù hợp:** ngày 22/9/2026 Trường vẫn còn 556 chỉ tiêu dự kiến cho đợt 4 (theo thông báo đợt 4 của Trường). Theo dõi xác nhận nhập học và chỉ tiêu còn lại chính là loại câu hỏi ở cột giữa. Nói nhẹ nhàng, không đổ lỗi đơn vị nào.

**Nếu trình diễn hỏng:** chuyển sang slide 9, "Dự phòng: số liệu trên dữ liệu giả lập".

## Câu hỏi có thể gặp và gợi ý trả lời

| Câu hỏi | Gợi ý trả lời |
| --- | --- |
| Sao không cho thí sinh hỏi trực tiếp? | Vì thí sinh cần câu trả lời chắc chắn, còn AI vẫn có thể sai. Để cán bộ duyệt thì Trường vẫn chịu trách nhiệm như hiện nay, nhưng cán bộ làm nhanh hơn. Việc mở cho thí sinh chỉ nên xem xét khi có bộ nghiệm thu đủ lớn. |
| AI trả lời sai thì sao? | Mỗi con số có nguồn để cán bộ kiểm tra: văn bản có mã nguồn, số liệu ghi thời điểm dữ liệu. Cán bộ duyệt trước khi gửi. Kết quả trên bộ thử xem ở slide 7 và 8. Đây là bộ thử, chưa phải cam kết đúng tuyệt đối. |
| Khác gì ChatGPT? | ChatGPT không có tài liệu, số liệu của Trường và có thể bịa. AI Tuyển sinh chỉ đọc văn bản của Trường và Bộ, và dữ liệu của Trung tâm qua truy vấn đã duyệt. Nó dẫn nguồn, tính bằng máy, tự kiểm tra chéo, và nói rõ khi thiếu thông tin. |
| Dữ liệu giả lập là gì, có phải số thật không? | Không phải số thật về thí sinh. Ngành, mã, chỉ tiêu, điểm chuẩn lấy từ văn bản công khai của Trường. Thí sinh, nguyện vọng, xác nhận nhập học là giả: số điện thoại dạng 0000…, CCCD bắt đầu bằng GL. Mục đích là cho thấy cách làm trước khi được phép nối dữ liệu thật. |
| Vì sao không dùng dữ liệu thật? | Dữ liệu thí sinh là dữ liệu cá nhân, nhóm không được tự lấy. Cần Nhà trường cho phép bằng văn bản (đề nghị số 2), theo Luật Bảo vệ dữ liệu cá nhân 2025. |
| Dữ liệu có bị lộ ra ngoài không? | Bản sao dữ liệu tuyển sinh nằm trên máy chủ của Trường và chỉ đọc. Dịch vụ AI bên ngoài chỉ nhận số tổng hợp, ví dụ "Kế toán: 185 thí sinh đã xác nhận", không nhận tên, CCCD, số điện thoại. Danh sách thí sinh lấy thẳng từ cơ sở dữ liệu và chỉ hiện cho cán bộ có quyền. Bộ kiểm thử tự động kiểm tra rằng không lời gọi AI nào chứa tên hay số điện thoại thí sinh. |
| AI có tự viết câu lệnh vào cơ sở dữ liệu không? | Không. AI chỉ chọn trong danh mục 18 truy vấn đã duyệt và điền tham số; tham số sai bị chặn. Cơ sở dữ liệu mở ở chế độ chỉ đọc, nên AI không sửa hay xóa được gì. |
| AI có quyết định điểm chuẩn không? | Không. AI chỉ tính kịch bản tham khảo từ dữ liệu, ví dụ "lấy 15 điểm thì trúng tuyển thêm bao nhiêu", và rà soát sai sót trong danh sách. Hội đồng tuyển sinh quyết định. AI không ghi vào hệ thống của Bộ hay phần mềm xét tuyển. |
| Có thông báo mới thì cập nhật thế nào? | Thêm văn bản vào kho (thu thập, đối chiếu, gắn mã, ghi văn bản nào cập nhật văn bản nào), không phải lập trình lại. Sau mỗi lần cập nhật, chạy lại bộ thử. Cán bộ đầu mối gửi văn bản mới cho nhóm. |
| Sao chậm (có việc mất 3–6 phút)? | Vì nhiều bước: lập kế hoạch, tra cứu, tính toán, nghiệm thu, sửa nếu chưa đạt. Soạn văn bản dài chậm nhất; câu hỏi số liệu thường chỉ khoảng 45 giây. Hướng cải tiến: việc đơn giản đi đường ngắn; câu hỏi thường gặp được soạn sẵn và cán bộ duyệt một lần. |
| Tốn bao nhiêu, ai trả? | Trung bình khoảng 2.000 đồng một yêu cầu văn bản, đo trên 40 yêu cầu thử; soạn văn bản dài có thể tới 5–14 nghìn đồng. Câu hỏi số liệu khoảng 700 đồng. Trả theo mức dùng, có trần chi tiêu. Đề nghị Trường đứng tên tài khoản. |
| Có thay thế cán bộ tư vấn không? | Không. AI làm phần tra cứu, đếm, soạn nháp lặp lại; cán bộ quyết định nội dung gửi đi và xử lý trường hợp khó. |
| Vì sao không mua máy chủ AI riêng? | Nhóm đã tính: khoảng 2,2–3 tỷ đầu tư, khoảng 0,8 tỷ mỗi năm, và chất lượng tiếng Việt kém hơn. Máy riêng chỉ cần nếu muốn AI đọc trực tiếp dữ liệu cá nhân. Thiết kế của nhóm tránh việc đó: dữ liệu nằm trên máy chủ dữ liệu thông thường của Trường, dịch vụ AI chỉ nhận số tổng hợp. |
| Nếu dịch vụ AI tăng giá hay bị gián đoạn? | Hệ thống đã chạy được với nhiều nhà cung cấp cùng lúc: một nhà lỗi thì tự chuyển sang nhà khác, nhà lỗi bị tạm ngắt vài phút. Thêm hay bớt nhà cung cấp chỉ cần sửa tệp cấu hình, không lập trình lại. Khi mọi nhà đều lỗi, hệ thống báo lỗi rõ ràng và phát lại bản ghi, không đưa câu trả lời sai. |
| Mở rộng sang Đào tạo, NCKH, HTQT thế nào? | Cùng một lõi, thêm tác tử, tài liệu và truy vấn dữ liệu. Trước khi làm, nhóm phỏng vấn cán bộ từng đơn vị để biết họ thật sự hỏi gì. Dữ liệu nội bộ cần phân quyền và phiếu đồng ý của đơn vị. |

## Lưu ý khi nói

- Luôn nói "trợ lý cho cán bộ Trung tâm Tuyển sinh", không nói "chatbot cho thí sinh".
- Mỗi lần nhắc số liệu của phần 2, nói rõ **"dữ liệu giả lập"**. Không để người nghe tưởng đó là số thật của Trường.
- Đừng nói "AI không bao giờ dùng dữ liệu thí sinh"; hãy nói "dữ liệu cá nhân không ra khỏi Trường, chỉ người có quyền mới xem".
- Nói "nhóm em đo được", "trên bộ thử". Không nói "AI luôn đúng".
- **Không nêu tên đơn vị nào mắc lỗi.** Chỗ chưa thống nhất giữa các văn bản chỉ nói chung, và đề nghị gửi danh sách riêng cho Trung tâm (`DIEM_CHUA_THONG_NHAT.md`).
- Trước buổi trình bày, điền họ tên, lớp, giáo viên hướng dẫn và ngày vào slide 1.

## Tệp liên quan

- `AI_Tuyen_sinh_trinh_bay.pptx`: slide, lời nói nằm trong Notes. Tạo lại bằng `build_deck.py`, số liệu lấy từ `deck_numbers.json`.
- `DIEM_CHUA_THONG_NHAT.md`: danh sách chỗ chưa thống nhất giữa các văn bản; gửi riêng cho Trung tâm sau buổi trình bày.
- `shots/`: ảnh chụp trang demo cho hai slide dự phòng.
- `..\NGHIEN_CUU_NGUOI_DUNG_TUYEN_SINH.md`: nghiên cứu "cán bộ sẽ hỏi gì", kèm phiếu phỏng vấn cán bộ Trung tâm.
- Kết quả thử nằm ở `C:\Users\laqdv\credere-data\06_ket-qua\tuyen-sinh\`:
  - `eval-*.json`: 30 câu văn bản; lần chạy chốt `eval-20260928-0528.json` đạt 30/30.
  - `kich-ban-*.md`: 10 tình huống cán bộ, có chấm tay; lần chạy chốt `kich-ban-20260928-0526.md` đạt 10/10.
  - `du-lieu-*.json`: 14 câu số liệu trên dữ liệu giả lập, trong đó `du-lieu-20260928-0516.json` đạt 14/14.
- Dữ liệu giả lập: `C:\Users\laqdv\credere-data\03_xu-ly\tuyen_sinh\gia_lap\`. Tạo lại bằng `scripts\make_gia_lap.py`.
