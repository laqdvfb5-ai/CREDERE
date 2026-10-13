# Nội dung chi tiết bài thuyết trình Credere — 15 phút

Theo đủ nội dung trong `yeucauslide.txt`. Bản chính **15 slide, tổng 15 phút**; 8 slide phụ lục chỉ mở khi hỏi đáp và được ẩn khỏi lượt trình chiếu thông thường. Mỗi slide có nội dung trình chiếu và lời nói đầy đủ dưới đây.

**Trọng tâm:** toàn bộ công việc mà dự án sẽ làm khi hoàn chỉnh, gồm sáu lĩnh vực, nhóm người dùng, đầu vào/đầu ra, phối hợp và bàn giao. Tình trạng demo chỉ là một mục minh chứng ở slide 6.

**Thời lượng:** bao gồm 1 phút 20 giây giới thiệu bản demo. Nếu yêu cầu live chưa xong, chuyển tiếp; ảnh phụ lục là kết quả đã lưu, phải nói rõ.

**Ngày đối chiếu:** 29/09/2026. **Demo:** https://proxyllm.store. Các tệp này không chứa mật khẩu, API key hay thông tin SSH.

## Đối chiếu yêu cầu

| Yêu cầu | Slide chính | Chi tiết phụ lục |
| --- | --- | --- |
| Tổng thể toàn bộ dự án | 1, 2, 3, 4, 14, 15 | 19, 23 |
| Cách hệ thống hoạt động | 2, 4, 6 | 22, 23 |
| Lợi ích so với quy trình con người tự làm | 5, 14 | 19, 23 |
| Phương án và kế hoạch triển khai dự án | 3, 6, 7, 10, 12, 13, 14, 15 | 17, 19, 23 |
| OpenAI API / model local: giá, lợi ích và bất lợi | 7, 8, 9, 10, 15 | 16, 17, 18, 20, 23 |
| Phương án bảo mật thông tin nhà trường | 10, 11, 12, 14, 15 | 20, 21, 23 |

## Phân bổ thời gian

| Slide | Chủ đề | Thời lượng | Mốc kết thúc |
| --- | --- | --- | --- |
| 1 | Credere: hệ thống trợ lý AI cho toàn trường | 0:30 | 0:30 |
| 2 | Bài toán tổng thể: từ yêu cầu đến công việc hoàn chỉnh | 1:10 | 1:40 |
| 3 | Phạm vi nghiệp vụ hoàn chỉnh gồm sáu lĩnh vực | 1:30 | 3:10 |
| 4 | Điều phối một yêu cầu qua nhiều lĩnh vực | 1:05 | 4:15 |
| 5 | Con người tự làm và có Credere hỗ trợ | 0:50 | 5:05 |
| 6 | Bản demo hiện tại là bước kiểm chứng ban đầu | 1:20 | 6:25 |
| 7 | Ba lựa chọn nơi xử lý model | 1:00 | 7:25 |
| 8 | API OpenAI: giá và cách tính một yêu cầu | 1:00 | 8:25 |
| 9 | Model local: chủ động dữ liệu, thêm công vận hành | 1:05 | 9:30 |
| 10 | Phương án chọn: API trước, local theo yêu cầu dữ liệu | 0:50 | 10:20 |
| 11 | Phân loại thông tin trước khi chọn tuyến AI | 0:45 | 11:05 |
| 12 | Bảo mật: từ cài đặt đến dữ liệu nghiệp vụ | 0:55 | 12:00 |
| 13 | Lộ trình hoàn thành toàn dự án theo từng giai đoạn | 1:15 | 13:15 |
| 14 | Bàn giao một hệ thống có thể sử dụng và vận hành | 1:05 | 14:20 |
| 15 | Đích đến: trợ lý phối hợp cho mọi mảng công việc của trường | 0:40 | 15:00 |

## Nội dung và lời nói

### Slide 1. Credere: hệ thống trợ lý AI cho toàn trường

**Thông điệp:** Kết nối sáu lĩnh vực để hỗ trợ nghiệp vụ và quyết định có căn cứ.

**Nội dung trên slide:**

- **Phục vụ** — Lãnh đạo · phòng ban · người học
- **Phối hợp** — Sáu AI lĩnh vực + lớp điều phối
- **Tạo kết quả** — Báo cáo · kế hoạch · bằng chứng

**Lời thuyết trình:**

Kính thưa quý thầy cô, Credere hướng tới một hệ thống trợ lý AI dùng chung cho toàn trường. Hệ thống sẽ hỗ trợ sáu lĩnh vực nghiệp vụ, phối hợp dữ liệu giữa các đơn vị và tạo báo cáo, kế hoạch có căn cứ cho người có thẩm quyền. Em sẽ trình bày toàn bộ phạm vi dự án, cách hoạt động, lợi ích, phương án triển khai và bảo mật. Bản demo chỉ là bước kiểm chứng ban đầu trong bức tranh đó.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Mục tiêu toàn dự án là xây dựng một nền tảng AI đa tác tử dùng chung cho trường đại học, hỗ trợ công việc chuyên môn của sáu lĩnh vực và tổng hợp liên đơn vị cho Ban Giám hiệu. Phạm vi hoàn chỉnh bao gồm dữ liệu có quyền và phiên bản, trợ lý theo chuyên môn, điều phối công việc nhiều bước, tra cứu và phân tích, soạn thảo báo cáo/kế hoạch, nguồn kiểm chứng, lịch sử, quản trị và vận hành. Người dùng là cán bộ, giảng viên, lãnh đạo; sinh viên/thí sinh có kênh tự phục vụ theo quyền trong phạm vi được duyệt. Đây là mô tả đích đến sẽ xây dựng. Bản demo hiện tại chỉ là một phần kiểm chứng được giới thiệu sau, không phải toàn bộ phạm vi dự án.

**Căn cứ:** `PLAN.md: Mục tiêu và Phạm vi Worker`; `Bài toán.docx`; `yeucauslide.txt`

**Chuyển ý:** Từ nội dung này, chuyển sang: bài toán tổng thể: từ yêu cầu đến công việc hoàn chỉnh.

### Slide 2. Bài toán tổng thể: từ yêu cầu đến công việc hoàn chỉnh

**Thông điệp:** Tiếp nhận yêu cầu nghiệp vụ, lấy đúng dữ liệu, phối hợp xử lý và trả sản phẩm để duyệt.

**Nội dung trên slide:**

- **Phục vụ ai?** — Lãnh đạo, phòng ban, giảng viên; người học theo quyền.
- **Kết nối những gì?** — Quy chế, hồ sơ, CSDL nghiệp vụ và nguồn học thuật.
- **Xử lý việc gì?** — Tra cứu, phân tích, đối chiếu, dự thảo và lập kế hoạch.
- **Trả lại sản phẩm gì?** — Báo cáo, bảng so sánh, đề xuất, chi phí và nguồn dẫn.

Ghi chú hiển thị: Cùng nền tảng: quyền dữ liệu, phiên bản, tiến độ, lịch sử, xuất file và quản trị.

**Lời thuyết trình:**

Bài toán tổng thể là giải quyết một công việc từ đầu đến đầu. Lãnh đạo cần báo cáo liên phòng và phương án hành động; cán bộ cần tra quy định, xử lý số liệu và soạn thảo; giảng viên cần hỗ trợ đào tạo, nghiên cứu; người học có thể sử dụng thông tin và hồ sơ trong phạm vi được cấp quyền. Credere sẽ kết nối văn bản, CSDL nghiệp vụ và nguồn học thuật, phân công xử lý rồi trả sản phẩm: bảng đối chiếu, dự thảo, báo cáo, kế hoạch triển khai và chi phí, kèm nguồn và phần chưa đủ căn cứ. Toàn bộ nền tảng còn phải có quyền truy cập, phiên bản dữ liệu, tiến độ, lịch sử, xuất kết quả và quản trị. Người dùng vẫn kiểm tra và duyệt quyết định.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Bài toán xuất phát từ công việc của một trường, không phải từ việc chọn model. Một yêu cầu có thể cần nhiều đầu mối, nhiều tài liệu, phép tính và biểu mẫu. Credere sẽ tiếp nhận yêu cầu, làm rõ phạm vi và kỳ dữ liệu, chia thành công việc, kết nối nguồn được phép, phối hợp các AI chuyên môn và tạo đầu ra có căn cứ. Lãnh đạo cần báo cáo liên phòng và phương án hành động; phòng ban cần xử lý nghiệp vụ, tra quy định và soạn thảo; giảng viên cần hỗ trợ đào tạo/nghiên cứu; người học có thể tra thông tin công khai và phần hồ sơ được phép. Đầu ra không chỉ là câu trả lời chat: còn bảng đối chiếu, dự thảo văn bản, kế hoạch triển khai với chi phí, danh mục nguồn và những thông tin còn thiếu. Toàn nền tảng cần quyền truy cập, phiên bản nguồn, tiến độ, lịch sử và khả năng xuất kết quả. Người có thẩm quyền vẫn kiểm tra và phê duyệt quyết định.

**Căn cứ:** `Bài toán.docx: Mục tiêu, Master, Kịch bản nghiệm thu`; `PLAN.md: Giao diện, Dữ liệu và quyền`

**Chuyển ý:** Từ nội dung này, chuyển sang: phạm vi nghiệp vụ hoàn chỉnh gồm sáu lĩnh vực.

### Slide 3. Phạm vi nghiệp vụ hoàn chỉnh gồm sáu lĩnh vực

**Thông điệp:** Mỗi AI chuyên môn có nguồn, công cụ và quyền riêng; cùng phục vụ công việc toàn trường.

**Nội dung trên slide:**

- **Tuyển sinh** — Chỉ tiêu, tư vấn, hồ sơ, xác nhận nhập học; báo cáo mùa tuyển sinh.
- **Đào tạo** — Thiết kế chương trình, chuẩn đầu ra; học vụ, tín chỉ, lớp và lịch thi.
- **Nghiên cứu khoa học** — Đề tài, công bố, tài trợ; phân tích xu hướng và đề xuất kế hoạch.
- **Hợp tác quốc tế** — Đối tác, liên kết đào tạo, học bổng; trao đổi và hợp tác nghiên cứu.
- **Nhân sự** — Hợp đồng, chính sách, lương, KPI; phân tích nhu cầu nhân lực.
- **Hành chính** — Công văn, thủ tục, cơ sở vật chất; hướng dẫn và soạn thảo.

Ghi chú hiển thị: Đích đến của toàn dự án. Triển khai theo giai đoạn, dữ liệu được duyệt và quyền của từng người.

**Lời thuyết trình:**

Phạm vi hoàn chỉnh gồm sáu mảng. Tuyển sinh hỗ trợ chỉ tiêu, tư vấn, hồ sơ, xác nhận nhập học và báo cáo mùa tuyển sinh. Đào tạo hỗ trợ thiết kế chương trình, chuẩn đầu ra, quy chế, học vụ, tín chỉ, lớp và lịch thi. Nghiên cứu khoa học hỗ trợ đề tài, công bố, tài trợ, phân tích xu hướng và xây dựng kế hoạch nghiên cứu. Hợp tác quốc tế hỗ trợ đối tác, liên kết đào tạo, học bổng, trao đổi và nghiên cứu chung. Nhân sự hỗ trợ tra chính sách, hợp đồng, lương, KPI và nhu cầu nguồn lực theo quyền. Hành chính hỗ trợ công văn, thủ tục, cơ sở vật chất và dự thảo văn bản. Các AI dùng nguồn và công cụ chuyên môn riêng nhưng có thể phối hợp cho một yêu cầu chung. Đây là toàn bộ phạm vi sẽ xây dựng, triển khai theo giai đoạn.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Tuyển sinh sẽ hỗ trợ tra chỉ tiêu/điểm chuẩn/học phí, tư vấn theo nguồn chính thức, xử lý hồ sơ và thống kê các mốc của mùa tuyển sinh. Đào tạo sẽ hỗ trợ thiết kế và rà soát chương trình, biên soạn chuẩn đầu ra, quy chế theo khóa, đăng ký học phần, cảnh báo học vụ, lớp học phần và lịch thi. Nghiên cứu khoa học sẽ quản lý/tra cứu đề tài và công bố, phân tích xu hướng, cơ hội tài trợ, so sánh nghiên cứu và phát triển kế hoạch/đề xuất đề tài. Hợp tác quốc tế sẽ hỗ trợ chiến lược đối tác, liên kết đào tạo, học bổng, trao đổi sinh viên/giảng viên và hợp tác nghiên cứu. Nhân sự sẽ tra chính sách/hợp đồng/lương, tổng hợp KPI và nguồn lực theo quyền; không tự quyết định xử lý cá nhân. Hành chính sẽ tra công văn, thủ tục và cơ sở vật chất, hướng dẫn quy trình và soạn dự thảo. Phạm vi sáu lĩnh vực lấy từ PLAN và mô hình dự án; ba lĩnh vực tối thiểu của đề bài gốc là Đào tạo, NCKH, HTQT. Tất cả mô tả này là chức năng dự án hướng tới; không tuyên bố sáu ứng dụng đã hoàn thành.

**Căn cứ:** `PLAN.md: Phạm vi Worker`; `Bài toán.docx: Các Tác tử Tớ`; `2aOboR0Rm398ong6dRyFudWSqCsv9pwaaPdoY5tg.jpg`

**Chuyển ý:** Từ nội dung này, chuyển sang: điều phối một yêu cầu qua nhiều lĩnh vực.

### Slide 4. Điều phối một yêu cầu qua nhiều lĩnh vực

**Thông điệp:** Master lập kế hoạch → giao đúng AI → kiểm tra/sửa → tổng hợp kết quả để người dùng duyệt.

**Nội dung trên slide:**

- **Đầu vào** — Yêu cầu, mục tiêu, mốc thời gian và phạm vi được phép.
- **AI chuyên môn** — Chọn các lĩnh vực cần thiết; chạy tuần tự hoặc song song.
- **Hỗ trợ dùng chung** — Tìm kiếm, truy vấn dữ liệu và phân tích/tính toán.
- **Đầu ra** — Báo cáo + bằng chứng + kế hoạch/chi phí + hạn chế.

Ghi chú hiển thị: Ví dụ đề bài: phân tích AI trong NCKH 3 năm, so 3 case study, đề xuất lộ trình và chi phí.

**Lời thuyết trình:**

Master sẽ nhận yêu cầu, phân rã và lập kế hoạch trước khi giao cho những AI liên quan. Việc độc lập có thể song song; việc phụ thuộc đợi đầu vào đạt. Các AI chuyên môn được hỗ trợ bởi tìm kiếm, truy vấn và phân tích, rồi Master kiểm tra, yêu cầu sửa có giới hạn và tổng hợp. Ví dụ trong đề bài: phân tích ứng dụng AI vào NCKH ba năm, so sánh ba case study, đề xuất lộ trình và chi phí năm tới. NCKH phụ trách bằng chứng nghiên cứu, HTQT hay Đào tạo bổ sung khi cần đối tác hoặc kỹ năng; công cụ phân tích tính chi phí. Kết quả phải có nguồn và lịch sử truy vết. Không phải câu nào cũng gọi đủ sáu AI hoặc được đọc toàn bộ dữ liệu.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Ví dụ từ đề bài gốc là phân tích tác động của AI tới kết quả NCKH trong ba năm, so sánh ba case study và đề xuất lộ trình/chi phí cho năm tới. Master sẽ xác định tiêu chí, kỳ dữ liệu và lập kế hoạch trước khi giao việc. AI NCKH phụ trách nghiên cứu và công bố; AI HTQT bổ sung đối tác hoặc hợp tác khi liên quan; AI Đào tạo hỗ trợ nhu cầu kỹ năng/chương trình, các AI khác chỉ tham gia nếu cần nguồn lực/hành chính thuộc phạm vi của chúng. Worker tìm kiếm thu nguồn; Worker phân tích chuẩn hóa chỉ số và tính chi phí. Mỗi tác vụ trả dữ liệu theo hợp đồng có task_id, trạng thái và lỗi. Master nghiệm thu, yêu cầu sửa có hướng dẫn và số lượt tối đa rồi tổng hợp. Dự án sẽ lưu trạng thái trung gian và lịch sử theo quyền để truy vết và phục hồi. Không bắt buộc mọi câu hỏi gọi đủ sáu AI; không mặc định cấp Tổng hợp được đọc hết CSDL. Cán bộ kiểm tra bằng chứng và phê duyệt báo cáo cuối.

**Căn cứ:** `Bài toán.docx: FR1–FR4, NFR1–NFR3, kịch bản NCKH`; `PLAN.md: Luồng thực thi và Dữ liệu/quyền`

**Chuyển ý:** Từ nội dung này, chuyển sang: con người tự làm và có credere hỗ trợ.

### Slide 5. Con người tự làm và có Credere hỗ trợ

**Thông điệp:** AI hỗ trợ thao tác lặp lại; con người giữ quyền hiểu bối cảnh và phê duyệt.

**Nội dung trên slide:**

| Công đoạn | Tự làm | Có Credere hỗ trợ |
| --- | --- | --- |
| Tìm và lấy dữ liệu | Mở văn bản, lọc bảng, hỏi đầu mối | Tra nguồn / chọn truy vấn định sẵn |
| Ghép nhiều đơn vị | Chờ từng đầu mối rồi ghép | Giao AI con, kết hợp khi đầu vào đạt |
| Tính và viết | Tính toán, lập bảng, soạn báo cáo | Code tính; AI viết nháp có nguồn |
| Kiểm tra và quyết định | Cán bộ kiểm tra, lãnh đạo duyệt | Vẫn do cán bộ và lãnh đạo chịu trách nhiệm |

**Lời thuyết trình:**

So với tự làm, cán bộ thường phải mở nhiều nguồn, lấy số từ các phòng, ghép bảng, tính và viết lại. Credere sẽ hỗ trợ phần lặp lại đó và cho thấy nguồn, kế hoạch, kết quả từng bước. Con người vẫn xác nhận định nghĩa chỉ số, bối cảnh và phê duyệt đầu ra. Chúng em chưa tuyên bố đã tiết kiệm một tỷ lệ cụ thể. Pilot sẽ đo cùng công việc theo hai cách, tính cả thời gian đọc lại và sửa, đến khi báo cáo được chấp nhận. Như vậy lợi ích được đánh giá bằng công sức thực sự giảm cùng chất lượng, thay vì chỉ tốc độ AI trả chữ.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Hiện cán bộ phải mở nhiều văn bản, lấy các bảng từ từng phòng, kiểm tra cùng kỳ rồi tính và viết lại. Khi có Credere, AI đề xuất kế hoạch, lựa chọn công cụ và soạn kết quả từ nguồn đã nối. Các bước độc lập có thể chạy song song. Tuy nhiên, thuật ngữ nghiệp vụ, văn bản nào áp dụng cho khóa nào và cách xử lý ngoại lệ vẫn cần cán bộ kiểm tra. Code tính đúng một biểu thức không bảo đảm model chọn đúng đầu vào. Vì vậy so sánh phải tính cả công rà soát và sửa. Chúng ta không khẳng định AI tốt hơn con người ở mọi công việc, cũng không dùng AI để thay thẩm quyền ban hành quyết định.

**Căn cứ:** `backend/app/graph.py`; `backend/app/workers.py`

**Chuyển ý:** Từ nội dung này, chuyển sang: bản demo hiện tại là bước kiểm chứng ban đầu.

### Slide 6. Bản demo hiện tại là bước kiểm chứng ban đầu

**Thông điệp:** Tuyển sinh + Đào tạo + Tổng hợp đã có luồng chạy; đây là một phần trong phạm vi sáu lĩnh vực.

**Nội dung trên slide:**

- **Đã kiểm chứng** — Giao việc cho hai AI con, phân tích và trả nguồn.
- **Phạm vi dữ liệu** — Văn bản công khai; số liệu nghiệp vụ giả lập.

Ảnh minh họa: `shots/current/welcome-principal.png`.

Ghi chú hiển thị: Demo: proxyllm.store. Giới thiệu luồng trong 1 phút 20 giây; không chờ mọi yêu cầu live hoàn tất.

**Lời thuyết trình:**

Bây giờ mới là phần minh chứng đã làm. Demo trên proxyllm.store có AI Tuyển sinh, AI Đào tạo và AI Tổng hợp. Hai AI con có luồng riêng; AI Tổng hợp giao việc, nhận kết quả rồi phân tích. Hồ sơ mẫu ghi 18 lượt gọi và 4 phút 47 giây. Kho văn bản công khai là thật, số liệu nghiệp vụ vẫn giả lập. Trong phần này em giới thiệu nhanh giao diện, kế hoạch và nguồn; không chờ một lượt live dài hoàn tất. Nếu dùng ảnh dự phòng, đó là kết quả đã lưu. Demo này chứng minh hướng kỹ thuật, còn phạm vi toàn dự án là sáu mảng vừa trình bày.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Chỉ ở phần này mới chuyển từ đích đến dự án sang những gì đã làm. Bản demo có hai AI lĩnh vực Tuyển sinh/Đào tạo và AI Tổng hợp; kho hiện là 106 văn bản công khai, hai SQLite nghiệp vụ giả lập. Hồ sơ đã lưu cho thấy AI Tổng hợp thực sự gọi hai graph con, đợi kết quả rồi phân tích: 18 lượt gọi, 4 phút 47 giây cho một ví dụ. Domain HTTPS đã chạy giao diện và SSE, nhưng đó không phải bằng chứng hệ thống sản xuất đã đủ bảo mật hoặc chất lượng. Dành tối đa 80 giây giới thiệu giao diện và luồng giao việc. Nếu chạy mới chưa xong, chuyển tiếp; dùng ảnh đã lưu ở phụ lục khi cần, nói rõ là kết quả cũ. Không đồng nhất bản demo với toàn bộ sáu lĩnh vực; tiếp theo là phương án để hoàn thành phạm vi đã nêu.

**Căn cứ:** `CONTENT_FACTS.json`; [https://proxyllm.store](https://proxyllm.store); `backend/app/apps.py`

**Chuyển ý:** Từ nội dung này, chuyển sang: ba lựa chọn nơi xử lý model.

### Slide 7. Ba lựa chọn nơi xử lý model

**Thông điệp:** Nơi đặt web/CSDL và nơi suy luận AI có thể khác nhau.

**Nội dung trên slide:**

| Tiêu chí | API trực tiếp | Local tại trường | Lai |
| --- | --- | --- | --- |
| Vốn ban đầu | Thấp; không mua GPU | Máy/GPU, lưu trữ, dự phòng | Có phần hạ tầng local |
| Vận hành model | Nhà cung cấp đảm nhận | Đội trường tự vận hành | Quản cả hai tuyến |
| Dữ liệu prompt | Ra API được duyệt | Ở hạ tầng trường nếu cấu hình kín | Theo chính sách từng tác vụ |
| Đánh đổi | Phụ thuộc mạng / nhà cung cấp | VRAM, tải, bảo trì, chất lượng | Chính sách và tích hợp phức tạp |

**Lời thuyết trình:**

Có ba phương án nơi chạy model. API trực tiếp giúp bắt đầu nhanh, không phải mua GPU, nhưng dữ liệu prompt đi qua dịch vụ ngoài và phụ thuộc mạng, hạn mức. Local tại trường cho quyền kiểm soát nơi xử lý cao hơn, đổi lại cần máy, vận hành và kiểm chứng chất lượng. Phương án lai chọn tuyến theo chính sách dữ liệu. Việc web chạy trên VPS không có nghĩa model đang chạy local; thuê GPU cloud cũng vẫn ở ngoài trường. Lựa chọn phải dựa trên cùng yêu cầu chất lượng, dữ liệu, tải và ngân sách.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Phương án A đặt web và dữ liệu trong môi trường quản lý rồi gọi API OpenAI trực tiếp. Phương án B giữ ứng dụng, dữ liệu và model mở trong hạ tầng của trường. Phương án C là lai: dữ liệu được phép xuất gọi API, phần bắt buộc nội bộ chạy model nội bộ. Cùng một giao diện có thể dùng các tuyến này nhưng phải xây cơ chế chính sách, không chỉ đổi base URL. VPS đang chạy demo không đồng nghĩa model đang chạy local; model hiện được gọi ra gateway qua mạng. GPU cloud thuê theo giờ cũng là hạ tầng ngoài trường, dù tự quản model. Lựa chọn cần dựa trên yêu cầu dữ liệu, ngân sách, năng lực vận hành và chất lượng trên đúng tác vụ của NAU.

**Căn cứ:** [https://developers.openai.com/api/docs/models/compare](https://developers.openai.com/api/docs/models/compare); [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility)

**Chuyển ý:** Từ nội dung này, chuyển sang: api openai: giá và cách tính một yêu cầu.

### Slide 8. API OpenAI: giá và cách tính một yêu cầu

**Thông điệp:** Cộng mọi lời gọi trong một Run; API trực tiếp và giá gateway hiện tại là hai kênh khác nhau.

**Nội dung trên slide:**

| Model / vai trò dự kiến | Input / 1M | Output / 1M | Phạm vi giá |
| --- | --- | --- | --- |
| GPT-6 Sol · Master/review | $2,00 | $10,00 | Standard · short context |
| GPT-6 Luna · Worker | $0,10 | $0,50 | Standard · short context |

Ghi chú hiển thị: Ví dụ tổng Master 20k/2k + Worker 30k/2k → $0,064 ≈ 1.728 đ/Run; tỷ giá giả định 27.000 đ/USD.

**Lời thuyết trình:**

Giá OpenAI API tham khảo ngày 29/9, Standard short context: Sol là 2 đô đầu vào và 10 đô đầu ra trên một triệu token; Luna là 0,1 và 0,5 đô. Một yêu cầu gồm nhiều lời gọi nên phải cộng Master, AI con, review và sửa. Ví dụ tổng Master dùng 20 nghìn token vào, 2 nghìn ra; Worker 30 nghìn vào, 2 nghìn ra thì phí là 0,064 đô, khoảng 1.728 đồng theo tỷ giá dự toán 27.000. Đây là giả định, chưa thuế, tool và retry. Khi dùng API trực tiếp do Trường quản lý phải đo lại trên đúng kênh, không lấy giá gateway làm hóa đơn OpenAI.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Bảng dùng đơn vị USD trên một triệu token, Standard short context, kiểm tra tài liệu OpenAI ngày 29/9/2026. Sol định hướng làm Master/review, Luna làm Worker. Một yêu cầu người dùng gồm nhiều lời gọi nên phải cộng cả AI con và lần sửa. Minh họa Master tổng 20 nghìn token vào, 2 nghìn ra là 0,06 USD; Worker 30 nghìn vào, 2 nghìn ra là 0,004 USD. Tổng 0,064 USD, với tỷ giá dự toán 27.000 là 1.728 đồng. Đây là giả định, không phải trung bình đã đo hay giá cố định mỗi câu. Ngữ cảnh dài, cache, công cụ, thuế và retry phải tính riêng. Demo hiện gọi gateway; triển khai API OpenAI trực tiếp cần tài khoản trường, ánh xạ model và chạy lại kiểm chứng trên đúng kênh.

**Căn cứ:** [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing); [https://developers.openai.com/api/docs/models/compare](https://developers.openai.com/api/docs/models/compare); [https://developers.openai.com/api/docs/models/gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol); `COST_MODEL.json`

**Chuyển ý:** Từ nội dung này, chuyển sang: model local: chủ động dữ liệu, thêm công vận hành.

### Slide 9. Model local: chủ động dữ liệu, thêm công vận hành

**Thông điệp:** Ứng viên Qwen3 + Ollama/vLLM; cần benchmark trên máy thực trước khi mua.

**Nội dung trên slide:**

| Thành phần minh họa | Cách tính | Chi phí |
| --- | --- | --- |
| Máy / GPU trọn bộ | 150 triệu / 36 tháng | 4,17 triệu/tháng phân bổ |
| Công + điện + bảo trì | 2 + 0,5 + 0,5 triệu | 3,00 triệu/tháng |
| Tổng sở hữu quy đổi | 4,17 + 3,00 | 7,17 triệu/tháng |
| Tiền chi năm đầu | 150 + 3 × 12 | 186 triệu |

Ghi chú hiển thị: Thuê thử A40: $0,49/h × 176h × 27.000 ≈ 2,33 triệu; GPU cloud có vị trí/hợp đồng riêng.

**Lời thuyết trình:**

Local có thể thử model trọng số mở như Qwen3 với Ollama hoặc vLLM; không mặc định tải model API về chạy. Cần đo tiếng Việt, nguồn, ngữ cảnh và số người đồng thời trước khi chọn máy. Ví dụ lập ngân sách: máy 150 triệu, phân bổ 36 tháng là 4,17 triệu/tháng; công, điện và bảo trì giả định thêm 3 triệu, tổng 7,17 triệu/tháng. Tiền chi năm đầu là 186 triệu. Đây chưa phải báo giá hay cấu hình đã chốt. Có thể thuê GPU thử trước, nhưng GPU cloud vẫn cần kiểm chính sách dữ liệu và tính thêm phí vận hành.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Có thể chọn Qwen3 8B, 14B hoặc 32B làm ứng viên kiểm chứng, không khẳng định đó là lựa chọn tốt nhất. Đây là model trọng số mở theo giấy phép của họ; không tải model API Sol/Luna về máy để chạy. Ollama giúp thử nhanh, vLLM có thể dùng làm máy chủ phục vụ, đều cần kiểm thử tích hợp. Model lượng tử hóa nhỏ hơn nhưng RAM/VRAM còn phải chứa cache ngữ cảnh và phiên đồng thời; dung lượng tệp không bằng tổng bộ nhớ vận hành. Bắt đầu một phiên và ngữ cảnh vừa phải rồi đo lên. VPS 2 GB RAM hiện tại chỉ chạy app gọi API, chưa có máy phục vụ model local được xác minh. Giả định máy trọn bộ 150 triệu đồng và dùng 36 tháng. Phân bổ vốn theo tháng là 4,17 triệu; vận hành giả định 3 triệu/tháng gồm công người 2 triệu, điện/làm mát 0,5 triệu và bảo trì 0,5 triệu. Tổng quy đổi 7,17 triệu/tháng. Dòng tiền năm đầu là 150 cộng 36, tức 186 triệu, khác với chi phí phân bổ năm là 86 triệu. Chưa tính phát triển app, nhập dữ liệu, bảo mật bổ sung, thuế, vốn và máy dự phòng. Để thử trước khi mua, giá A40 48 GB trên Runpod được tham khảo ở 0,49 USD/giờ; 176 giờ khoảng 2,33 triệu theo tỷ giá 27.000, chưa storage và công vận hành. Đây là GPU cloud, không phải dữ liệu được giữ tại trường.

**Căn cứ:** [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility); [https://www.runpod.io/pricing](https://www.runpod.io/pricing); `LOCAL_OPTIONS_RESEARCH.md`; `COST_MODEL.json`

**Chuyển ý:** Từ nội dung này, chuyển sang: phương án chọn: api trước, local theo yêu cầu dữ liệu.

### Slide 10. Phương án chọn: API trước, local theo yêu cầu dữ liệu

**Thông điệp:** Chọn tuyến theo chính sách dữ liệu; không chuyển cloud chỉ vì model local gặp lỗi.

**Nội dung trên slide:**

- **Dữ liệu được phép xuất** — API trực tiếp, tài khoản do Trường quản lý.
- **Bắt buộc giữ nội bộ** — Model local + truy vấn/nguồn trong vùng kiểm soát.
- **Điều phối xuyên suốt** — Cả Master, AI con, review và tổng hợp tuân chính sách.
- **Khi xảy ra lỗi** — Local-only không tự fallback ra API ngoài.

Ghi chú hiển thị: Minh họa 5.000 Run/tháng: API 8,64 triệu; local phân bổ 7,17 triệu nếu đủ tải/cùng chất lượng — chưa đo.

**Lời thuyết trình:**

Đề xuất bắt đầu bằng API cho dữ liệu được phép gửi và benchmark local cho việc bắt buộc nội bộ. Minh họa 5.000 yêu cầu/tháng theo giả định vừa nêu: API khoảng 8,64 triệu; local phân bổ 7,17 triệu nếu đủ tải và cùng chất lượng, điều này chưa được đo. Do đó chưa thể kết luận mua máy rẻ hơn. Với phương án lai, chính sách phải theo cả Master, AI con, review và tổng hợp. Nếu việc chỉ được xử lý nội bộ gặp lỗi, phải dừng hoặc dùng model nội bộ khác; không tự gửi cloud.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Phương án đề xuất là dùng API trực tiếp để thử các việc có nguồn được phép gửi, đồng thời benchmark model local cho việc có yêu cầu giữ nội bộ. Khi triển khai lai, tác vụ được gắn nhãn chính sách ngay từ lúc nhận yêu cầu. Chính sách phải đi qua AI con, bước nghiệm thu, model dự phòng và AI Tổng hợp. Một kết quả AI con dù chỉ là tóm tắt vẫn có thể chứa dữ liệu hạn chế nên không được tự coi là công khai. Nếu tác vụ local-only gặp lỗi, hệ thống chờ, dừng hoặc dùng model nội bộ khác đã duyệt; không tự gửi sang cloud. Bản demo chưa có cổng định tuyến theo độ nhạy này. Thử nghiệm phải chứng minh cả chất lượng lẫn đường đi dữ liệu. Với cùng mô hình chi phí, 5.000 Run/tháng giả định API là 8,64 triệu, local phân bổ là 7,17 triệu. Không dùng so sánh này để kết luận mua máy ngay vì chưa có số đo công suất và chất lượng local. Chi phí, kỹ năng vận hành và yêu cầu giữ dữ liệu quyết định tuyến triển khai. Biểu đồ ba mức tải được đưa sang phụ lục để giữ thời lượng bài chính.

**Căn cứ:** `backend/app/llm.py`; `backend/app/web.py`; `SECURITY_BENEFITS_DRAFT.md`

**Chuyển ý:** Từ nội dung này, chuyển sang: phân loại thông tin trước khi chọn tuyến ai.

### Slide 11. Phân loại thông tin trước khi chọn tuyến AI

**Thông điệp:** Đơn vị sở hữu dữ liệu quyết định ai được xem, được tổng hợp và được gửi đi.

**Nội dung trên slide:**

| Mức đề xuất | Ví dụ | Nguyên tắc xử lý |
| --- | --- | --- |
| Công khai | Quy chế, thông báo đã công bố | API được duyệt; kiểm phiên bản |
| Nội bộ | Thống kê vận hành chưa công bố | Theo quyền và danh mục được phép xuất |
| Hạn chế / nhạy cảm | Hồ sơ, điểm, liên hệ, nhân sự | Giữ nội bộ khi chính sách yêu cầu |
| Mọi mức | Câu hỏi, log, báo cáo và CSV | Cùng chính sách truy cập và thời hạn lưu |

Ghi chú hiển thị: Phân loại là đề xuất quản trị dữ liệu; phải được đơn vị chủ dữ liệu xác nhận.

**Lời thuyết trình:**

Trường cần phân loại dữ liệu trước: công khai, nội bộ và hạn chế/nhạy cảm. Quy chế công khai có thể dùng API được duyệt; thống kê nội bộ cần quyền và danh mục được phép xuất; hồ sơ, điểm, nhân sự hạn chế phải theo tuyến nội bộ khi chính sách yêu cầu. Câu hỏi, báo cáo, CSV và log cũng áp dụng cùng quyền và hạn lưu. Không thể kết luận an toàn chỉ vì database đặt trong trường hoặc đã bỏ cột họ tên.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Nhóm đề xuất ba mức phân loại do Nhà trường phê duyệt. Công khai là quy chế và thông báo đã công bố; nội bộ là chỉ tiêu, thống kê vận hành chưa công bố; hạn chế là hồ sơ cá nhân, điểm, liên hệ hoặc nhân sự. Phân loại theo từng trường dữ liệu và mục đích sử dụng, không chỉ theo thư mục. Với nội bộ, cần quyết định phần nào được xuất ra nhà cung cấp và phần nào phải xử lý trong trường. Việc lưu CSDL trên VPS hay trong trường không tự quyết định prompt có rời đi không. Bộ duyệt nguồn cũng phải ghi chủ sở hữu, ngày hiệu lực, người được phép và thời hạn lưu. Đây là kế hoạch, chưa phải ma trận quyền đã được Trường ban hành.

**Căn cứ:** `DATA_PLAN.md`; `SECURITY_BENEFITS_DRAFT.md`

**Chuyển ý:** Từ nội dung này, chuyển sang: bảo mật: từ cài đặt đến dữ liệu nghiệp vụ.

### Slide 12. Bảo mật: từ cài đặt đến dữ liệu nghiệp vụ

**Thông điệp:** Mật khẩu cài đặt đã có; quyền đọc/xuất dữ liệu theo người dùng vẫn phải bổ sung.

**Nội dung trên slide:**

| Lớp | Việc cần thực hiện | Bằng chứng nghiệm thu |
| --- | --- | --- |
| Danh tính / quyền | SSO, vai trò; kiểm API, nguồn, CSV | Thử cho phép/từ chối/thu hồi |
| Dữ liệu gửi model | Lọc câu hỏi, log, nhóm nhỏ; local-only | Không lộ PII hoặc đi sai tuyến |
| Hạ tầng / bí mật | TLS, CSDL riêng, key, hạn mức | Kiểm cổng, quyền và thu hồi key |
| Vận hành | Log có hạn lưu; backup mã hóa; restore | Diễn tập sự cố và khôi phục |

Ghi chú hiển thị: Đề xuất pilot; hiện chưa có phân quyền hỏi đáp theo người dùng. Chi tiết chính sách API ở phụ lục A5.

**Lời thuyết trình:**

Bản demo đã có HTTPS và mật khẩu cài đặt, nhưng hệ thống hoàn chỉnh phải có xác thực người dùng và kiểm quyền tại backend cho mọi nguồn, lịch sử và xuất CSV. Phải kiểm dữ liệu ở cả câu hỏi, văn bản, báo cáo, log và các nhóm nhỏ có thể suy ra cá nhân. Chính sách lưu giữ của API cần được rà theo hợp đồng; không dùng huấn luyện mặc định không đồng nghĩa không lưu log. Hạ tầng cần quản khóa, giới hạn sử dụng, backup mã hóa và thử phục hồi. Mỗi lớp có người phụ trách, test và bằng chứng nghiệm thu trước khi dùng hồ sơ thật.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Bản demo có HTTPS và mật khẩu bảo vệ API cấu hình, nhưng không có đăng nhập nghiệp vụ cho từng phòng ban. Tab Hiệu trưởng không xác minh chức danh. Pilot cần SSO, vai trò và kiểm quyền ngay tại backend cho hỏi đáp, nguồn, lịch sử, SSE và tải CSV. Code đã tách hàng cá nhân trong truy vấn, nhưng câu hỏi, văn bản, báo cáo và log vẫn cần kiểm; tổng hợp nhóm nhỏ vẫn có thể làm lộ người. Với API OpenAI, không dùng dữ liệu huấn luyện mặc định không đồng nghĩa không giữ log: điều kiện lưu giữ và ZDR phải kiểm theo hợp đồng/endpoint. Với local-only, mọi bước kể cả review và dự phòng phải ở tuyến nội bộ. Vận hành cần quản key, hạn mức, log có hạn lưu và backup phục hồi được; giao phòng CNTT chịu trách nhiệm.

**Căn cứ:** `backend/app/settings_auth.py`; `backend/app/web.py`; `SECURITY_BENEFITS_DRAFT.md`; [https://developers.openai.com/api/docs/guides/your-data](https://developers.openai.com/api/docs/guides/your-data)

**Chuyển ý:** Từ nội dung này, chuyển sang: lộ trình hoàn thành toàn dự án theo từng giai đoạn.

### Slide 13. Lộ trình hoàn thành toàn dự án theo từng giai đoạn

**Thông điệp:** Xây lõi dùng chung, nghiệm thu lĩnh vực ưu tiên, pilot có kiểm soát rồi hoàn thiện đủ sáu lĩnh vực.

**Nội dung trên slide:**

| Giai đoạn | Phạm vi công việc | Điều kiện chuyển bước |
| --- | --- | --- |
| 1 · Chốt toàn bộ bài toán | Nguồn/quyền/đầu ra cho sáu lĩnh vực | Đầu mối và yêu cầu được duyệt |
| 2 · Lõi và MVP ưu tiên | Đào tạo, NCKH, HTQT theo đề bài; kế thừa demo | Điều phối, dữ liệu, quyền đạt test |
| 3 · Pilot có kiểm soát | Phạm vi nhỏ; API/local, backup, câu mới | Chất lượng và vận hành đạt |
| 4 · Đủ sáu lĩnh vực | Tuyển sinh đầy đủ; Nhân sự và Hành chính | Từng lĩnh vực có nguồn, quyền, nghiệm thu |

Ghi chú hiển thị: 12 tuần là khung đề xuất giai đoạn đầu/pilot, không cam kết hoàn thành toàn trường trong 12 tuần.

**Lời thuyết trình:**

Lộ trình dẫn tới toàn bộ dự án qua bốn giai đoạn. Đầu tiên chốt công việc, nguồn, quyền và đầu ra của sáu lĩnh vực. Tiếp theo xây lõi dùng chung và MVP ưu tiên Đào tạo, NCKH, HTQT theo đề bài, kế thừa demo đã có. Sau đó pilot phạm vi nhỏ trong khung đề xuất tháng 10–12, kiểm chất lượng, API/local và vận hành. Cuối cùng hoàn thiện Tuyển sinh, Nhân sự, Hành chính và các báo cáo liên lĩnh vực, mở rộng từng phần khi có đủ nguồn và quyền. Mười hai tuần là khung giai đoạn đầu, không phải cam kết làm xong toàn trường. Mỗi bước chỉ chuyển tiếp khi đạt điều kiện nghiệm thu.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Lộ trình phải dẫn tới phạm vi toàn dự án. Giai đoạn một khảo sát nhu cầu, vai trò, nguồn và sản phẩm đầu ra cho sáu lĩnh vực, dù chưa triển khai tất cả cùng lúc. Giai đoạn hai làm lõi điều phối, dữ liệu, quyền, lưu trạng thái và kiểm thử; ưu tiên ba lĩnh vực Đào tạo/NCKH/HTQT theo đề bài gốc, kế thừa kết quả demo Tuyển sinh/Đào tạo. Giai đoạn ba pilot giới hạn theo điều kiện dữ liệu, nhân sự và hạ tầng trong khung đề xuất tháng 10–12/2026. Giai đoạn bốn hoàn thiện Tuyển sinh, Nhân sự và Hành chính cùng báo cáo liên lĩnh vực, triển khai lần lượt khi có chủ dữ liệu và bộ nghiệm thu. Khung 12 tuần không phải lời hứa hoàn thành sáu lĩnh vực hoặc toàn trường. Mỗi bước cần người phụ trách, dữ liệu được phép và tiêu chí chất lượng/quyền. Cần chốt lịch cụ thể sau khảo sát với Nhà trường.

**Căn cứ:** `PLAN.md: Phạm vi Worker, M-1 đến M6, Pilot`; `Bài toán.docx`; `DATA_PLAN.md`

**Chuyển ý:** Từ nội dung này, chuyển sang: bàn giao một hệ thống có thể sử dụng và vận hành.

### Slide 14. Bàn giao một hệ thống có thể sử dụng và vận hành

**Thông điệp:** Không chỉ giao một chatbot: bàn giao ứng dụng, nguồn/công cụ, cơ chế quản trị và bằng chứng nghiệm thu.

**Nội dung trên slide:**

- **Ứng dụng nghiệp vụ** — Trợ lý theo vai trò; kế hoạch, bằng chứng, lịch sử và xuất báo cáo.
- **Nguồn và tích hợp** — Dữ liệu có phiên bản/quyền; truy vấn, công cụ và cập nhật.
- **Quản trị và vận hành** — Model/hạn mức, đăng nhập, backup, phục hồi và hướng dẫn.
- **Nghiệm thu và chuyển giao** — Test từng lĩnh vực/liên phòng; đo lợi ích; đào tạo người vận hành.

Ghi chú hiển thị: Đơn vị sở hữu dữ liệu xác nhận nguồn; CNTT vận hành; nhóm phát triển tích hợp; người có thẩm quyền nghiệm thu.

**Lời thuyết trình:**

Khi hoàn thành, nhóm bàn giao một hệ thống vận hành được: ứng dụng theo vai trò; nguồn và truy vấn có phiên bản/quyền; các AI lĩnh vực và cơ chế điều phối; lịch sử, bằng chứng và xuất báo cáo; cấu hình, hạn mức, backup và tài liệu chuyển giao. Nghiệm thu bằng câu mới do cán bộ chấm, kiểm quyền và lỗi, đo cả thời gian sửa và chi phí để hoàn thành công việc. Đơn vị chủ dữ liệu xác nhận nguồn, CNTT nhận vận hành, nhóm phát triển tích hợp và người có thẩm quyền duyệt. Đích đến không chỉ là một cửa sổ chat hay bản trình diễn.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Sản phẩm bàn giao toàn dự án gồm mã nguồn và cấu hình có phiên bản; giao diện hỏi đáp, theo dõi kế hoạch/tác vụ, mở bằng chứng, lịch sử và xuất báo cáo; các AI lĩnh vực với registry, schema, công cụ và bộ câu hỏi riêng; kho tài liệu/dữ liệu có chủ sở hữu, quyền, phiên bản và cơ chế cập nhật; hệ thống đăng nhập/quản trị, hạn mức model và nhật ký; tài liệu triển khai, sao lưu/phục hồi và chuyển giao. Chất lượng kiểm bằng câu mới, người chuyên môn chấm nguồn/số/suy luận; kiểm thử sai quyền, lỗi và phục hồi. Giá trị so với người tự làm phải tính tới bản báo cáo được chấp nhận, gồm công sửa. Không mặc định mọi output do AI tạo đều được tự động ban hành hoặc ghi vào CSDL trường. Đơn vị chủ dữ liệu duyệt nguồn, CNTT nhận vận hành, nhóm phát triển sửa lỗi và người có thẩm quyền duyệt nghiệm thu.

**Căn cứ:** `PLAN.md: Bàn giao, Giao diện, Tiêu chí kiểm tra`; `Bài toán.docx: FR/NFR`

**Chuyển ý:** Từ nội dung này, chuyển sang: đích đến: trợ lý phối hợp cho mọi mảng công việc của trường.

### Slide 15. Đích đến: trợ lý phối hợp cho mọi mảng công việc của trường

**Thông điệp:** Phê duyệt phạm vi toàn dự án, chọn giai đoạn ưu tiên và nghiệm thu trước mỗi lần mở rộng.

**Nội dung trên slide:**

- **Phạm vi** — Sáu lĩnh vực nghiệp vụ và báo cáo phối hợp cho lãnh đạo.
- **Dữ liệu / con người** — Mỗi đơn vị có đầu mối, nguồn được duyệt và quyền rõ.
- **Hạ tầng / ngân sách** — Chọn API/local theo chất lượng, chi phí và chính sách.
- **Triển khai** — Bàn giao từng giai đoạn; đo giá trị rồi mở rộng.

**Lời thuyết trình:**

Credere sẽ là hệ thống trợ lý phối hợp cho sáu lĩnh vực của toàn trường, tạo báo cáo và kế hoạch có bằng chứng. Đề nghị Nhà trường chốt phạm vi và giai đoạn ưu tiên, cử đầu mối từng mảng, duyệt dữ liệu/quyền, hạ tầng và ngân sách thử. Nhóm sẽ bàn giao từng giai đoạn, đo được giá trị rồi mở rộng. Bản demo hôm nay là bước khởi đầu của mục tiêu đó. Em xin cảm ơn quý thầy cô.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Đích đến của Credere là hệ thống trợ lý dùng chung cho toàn trường với sáu lĩnh vực, có khả năng phối hợp để trả báo cáo và kế hoạch có bằng chứng. Bản demo chỉ chứng minh một phần cơ chế để tiến tới mục tiêu đó. Đề nghị Nhà trường phê duyệt phạm vi và thứ tự ưu tiên, cử đầu mối từng lĩnh vực, xác nhận dữ liệu/quyền và người vận hành; chốt ngân sách theo phương án API/local và tiêu chí nghiệm thu. Kết quả được bàn giao từng giai đoạn, chỉ mở rộng khi chất lượng, quyền và vận hành đạt điều kiện. Không thu hẹp toàn dự án thành hai AI đang có, cũng không tuyên bố toàn bộ phạm vi tương lai đã chạy.

**Căn cứ:** `yeucauslide.txt`; `PLAN.md`; `COST_MODEL.json`

### Slide 16. A1 · So chi phí ở ba mức tải giả định

**Thông điệp:** Bảng chỉ so phần suy luận AI; chưa chứng minh máy local đạt cùng chất lượng và công suất.

**Nội dung trên slide:**

| Tải/tháng | API giả định | Local giả định |
| --- | --- | --- |
| 1.000 | 1,73 triệu | 7,17 triệu |
| 5.000 | 8,64 triệu | 7,17 triệu |
| 20.000 | 34,56 triệu | 7,17 triệu |

Ghi chú hiển thị: Local ở các tải trên chưa được benchmark. Phải so chi phí trên công việc được chấp nhận, không chỉ giá token.

**Lời thuyết trình:**

So ba mức tải với phí API giả định 1.728 đồng/yêu cầu và local phân bổ 7,17 triệu/tháng. API tăng theo số yêu cầu, local có phần cố định. Ở 1.000 yêu cầu, API khoảng 1,73 triệu; 5.000 là 8,64 triệu; 20.000 là 34,56 triệu. Local giữ 7,17 chỉ với giả định một máy vẫn phục vụ được tải đó trong giờ vận hành và đạt cùng chất lượng. Nếu phải thêm GPU, chạy dài giờ hoặc rà soát nhiều hơn, chi phí thay đổi. Điểm hai đường bằng nhau khoảng 4.147 yêu cầu/tháng chỉ là giao điểm mô hình, không phải điểm hòa vốn đã nghiệm thu. Chưa gồm phần hạ tầng, nhân công ứng dụng chung và chi phí rủi ro.

**Căn cứ:** `COST_MODEL.json`; [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)

### Slide 17. A2 · Ứng viên và cấu hình thử model local

**Thông điệp:** Local tăng quyền kiểm soát nơi xử lý; không tự động bảo đảm chất lượng hay an toàn.

**Nội dung trên slide:**

| Ứng viên | Mốc thử ban đầu* | Lợi ích / đánh đổi |
| --- | --- | --- |
| Qwen3-8B | GPU 16–24 GB | Nhẹ hơn; phải thử độ đúng và tiếng Việt |
| Qwen3-14B | GPU 24 GB | Thử Worker và Master, theo ngữ cảnh |
| Qwen3-32B | GPU 48 GB | Tốn bộ nhớ hơn; chưa đo năng lực phục vụ |
| Ollama / vLLM | API tương thích để tích hợp | Không bảo đảm cùng chất lượng với API |

Ghi chú hiển thị: *VRAM là ước lượng để chọn bài thử, không phải cam kết cấu hình. Đo KV cache và số phiên trước khi mua.

**Lời thuyết trình:**

Có thể chọn Qwen3 8B, 14B hoặc 32B làm ứng viên kiểm chứng, không khẳng định đó là lựa chọn tốt nhất. Đây là model trọng số mở theo giấy phép của họ; không tải model API Sol/Luna về máy để chạy. Ollama giúp thử nhanh, vLLM có thể dùng làm máy chủ phục vụ, đều cần kiểm thử tích hợp. Model lượng tử hóa nhỏ hơn nhưng RAM/VRAM còn phải chứa cache ngữ cảnh và phiên đồng thời; dung lượng tệp không bằng tổng bộ nhớ vận hành. Bắt đầu một phiên và ngữ cảnh vừa phải rồi đo lên. VPS 2 GB RAM hiện tại chỉ chạy app gọi API, chưa có máy phục vụ model local được xác minh.

**Căn cứ:** [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility); [https://huggingface.co/Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B); `LOCAL_OPTIONS_RESEARCH.md`

### Slide 18. A3 · Giả định và phép tính chi phí

**Thông điệp:** Thay giả định bằng số đo thực tế và báo giá trước khi quyết định ngân sách.

**Nội dung trên slide:**

| Khoản | Giả định | Kết quả |
| --- | --- | --- |
| Master | 20k vào × $2 + 2k ra × $10 | 0,060 USD |
| Worker | 30k vào × $0,1 + 2k ra × $0,5 | 0,004 USD |
| Toàn Run | 0,064 USD × 27.000 đ/USD | 1.728 đ |
| Local | 150 triệu / 36 + 3 triệu | 7,167 triệu/tháng |

**Lời thuyết trình:**

Công thức API: tổng trên từng model của token vào nhân giá vào cộng token ra nhân giá ra, chia một triệu; cộng công cụ, storage, lỗi và thử lại nếu có. Kịch bản này Master: (20.000×2 + 2.000×10)/1.000.000=0,06 USD. Worker: (30.000×0,1 + 2.000×0,5)/1.000.000=0,004 USD. Tổng 0,064 USD, nhân 27.000=1.728 đồng. Local: 150.000.000/36 + 3.000.000=7.166.667 đồng/tháng. Giao điểm giả định 7.166.667/1.728≈4.147 yêu cầu/tháng. Local 36 tháng chi 150+3×36=258 triệu. Các công thức chỉ công bằng khi cùng chất lượng/công suất và phạm vi chi phí; chưa gồm phần dùng chung và thuế. Giá phần cứng 150 triệu chưa có cấu hình/báo giá kèm theo nên tuyệt đối không trình bày là gói mua được chốt.

**Căn cứ:** [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing); `COST_MODEL.json`

### Slide 19. A4 · Kết quả nội bộ và giới hạn bộ chấm

**Thông điệp:** Kiểm thử phần mềm và đánh giá chất lượng nghiệp vụ là hai loại bằng chứng khác nhau.

**Nội dung trên slide:**

| Bằng chứng | Kết quả ghi nhận | Ý nghĩa / giới hạn |
| --- | --- | --- |
| Test phần mềm | 159 test đạt | Luồng và ràng buộc; model giả lập |
| Văn bản Tuyển sinh | 30/30 | Bộ nội bộ có đáp án |
| Dữ liệu Tuyển sinh | 14/14 | CSDL giả lập |
| Đào tạo / Tổng hợp | 10/10 và 4/4 | Mẫu nhỏ, chưa nghiệm thu độc lập |

**Lời thuyết trình:**

159 test phần mềm đã qua trước khi triển khai, kiểm tra điều phối, schema, lỗi, truy vấn và cổng mật khẩu. Không diễn giải thành 159 câu nghiệp vụ được model thật trả lời đúng. Các tệp đánh giá đã lưu gồm 30/30 văn bản Tuyển sinh, 14/14 dữ liệu Tuyển sinh giả lập, 10/10 Đào tạo và 4/4 Tổng hợp. Đây là bộ thử nội bộ đã sử dụng trong phát triển; bộ chấm còn thiên về sự xuất hiện của số và mã nguồn nên có thể bỏ lọt lỗi diễn giải. Cần thêm người chuyên môn chấm mù, câu mới, dữ liệu mâu thuẫn và trường hợp thiếu nguồn. Bộ đo ngữ cảnh dài trước đó bão hòa nên cũng không dùng làm chứng cứ rằng model sẽ luôn đúng.

**Căn cứ:** `CONTENT_FACTS.json:limited_evaluations`; `CONTENT_FACTS.json:software_verification`

### Slide 20. A5 · Chính sách dữ liệu của OpenAI API

**Thông điệp:** Không dùng dữ liệu để huấn luyện không đồng nghĩa không lưu giữ.

**Nội dung trên slide:**

- **Huấn luyện** — API không dùng để huấn luyện mặc định, trừ khi opt-in.
- **Lưu giữ** — Log mặc định có thể đến 30 ngày; endpoint có trạng thái riêng.
- **ZDR** — Cần phê duyệt, có điều kiện và giới hạn tính năng.
- **Trước khi dùng** — Duyệt nhà cung cấp, hợp đồng, vùng xử lý và loại dữ liệu.

Ghi chú hiển thị: Nguồn OpenAI API kiểm tra 29/09/2026; không áp dụng thay cho chính sách gateway khác.

**Lời thuyết trình:**

Theo tài liệu OpenAI API đã kiểm tra, dữ liệu API mặc định không dùng để huấn luyện trừ khi khách hàng chọn chia sẻ. Log giám sát lạm dụng mặc định có thể giữ tối đa 30 ngày, có ngoại lệ; trạng thái ứng dụng phụ thuộc endpoint. Zero Data Retention cần được phê duyệt và có giới hạn theo tính năng. Vì vậy Trường cần rà soát hợp đồng, nơi xử lý và điều kiện endpoint, thay vì chỉ đọc một dòng về huấn luyện. Các chính sách này áp dụng cho dịch vụ OpenAI được tài liệu mô tả, không tự mở rộng sang gateway trung gian. Nếu yêu cầu dữ liệu tuyệt đối không ra ngoài, cả chuỗi xử lý phải ở nội bộ hoặc chỉ xuất bản tổng hợp đã được cho phép.

**Căn cứ:** [https://developers.openai.com/api/docs/guides/your-data](https://developers.openai.com/api/docs/guides/your-data)

### Slide 21. A6 · Kiểm soát toàn bộ luồng dữ liệu

**Thông điệp:** Tổng hợp số liệu giảm phơi bày, nhưng không tự động bảo đảm ẩn danh.

**Nội dung trên slide:**

- **Đã có trong truy vấn** — Danh sách cá nhân tách khỏi đầu vào model; CSDL chỉ đọc.
- **Cần thêm** — Kiểm câu hỏi, nguồn, tham số, báo cáo, log và bản ghi.
- **Chống suy danh tính** — Nhóm nhỏ, suy từ tổng và chuỗi truy vấn; ngưỡng phải duyệt.
- **Chống chèn chỉ dẫn** — Tài liệu không được cấp quyền/công cụ; có bộ thử tấn công.

**Lời thuyết trình:**

Code hiện tách hàng cá nhân khỏi payload của các truy vấn gắn nhãn cá nhân; model nhận số lượng và tổng hợp, bảng chi tiết đi tới trình duyệt. Tuy nhiên người dùng có thể gõ tên hoặc điện thoại vào câu hỏi, nguồn văn bản có thể chứa thông tin đó, và log có thể giữ lại. Cần kiểm soát mọi đường này, không chỉ xóa cột họ tên. Nhóm nhỏ có thể làm suy ra cá nhân; ngưỡng ví dụ dưới 5 người cần được cân nhắc cùng khả năng suy ngược từ tổng và nhiều truy vấn liên tiếp. Nội dung tài liệu phải được coi là dữ liệu, không được thay quyền hay cho phép công cụ. Cần thử prompt injection, xuất dữ liệu trái phép và kết quả AI con làm lộ thông tin ở bước tổng hợp.

**Căn cứ:** `backend/app/tools/data.py`; `backend/app/workers.py`; `backend/app/web.py`; `SECURITY_BENEFITS_DRAFT.md`

### Slide 22. A7 · Ảnh kết quả Tổng hợp để dự phòng

**Thông điệp:** Ảnh của lượt chạy đã lưu; không phải kết quả vừa gọi AI trong buổi trình bày.

**Nội dung trên slide:**


Ảnh minh họa: `shots/current/answer-principal.png`.

**Lời thuyết trình:**

Dùng phụ lục khi mạng, model hoặc thời gian không cho phép demo live. Nói rõ ảnh chụp giao diện đang hiển thị bản ghi 29/9/2026. Câu hỏi cần hai lĩnh vực, bảng chỉ số có nguồn và phần lưu ý về mẫu số. Nhãn giả lập phải được đọc rõ. Có thể đối chiếu với slide 10 để giải thích T1/T2/T3. Không dùng con số hiển thị để nhận định tình hình thật của Trường. Nếu người nghe hỏi độ đúng, chỉ ra đây là kết quả hệ thống đã nghiệm thu và còn cần kiểm tra chuyên môn; đừng trả lời rằng 3/3 task đạt nghĩa là mọi phát biểu đã được kiểm chứng độc lập.

**Căn cứ:** `shots/current/screenshots.json`; `CONTENT_FACTS.json:principal_example`

### Slide 23. A8 · Đối chiếu yêu cầu và nguồn tham khảo

**Thông điệp:** Mọi ý trong yeucauslide.txt có mục riêng; lời nói chi tiết nằm trong Notes và tài liệu kèm.

**Nội dung trên slide:**

| Nội dung bắt buộc | Căn cứ |
| --- | --- |
| Tổng thể / cơ chế / lợi ích | Code, PLAN, hồ sơ chạy; cách đo đề xuất |
| Triển khai / kế hoạch | VPS hiện tại + giai đoạn có điều kiện |
| API / local / chi phí | Tài liệu chính thức + giả định hiển thị |
| Bảo mật thông tin | Code hiện tại + phương án pilot có kiểm thử |

**Lời thuyết trình:**

Nguồn ưu tiên là code đang chạy và dữ liệu API /api/apps, sau đó hồ sơ chạy đã lưu và tài liệu chính thức nhà cung cấp. Các yêu cầu trong yeucauslide.txt được ánh xạ tự động tới slide trong DOI_CHIEU_YEU_CAU.md. Các giá OpenAI, chính sách dữ liệu, ứng viên Qwen/Ollama và giá GPU thuê có URL ở Notes và NGUON_THAM_KHAO.md, kiểm tra ngày 29/9. Dự toán được ghi trong COST_MODEL.json để thay tham số. Bộ slide chỉnh sửa được, lời nói có trong PowerPoint và bản Markdown/HTML. Không đưa mật khẩu, khóa API hoặc thông tin SSH vào bài. Bản này thay trọng tâm demo ngắn bằng cái nhìn chi tiết toàn dự án theo yêu cầu mới.

**Căn cứ:** [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing); [https://developers.openai.com/api/docs/models/compare](https://developers.openai.com/api/docs/models/compare); [https://developers.openai.com/api/docs/guides/your-data](https://developers.openai.com/api/docs/guides/your-data); [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility); [https://www.runpod.io/pricing](https://www.runpod.io/pricing); `CONTENT_FACTS.json`; `yeucauslide.txt`

## Chuẩn bị và trình diễn

1. Mở slide, bật Presenter View để thấy Notes; dùng bản PDF nếu thiếu PowerPoint.
2. Mở https://proxyllm.store, kiểm ba trợ lý, nhãn giả lập, kho nguồn; không nhập thông tin cá nhân thật.
3. Chuẩn bị đúng một câu liên lĩnh vực. Câu nhập tay/gợi ý gọi API mới và có phí; không bấm nhiều lần.
4. Giới hạn giới thiệu demo ở 1:20; nếu chưa xong thì tiếp tục slide. Dùng phụ lục ảnh kết quả và công khai đó là lượt đã lưu.
5. Không mở file chứa khóa/mật khẩu trên màn hình chiếu. Trang cài đặt vẫn yêu cầu mật khẩu riêng.
6. Phần hỏi đáp ngoài 15 phút có thể mở phụ lục cấu hình local, phép tính chi phí và chính sách dữ liệu.

## Giải thích mức tin cậy

- **Đã có/đã đo:** code, inventory public domain và các bản ghi/tệp test đã được kiểm tra trong phiên này hoặc phiên trước, ghi rõ phạm vi.
- **Giá tham khảo:** nguồn chính thức có ngày; không thay báo giá/hóa đơn của nhà cung cấp hoặc cổng trung gian.
- **Giả định dự toán:** token/Run, tải tháng, tỷ giá 27.000, máy 150 triệu và vận hành 3 triệu; thay được trong COST_MODEL.json.
- **Đề xuất pilot:** phân quyền, policy local-only, phục hồi, lịch 12 tuần và ngưỡng nghiệm thu; chưa phải toàn bộ đã triển khai.
