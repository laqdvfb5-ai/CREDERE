# Nội dung chi tiết bài thuyết trình Credere — 15 phút

Theo đủ nội dung trong `yeucauslide.txt`. Bản chính **15 slide, tổng 15 phút**; 8 slide phụ lục chỉ mở khi hỏi đáp và được ẩn khỏi lượt trình chiếu thông thường. Mỗi slide có nội dung trình chiếu và lời nói đầy đủ dưới đây.

**Thời lượng:** bao gồm 2 phút 30 giây trình diễn. Nếu yêu cầu live chưa xong, chuyển tiếp; ảnh phụ lục là kết quả đã lưu, phải nói rõ.

**Ngày đối chiếu:** 29/09/2026. **Demo:** https://proxyllm.store. Các tệp này không chứa mật khẩu, API key hay thông tin SSH.

## Đối chiếu yêu cầu

| Yêu cầu | Slide chính | Chi tiết phụ lục |
| --- | --- | --- |
| Tổng thể toàn bộ dự án | 1, 3, 5, 15 | 16, 19, 23 |
| Cách hệ thống hoạt động | 3, 4, 5 | 22, 23 |
| Lợi ích so với quy trình con người tự làm | 2, 14 | 19, 23 |
| Phương án và kế hoạch triển khai dự án | 3, 5, 6, 10, 12, 13, 14, 15 | 16, 17, 19, 23 |
| OpenAI API / model local: giá, lợi ích và bất lợi | 6, 7, 8, 9, 10, 14, 15 | 17, 18, 20, 23 |
| Phương án bảo mật thông tin nhà trường | 10, 11, 12, 14, 15 | 20, 21, 23 |

## Phân bổ thời gian

| Slide | Chủ đề | Thời lượng | Mốc kết thúc |
| --- | --- | --- | --- |
| 1 | Credere: một nền tảng, nhiều trợ lý AI | 0:40 | 0:40 |
| 2 | Con người tự làm và có Credere hỗ trợ | 0:55 | 1:35 |
| 3 | Kiến trúc toàn bộ hệ thống | 0:50 | 2:25 |
| 4 | AI Hiệu trưởng giao việc thật cho AI con | 1:05 | 3:30 |
| 5 | Trình diễn trên tên miền đã triển khai | 2:30 | 6:00 |
| 6 | Ba lựa chọn nơi xử lý model | 1:00 | 7:00 |
| 7 | API OpenAI: giá và cách tính một yêu cầu | 1:10 | 8:10 |
| 8 | Model local: chủ động dữ liệu, thêm công vận hành | 1:10 | 9:20 |
| 9 | So chi phí công bằng: cùng tải, cùng chất lượng | 0:45 | 10:05 |
| 10 | Phương án C: kết hợp API và model nội bộ | 0:45 | 10:50 |
| 11 | Phân loại thông tin trước khi chọn tuyến AI | 0:45 | 11:35 |
| 12 | Bảo mật: từ cài đặt đến dữ liệu nghiệp vụ | 1:00 | 12:35 |
| 13 | Kế hoạch đề xuất trong 12 tuần | 1:05 | 13:40 |
| 14 | Nghiệm thu bằng công việc thật và người phụ trách | 0:45 | 14:25 |
| 15 | Đề xuất lựa chọn và các quyết định cần chốt | 0:35 | 15:00 |

## Nội dung và lời nói

### Slide 1. Credere: một nền tảng, nhiều trợ lý AI

**Thông điệp:** Tổng thể dự án · cách hoạt động · triển khai · API/local · bảo mật

**Nội dung trên slide:**

- **Tuyển sinh** — Tra cứu và số liệu
- **Đào tạo** — Quy chế và học vụ
- **Tổng hợp** — Giao việc liên lĩnh vực

**Lời thuyết trình:**

Kính thưa quý thầy cô, Credere là nền tảng trợ lý AI hỗ trợ cán bộ tra cứu, xử lý số liệu và soạn báo cáo có căn cứ. Hiện nhóm có AI Tuyển sinh, AI Đào tạo và AI Tổng hợp cho lãnh đạo; hướng mở rộng là NCKH, HTQT, Nhân sự và Hành chính. Bản demo có 106 văn bản công khai, còn số liệu nghiệp vụ là giả lập. Em xin trình bày cách hoạt động, lợi ích, phương án triển khai, chi phí API so với local và bảo mật thông tin nhà trường.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Kính thưa quý thầy cô, Credere là dự án xây dựng trợ lý nghiệp vụ cho nhà trường theo mô hình nhiều tác tử AI phối hợp. Bài trình bày đi qua mục tiêu, cách hoạt động, lợi ích so với cách làm thủ công, các phương án triển khai và bảo mật. Bản hiện tại đã có AI Tuyển sinh, AI Đào tạo và AI Tổng hợp, truy cập qua https://proxyllm.store. Tài liệu công khai và số liệu nghiệp vụ cần được phân biệt: kho có 106 văn bản công khai; hai cơ sở dữ liệu nghiệp vụ đang chạy vẫn là giả lập. Việc chuyển toàn bộ dữ liệu lên VPS không biến dữ liệu giả lập thành hồ sơ thật. Các phần đề xuất sau đây là kế hoạch cần kiểm chứng cùng Nhà trường, không phải mọi tính năng đã hoàn thành. Mục tiêu toàn dự án hướng tới sáu lĩnh vực: Tuyển sinh, Đào tạo, NCKH, HTQT, Nhân sự và Hành chính. Hiện có hai AI lĩnh vực cùng AI Tổng hợp; phần mở rộng có điều kiện về dữ liệu và quyền.

**Căn cứ:** `CONTENT_FACTS.json`; [https://proxyllm.store/api/apps](https://proxyllm.store/api/apps)

**Chuyển ý:** Từ nội dung này, chuyển sang: con người tự làm và có credere hỗ trợ.

### Slide 2. Con người tự làm và có Credere hỗ trợ

**Thông điệp:** AI hỗ trợ thao tác lặp lại; con người giữ quyền hiểu bối cảnh và phê duyệt.

**Nội dung trên slide:**

| Công đoạn | Tự làm | Có Credere hỗ trợ |
| --- | --- | --- |
| Tìm và lấy dữ liệu | Mở văn bản, lọc bảng, hỏi đầu mối | Tra nguồn / chọn truy vấn định sẵn |
| Ghép nhiều đơn vị | Chờ từng đầu mối rồi ghép | Giao AI con, kết hợp khi đầu vào đạt |
| Tính và viết | Tính toán, lập bảng, soạn báo cáo | Code tính; AI viết nháp có nguồn |
| Kiểm tra và quyết định | Cán bộ kiểm tra, lãnh đạo duyệt | Vẫn do cán bộ và lãnh đạo chịu trách nhiệm |

**Lời thuyết trình:**

Khi tự làm một báo cáo liên phòng, cán bộ phải tìm văn bản, lấy số liệu từ các đầu mối, ghép bảng, tính và viết lại. Credere hỗ trợ các thao tác đó bằng truy vấn định sẵn, phép tính do code thực hiện và bản nháp có nguồn. Các công việc độc lập có thể chạy song song. Tuy nhiên, cán bộ vẫn kiểm tra định nghĩa chỉ số, bối cảnh và phê duyệt kết quả. Chúng em chưa khẳng định tiết kiệm một tỷ lệ thời gian cụ thể. Khi pilot sẽ đo đến lúc báo cáo được chấp nhận, tính cả thời gian đọc lại và sửa, để biết AI có thực sự giảm công hay không.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Hiện cán bộ phải mở nhiều văn bản, lấy các bảng từ từng phòng, kiểm tra cùng kỳ rồi tính và viết lại. Khi có Credere, AI đề xuất kế hoạch, lựa chọn công cụ và soạn kết quả từ nguồn đã nối. Các bước độc lập có thể chạy song song. Tuy nhiên, thuật ngữ nghiệp vụ, văn bản nào áp dụng cho khóa nào và cách xử lý ngoại lệ vẫn cần cán bộ kiểm tra. Code tính đúng một biểu thức không bảo đảm model chọn đúng đầu vào. Vì vậy so sánh phải tính cả công rà soát và sửa. Chúng ta không khẳng định AI tốt hơn con người ở mọi công việc, cũng không dùng AI để thay thẩm quyền ban hành quyết định.

**Căn cứ:** `backend/app/graph.py`; `backend/app/workers.py`

**Chuyển ý:** Từ nội dung này, chuyển sang: kiến trúc toàn bộ hệ thống.

### Slide 3. Kiến trúc toàn bộ hệ thống

**Thông điệp:** Tách giao diện, điều phối, dữ liệu và nơi chạy model để có thể thay từng phần.

**Nội dung trên slide:**

- **Giao diện web** — Hỏi đáp · nguồn · CSV · tiến độ
- **Điều phối** — Master · kế hoạch · nghiệm thu
- **AI lĩnh vực** — Tuyển sinh · Đào tạo · Phân tích
- **Nguồn và model** — JSON / SQLite · gateway API

Ghi chú hiển thị: Đang chạy: FastAPI + LangGraph + SQLite, sau Nginx/systemd trên VPS. Chưa có SSO và checkpoint bền.

**Lời thuyết trình:**

Hệ thống có bốn lớp: giao diện web, bộ điều phối, các AI lĩnh vực và lớp nguồn dữ liệu/model. Backend lập kế hoạch, kiểm tra rồi giao việc; AI lĩnh vực đọc nguồn hoặc chọn truy vấn; bộ điều phối nghiệm thu và tổng hợp. Văn bản và cơ sở dữ liệu được quản lý riêng, model không tự chạy SQL tùy ý. Bản demo hiện dùng FastAPI, LangGraph và SQLite chỉ đọc, chạy sau Nginx trên VPS. Model vẫn gọi qua API bên ngoài. Vì tách các lớp này, sau này có thể giữ ứng dụng tại trường và thay nơi chạy model khi cần.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Trên cùng là trình duyệt cho cán bộ và lãnh đạo. Backend nhận yêu cầu, dựng kế hoạch và quản lý các tác vụ bằng LangGraph. AI lĩnh vực làm việc với văn bản đã xử lý và bộ truy vấn dữ liệu riêng. Gateway gọi model theo vai trò và ghi mức sử dụng. Ở bản demo, nguồn là JSON, số liệu là SQLite chỉ đọc; web dùng FastAPI, tiến độ qua SSE. Trên VPS, Nginx kết thúc HTTPS và chuyển tới ứng dụng, systemd giữ tiến trình chạy. PostgreSQL, tìm kiếm ngữ nghĩa nâng cao và SSO trong kế hoạch cũ chưa phải toàn bộ đã có. Kiến trúc cho phép giữ ứng dụng ở trường hoặc VPS nhưng lựa chọn nơi chạy model là quyết định riêng.

**Căn cứ:** `backend/app/web.py`; `backend/app/graph.py`; `deploy/credere.service`

**Chuyển ý:** Từ nội dung này, chuyển sang: ai hiệu trưởng giao việc thật cho ai con.

### Slide 4. AI Hiệu trưởng giao việc thật cho AI con

**Thông điệp:** Cấp Tổng hợp không được nạp toàn bộ dataset của hai AI lĩnh vực.

**Nội dung trên slide:**

- **AI Tổng hợp** — Yêu cầu + mô tả năng lực AI con
- **AI Tuyển sinh** — Nguồn và truy vấn tuyển sinh riêng
- **AI Đào tạo** — Nguồn và truy vấn đào tạo riêng
- **Kết quả trả về** — Báo cáo + bằng chứng + số liệu đã nghiệm thu

Ghi chú hiển thị: Bản ghi 29/9: hai AI con có kế hoạch riêng; T3 đợi T1 + T2; 18 lượt gọi, 4 phút 47 giây.

**Lời thuyết trình:**

Điểm quan trọng là AI Hiệu trưởng thực sự giao việc, không được nạp toàn bộ dataset của hai AI con. Code của nó không gắn kho tài liệu hay CSDL trực tiếp. Nó biết năng lực từng AI để lập kế hoạch; AI con tự chạy, nghiệm thu rồi trả báo cáo và số liệu. Nếu cần tính thêm, tác tử Phân tích nhận các kết quả đó. Một bản ghi ngày 29/9 cho thấy Tuyển sinh và Đào tạo được giao cùng đợt; bước Phân tích đợi cả hai đạt. Toàn bộ có 18 lượt gọi và mất 4 phút 47 giây. Câu đơn lĩnh vực có thể chỉ gọi một AI con. Đây là cấu trúc phối hợp; quyền truy cập theo người dùng vẫn cần bổ sung.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Code tạo AI Tổng hợp với sources rỗng, data bằng None và công cụ riêng là analysis. Khi lập kế hoạch, nó nhận yêu cầu cùng mô tả năng lực AI con, không nhận toàn bộ tài liệu và cơ sở dữ liệu. Khi giao việc, mỗi AI con mở một lượt graph và client riêng, tự lập kế hoạch, làm việc, nghiệm thu rồi trả về báo cáo và các kết quả đã đạt. Hiệu trưởng có thể dùng số liệu đó để phân tích tiếp. Một câu đơn lĩnh vực không bắt buộc gọi đủ hai con; một câu liên phòng có thể chạy song song hoặc tuần tự tùy phụ thuộc. Đây là phân tách ngữ cảnh và công cụ trong code, chưa phải cơ chế xác thực theo chức danh người dùng. Bản ghi 02:51 ngày 29/9 trả lời câu hỏi về ngành thiếu chỉ tiêu và cảnh báo học vụ/rời trường. Khoảng giây 40, T1 và T2 được giao cùng đợt. Hai AI có plan_saved riêng; bên Tuyển sinh còn dùng worker văn bản, dữ liệu và phân tích, bên Đào tạo dùng worker dữ liệu. Khoảng phút 4 giây 13, bước T3 mới được giao sau khi đầu vào đạt. Tổng thời gian 287,2 giây, gồm 18 lượt gọi: Tuyển sinh 8, Đào tạo 4 và cấp điều phối 6. Trong 6 lượt cấp trên có 2 lượt của T3, không được gán toàn bộ 6 lượt cho T3. Đây là bằng chứng từ hồ sơ đã lưu, chưa phải lần gọi live mới trong buổi sửa slide.

**Căn cứ:** `backend/app/apps.py:128`; `backend/app/workers.py:234`

**Chuyển ý:** Từ nội dung này, chuyển sang: trình diễn trên tên miền đã triển khai.

### Slide 5. Trình diễn trên tên miền đã triển khai

**Thông điệp:** https://proxyllm.store — nhập yêu cầu mới, xem giao việc và mở nguồn.

**Nội dung trên slide:**

- **Quan sát** — AI nào nhận việc; phụ thuộc nào phải đợi.
- **Kiểm chứng** — Nguồn dẫn, mốc dữ liệu và phần hạn chế.

Ảnh minh họa: `shots/current/welcome-principal.png`.

Ghi chú hiển thị: Giới hạn demo 2 phút 30 giây; nếu chưa xong, tiếp tục bài và dùng ảnh dự phòng khi cần.

**Lời thuyết trình:**

Bây giờ em mở proxyllm.store và chọn AI Tổng hợp. Ví dụ cần biết ngành nào thiếu chỉ tiêu và ở những ngành đó tình hình cảnh báo học vụ, rời trường ra sao. Quý thầy cô chú ý kế hoạch và phần việc giao cho từng AI bên phải. Phần demo dành 2 phút 30 giây, nên nếu kết quả chưa xong em sẽ tiếp tục bài và quay lại khi cần. Khi có kết quả, chúng ta kiểm tra nguồn, mốc dữ liệu và giới hạn trước khi dùng. Số liệu nghiệp vụ trong ví dụ là giả lập. Nếu dùng ảnh kết quả dự phòng, em sẽ nói rõ đó là lượt chạy đã lưu.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Mở https://proxyllm.store, chọn AI Tổng hợp, giới thiệu một yêu cầu liên lĩnh vực. Thời gian phần demo là 2 phút 30 giây, không phải cam kết hệ thống trả lời trong mốc này. Câu liên lĩnh vực trong hồ sơ mất 4 phút 47 giây, nên chỉ cần cho thấy kế hoạch và AI con nhận việc trong phần live. Nếu chưa xong, chuyển sang slide tiếp; dùng phụ lục ảnh kết quả đã lưu khi cần và nói rõ nguồn gốc. Không chạy nhiều câu cùng lúc trong phần trình diễn. Khi có kết quả, mở Nguồn đã dẫn, chỉ mốc dữ liệu và giới hạn. Giao diện nhập tay/gợi ý chạy mới, không có nút Bản ghi; không hướng dẫn Shift+bấm. Domain đã được xác nhận tải web và SSE bản ghi, chưa nghiệm thu tải live lớn. Số liệu nghiệp vụ vẫn giả lập dù toàn bộ dữ liệu đã được chuyển lên VPS.

**Căn cứ:** [https://proxyllm.store](https://proxyllm.store); `shots/current/screenshots.json`

**Chuyển ý:** Từ nội dung này, chuyển sang: ba lựa chọn nơi xử lý model.

### Slide 6. Ba lựa chọn nơi xử lý model

**Thông điệp:** Nơi đặt web/CSDL và nơi suy luận AI có thể khác nhau.

**Nội dung trên slide:**

| Tiêu chí | API trực tiếp | Local tại trường | Lai |
| --- | --- | --- | --- |
| Vốn ban đầu | Thấp; không mua GPU | Máy/GPU, lưu trữ, dự phòng | Có phần hạ tầng local |
| Vận hành model | Nhà cung cấp đảm nhận | Đội trường tự vận hành | Quản cả hai tuyến |
| Dữ liệu prompt | Ra API được duyệt | Ở hạ tầng trường nếu cấu hình kín | Theo chính sách từng tác vụ |
| Đánh đổi | Phụ thuộc mạng / nhà cung cấp | VRAM, tải, bảo trì, chất lượng | Chính sách và tích hợp phức tạp |

**Lời thuyết trình:**

Có ba phương án. API trực tiếp giúp bắt đầu nhanh và không phải mua GPU, nhưng prompt đi qua dịch vụ ngoài, phụ thuộc mạng và hạn mức. Model local tại trường cho quyền kiểm soát nơi xử lý cao hơn, đổi lại phải đầu tư và vận hành máy, đo bộ nhớ, chất lượng và tải. Phương án lai chọn tuyến theo dữ liệu: phần được phép gửi dùng API, phần bắt buộc nội bộ dùng local. VPS đang chạy web không có nghĩa model chạy local. Thuê GPU cloud cũng vẫn là xử lý ngoài trường. Vì vậy quyết định phải dựa đồng thời vào dữ liệu, chất lượng và tổng chi phí.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Phương án A đặt web và dữ liệu trong môi trường quản lý rồi gọi API OpenAI trực tiếp. Phương án B giữ ứng dụng, dữ liệu và model mở trong hạ tầng của trường. Phương án C là lai: dữ liệu được phép xuất gọi API, phần bắt buộc nội bộ chạy model nội bộ. Cùng một giao diện có thể dùng các tuyến này nhưng phải xây cơ chế chính sách, không chỉ đổi base URL. VPS đang chạy demo không đồng nghĩa model đang chạy local; model hiện được gọi ra gateway qua mạng. GPU cloud thuê theo giờ cũng là hạ tầng ngoài trường, dù tự quản model. Lựa chọn cần dựa trên yêu cầu dữ liệu, ngân sách, năng lực vận hành và chất lượng trên đúng tác vụ của NAU.

**Căn cứ:** [https://developers.openai.com/api/docs/models/compare](https://developers.openai.com/api/docs/models/compare); [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility)

**Chuyển ý:** Từ nội dung này, chuyển sang: api openai: giá và cách tính một yêu cầu.

### Slide 7. API OpenAI: giá và cách tính một yêu cầu

**Thông điệp:** Cộng mọi lời gọi trong một Run; API trực tiếp và giá gateway hiện tại là hai kênh khác nhau.

**Nội dung trên slide:**

| Model / vai trò dự kiến | Input / 1M | Output / 1M | Phạm vi giá |
| --- | --- | --- | --- |
| GPT-6 Sol · Master/review | $2,00 | $10,00 | Standard · short context |
| GPT-6 Luna · Worker | $0,10 | $0,50 | Standard · short context |

Ghi chú hiển thị: Ví dụ tổng Master 20k/2k + Worker 30k/2k → $0,064 ≈ 1.728 đ/Run; tỷ giá giả định 27.000 đ/USD.

**Lời thuyết trình:**

Giá API chính thức tham khảo ngày 29/9, Standard short context, tính bằng USD trên một triệu token. Sol là 2 đô đầu vào và 10 đô đầu ra; Luna là 0,1 đô đầu vào và 0,5 đô đầu ra. Một yêu cầu người dùng có nhiều lời gọi, phải cộng cả AI con, nghiệm thu và sửa. Ví dụ tổng Master dùng 20 nghìn vào, 2 nghìn ra; Worker dùng 30 nghìn vào, 2 nghìn ra thì phí token là 0,064 đô, khoảng 1.728 đồng theo tỷ giá dự toán 27.000. Đây là giả định minh họa, chưa có thuế, công cụ hay retry. API trực tiếp và gateway của demo là hai kênh khác nhau; khi chuyển phải kiểm chứng lại.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Bảng dùng đơn vị USD trên một triệu token, Standard short context, kiểm tra tài liệu OpenAI ngày 29/9/2026. Sol định hướng làm Master/review, Luna làm Worker. Một yêu cầu người dùng gồm nhiều lời gọi nên phải cộng cả AI con và lần sửa. Minh họa Master tổng 20 nghìn token vào, 2 nghìn ra là 0,06 USD; Worker 30 nghìn vào, 2 nghìn ra là 0,004 USD. Tổng 0,064 USD, với tỷ giá dự toán 27.000 là 1.728 đồng. Đây là giả định, không phải trung bình đã đo hay giá cố định mỗi câu. Ngữ cảnh dài, cache, công cụ, thuế và retry phải tính riêng. Demo hiện gọi gateway; triển khai API OpenAI trực tiếp cần tài khoản trường, ánh xạ model và chạy lại kiểm chứng trên đúng kênh.

**Căn cứ:** [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing); [https://developers.openai.com/api/docs/models/compare](https://developers.openai.com/api/docs/models/compare); [https://developers.openai.com/api/docs/models/gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol); `COST_MODEL.json`

**Chuyển ý:** Từ nội dung này, chuyển sang: model local: chủ động dữ liệu, thêm công vận hành.

### Slide 8. Model local: chủ động dữ liệu, thêm công vận hành

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

Local dùng model trọng số mở, ví dụ Qwen3 với Ollama hoặc vLLM; không phải tải model API về chạy. Cần thử tiếng Việt, độ đúng và số phiên trước khi chọn cấu hình. Để minh họa tổng chi phí, giả định máy 150 triệu, dùng 36 tháng: phân bổ 4,17 triệu/tháng. Cộng công vận hành, điện và bảo trì giả định 3 triệu, tổng là 7,17 triệu/tháng. Tiền chi năm đầu là 186 triệu. Đây chưa phải báo giá hay cấu hình đã chốt. Có thể thuê GPU thử trước, nhưng GPU cloud vẫn nằm ngoài trường và phát sinh phí lưu trữ, vận hành. Đề xuất là benchmark trước khi mua máy.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Có thể chọn Qwen3 8B, 14B hoặc 32B làm ứng viên kiểm chứng, không khẳng định đó là lựa chọn tốt nhất. Đây là model trọng số mở theo giấy phép của họ; không tải model API Sol/Luna về máy để chạy. Ollama giúp thử nhanh, vLLM có thể dùng làm máy chủ phục vụ, đều cần kiểm thử tích hợp. Model lượng tử hóa nhỏ hơn nhưng RAM/VRAM còn phải chứa cache ngữ cảnh và phiên đồng thời; dung lượng tệp không bằng tổng bộ nhớ vận hành. Bắt đầu một phiên và ngữ cảnh vừa phải rồi đo lên. VPS 2 GB RAM hiện tại chỉ chạy app gọi API, chưa có máy phục vụ model local được xác minh. Giả định máy trọn bộ 150 triệu đồng và dùng 36 tháng. Phân bổ vốn theo tháng là 4,17 triệu; vận hành giả định 3 triệu/tháng gồm công người 2 triệu, điện/làm mát 0,5 triệu và bảo trì 0,5 triệu. Tổng quy đổi 7,17 triệu/tháng. Dòng tiền năm đầu là 150 cộng 36, tức 186 triệu, khác với chi phí phân bổ năm là 86 triệu. Chưa tính phát triển app, nhập dữ liệu, bảo mật bổ sung, thuế, vốn và máy dự phòng. Để thử trước khi mua, giá A40 48 GB trên Runpod được tham khảo ở 0,49 USD/giờ; 176 giờ khoảng 2,33 triệu theo tỷ giá 27.000, chưa storage và công vận hành. Đây là GPU cloud, không phải dữ liệu được giữ tại trường.

**Căn cứ:** [https://qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/); [https://docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility); [https://www.runpod.io/pricing](https://www.runpod.io/pricing); `LOCAL_OPTIONS_RESEARCH.md`; `COST_MODEL.json`

**Chuyển ý:** Từ nội dung này, chuyển sang: so chi phí công bằng: cùng tải, cùng chất lượng.

### Slide 9. So chi phí công bằng: cùng tải, cùng chất lượng

**Thông điệp:** Bảng chỉ so phần suy luận AI; chưa chứng minh máy local đạt cùng chất lượng và công suất.

**Nội dung trên slide:**

| Tải/tháng | API giả định | Local giả định |
| --- | --- | --- |
| 1.000 | 1,73 triệu | 7,17 triệu |
| 5.000 | 8,64 triệu | 7,17 triệu |
| 20.000 | 34,56 triệu | 7,17 triệu |

Ghi chú hiển thị: Local ở các tải trên chưa được benchmark. Phải so chi phí trên công việc được chấp nhận, không chỉ giá token.

**Lời thuyết trình:**

Bảng này giữ cùng giả định API 1.728 đồng một yêu cầu. 1.000 yêu cầu một tháng khoảng 1,73 triệu, 5.000 là 8,64 triệu và 20.000 là 34,56 triệu. Local được giữ ở 7,17 triệu chỉ nếu một máy đủ công suất và đạt cùng chất lượng; hiện chưa đo điều đó. Giao điểm khoảng 4.147 yêu cầu/tháng chỉ là kết quả mô hình chi phí, chưa phải hòa vốn đã chứng minh. Cần cộng công rà soát, lỗi và hạ tầng liên quan trước quyết định đầu tư.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

So ba mức tải với phí API giả định 1.728 đồng/yêu cầu và local phân bổ 7,17 triệu/tháng. API tăng theo số yêu cầu, local có phần cố định. Ở 1.000 yêu cầu, API khoảng 1,73 triệu; 5.000 là 8,64 triệu; 20.000 là 34,56 triệu. Local giữ 7,17 chỉ với giả định một máy vẫn phục vụ được tải đó trong giờ vận hành và đạt cùng chất lượng. Nếu phải thêm GPU, chạy dài giờ hoặc rà soát nhiều hơn, chi phí thay đổi. Điểm hai đường bằng nhau khoảng 4.147 yêu cầu/tháng chỉ là giao điểm mô hình, không phải điểm hòa vốn đã nghiệm thu. Chưa gồm phần hạ tầng, nhân công ứng dụng chung và chi phí rủi ro.

**Căn cứ:** `COST_MODEL.json`; [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)

**Chuyển ý:** Từ nội dung này, chuyển sang: phương án c: kết hợp api và model nội bộ.

### Slide 10. Phương án C: kết hợp API và model nội bộ

**Thông điệp:** Chọn tuyến theo chính sách dữ liệu; không chuyển cloud chỉ vì model local gặp lỗi.

**Nội dung trên slide:**

- **Dữ liệu được phép xuất** — API trực tiếp, tài khoản do Trường quản lý.
- **Bắt buộc giữ nội bộ** — Model local + truy vấn/nguồn trong vùng kiểm soát.
- **Điều phối xuyên suốt** — Cả Master, AI con, review và tổng hợp tuân chính sách.
- **Khi xảy ra lỗi** — Local-only không tự fallback ra API ngoài.

Ghi chú hiển thị: Đề xuất tích hợp; hiện mới có lọc nhà cung cấp theo nhãn trusted, chưa có local-only policy.

**Lời thuyết trình:**

Phương án đề xuất là dùng API trực tiếp cho nguồn được phép gửi, đồng thời thử local cho nhu cầu nội bộ. Chính sách phải đi theo toàn bộ yêu cầu: Master, AI con, nghiệm thu và tổng hợp. Báo cáo AI con cũng có thể chứa thông tin nhạy cảm, không tự trở thành công khai khi tóm tắt. Nếu tác vụ được đánh dấu chỉ xử lý nội bộ mà model lỗi, hệ thống dừng hoặc dùng model nội bộ khác; không tự chuyển cloud. Cơ chế định tuyến theo độ nhạy này là phần cần xây trước pilot.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Phương án đề xuất là dùng API trực tiếp để thử các việc có nguồn được phép gửi, đồng thời benchmark model local cho việc có yêu cầu giữ nội bộ. Khi triển khai lai, tác vụ được gắn nhãn chính sách ngay từ lúc nhận yêu cầu. Chính sách phải đi qua AI con, bước nghiệm thu, model dự phòng và AI Tổng hợp. Một kết quả AI con dù chỉ là tóm tắt vẫn có thể chứa dữ liệu hạn chế nên không được tự coi là công khai. Nếu tác vụ local-only gặp lỗi, hệ thống chờ, dừng hoặc dùng model nội bộ khác đã duyệt; không tự gửi sang cloud. Bản demo chưa có cổng định tuyến theo độ nhạy này. Thử nghiệm phải chứng minh cả chất lượng lẫn đường đi dữ liệu.

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

Bảo mật bắt đầu bằng phân loại dữ liệu do Nhà trường phê duyệt. Công khai như quy chế có thể dùng API được duyệt. Nội bộ như thống kê chưa công bố cần quyền người dùng và danh mục được phép xuất. Hồ sơ, điểm, liên hệ hoặc nhân sự hạn chế phải ở tuyến nội bộ nếu chính sách yêu cầu. Câu hỏi, báo cáo, CSV và log cũng theo cùng quyền và thời hạn lưu. Chép dữ liệu lên một máy chủ hay bỏ cột họ tên chưa đủ để kết luận thông tin đã an toàn.

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

Bản hiện tại có HTTPS và mật khẩu cài đặt, nhưng chưa có phân quyền hỏi đáp theo phòng ban. Pilot cần tài khoản trường và kiểm quyền tại backend, cả nguồn, lịch sử, SSE và xuất CSV. Luồng hiện tại đã tách hàng cá nhân khỏi dữ liệu truy vấn gửi model; vẫn phải kiểm câu hỏi, văn bản, log và nhóm nhỏ có thể suy ra cá nhân. Với API, không dùng dữ liệu huấn luyện mặc định không đồng nghĩa không lưu log; phải rà điều kiện hợp đồng và endpoint. Vận hành còn cần quản lý key, hạn mức, backup mã hóa và thử phục hồi. Mỗi lớp phải có người chịu trách nhiệm và bằng chứng kiểm thử.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Bản demo có HTTPS và mật khẩu bảo vệ API cấu hình, nhưng không có đăng nhập nghiệp vụ cho từng phòng ban. Tab Hiệu trưởng không xác minh chức danh. Pilot cần SSO, vai trò và kiểm quyền ngay tại backend cho hỏi đáp, nguồn, lịch sử, SSE và tải CSV. Code đã tách hàng cá nhân trong truy vấn, nhưng câu hỏi, văn bản, báo cáo và log vẫn cần kiểm; tổng hợp nhóm nhỏ vẫn có thể làm lộ người. Với API OpenAI, không dùng dữ liệu huấn luyện mặc định không đồng nghĩa không giữ log: điều kiện lưu giữ và ZDR phải kiểm theo hợp đồng/endpoint. Với local-only, mọi bước kể cả review và dự phòng phải ở tuyến nội bộ. Vận hành cần quản key, hạn mức, log có hạn lưu và backup phục hồi được; giao phòng CNTT chịu trách nhiệm.

**Căn cứ:** `backend/app/settings_auth.py`; `backend/app/web.py`; `SECURITY_BENEFITS_DRAFT.md`; [https://developers.openai.com/api/docs/guides/your-data](https://developers.openai.com/api/docs/guides/your-data)

**Chuyển ý:** Từ nội dung này, chuyển sang: kế hoạch đề xuất trong 12 tuần.

### Slide 13. Kế hoạch đề xuất trong 12 tuần

**Thông điệp:** Mỗi giai đoạn có đầu ra và điều kiện chuyển tiếp; thời gian phụ thuộc dữ liệu và nhân sự.

**Nội dung trên slide:**

| Giai đoạn | Công việc chính | Đầu ra / điều kiện đạt |
| --- | --- | --- |
| Tuần 1–2 · Chốt đầu vào | Phỏng vấn, nguồn, quyền, đo nền | Bộ việc ưu tiên + nguồn được duyệt |
| Tuần 3–5 · Nền tảng | SSO/quyền, nhập nguồn, truy vấn | Test đọc/xuất dữ liệu đúng quyền |
| Tuần 6–8 · Hoàn thiện | Phối hợp, phục hồi, so API/local | Qua kiểm thử lỗi và chất lượng |
| Tuần 9–12 · Pilot | Câu mới, cán bộ chấm, đo chi phí | Biên bản đạt / điểm phải sửa |

Ghi chú hiển thị: Lịch đề xuất 10–12/2026, cần chốt năng lực nhóm, dữ liệu và lịch nghiệm thu với Nhà trường.

**Lời thuyết trình:**

Lịch đề xuất là 12 tuần có điều kiện. Tuần 1–2 chốt nghiệp vụ, nguồn, quyền và đo cách cán bộ tự làm. Tuần 3–5 xây nền tảng truy cập, nhập nguồn có phiên bản và truy vấn. Tuần 6–8 hoàn thiện phối hợp, thử lỗi, phục hồi và so API/local. Tuần 9–12 nghiệm thu bằng câu hỏi mới, cho nhóm nhỏ dùng rồi bàn giao. Đơn vị dữ liệu xác nhận chỉ số; CNTT quản hạ tầng; nhóm phát triển sửa và kiểm thử. Thời gian cần thống nhất theo nhân sự và dữ liệu thực tế. Chưa đạt kiểm tra quyền thì chưa nối hồ sơ thật, chưa đạt chất lượng thì chưa mở rộng.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Lịch đề xuất bám giai đoạn tháng 10 đến tháng 12 năm 2026. Hai tuần đầu làm rõ nghiệp vụ và ma trận quyền, lấy nguồn được duyệt, đo cách cán bộ tự làm. Tuần 3–5 xây cơ chế đăng nhập, truy cập dữ liệu và nguồn có phiên bản. Tuần 6–8 hoàn thiện phối hợp, phục hồi và đối chứng API/local. Tuần 9–12 nghiệm thu bằng câu mới, thử tại nhóm nhỏ và bàn giao. Đây là kế hoạch có điều kiện, không cam kết đủ mọi lĩnh vực trong 12 tuần. Ưu tiên Tuyển sinh và Đào tạo đang có; NCKH/HTQT đưa vào khi có dữ liệu và đạt điều kiện. Chưa đạt kiểm tra quyền thì chưa nối dữ liệu thật, chưa đạt chất lượng thì chưa mở rộng.

**Căn cứ:** `PLAN.md`; `DATA_PLAN.md`

**Chuyển ý:** Từ nội dung này, chuyển sang: nghiệm thu bằng công việc thật và người phụ trách.

### Slide 14. Nghiệm thu bằng công việc thật và người phụ trách

**Thông điệp:** Đầu mối nghiệp vụ duyệt nguồn; CNTT vận hành; nhóm phát triển sửa; lãnh đạo nghiệm thu.

**Nội dung trên slide:**

- **Chất lượng** — Câu mới; cán bộ chấm nguồn, số và suy luận theo rubric.
- **Quyền / an toàn** — Không đọc/xuất trái quyền trong bộ thử; kiểm injection.
- **Bền vững** — Thử lỗi, khởi động lại, backup/restore và hạn mức.
- **Giá trị sử dụng** — Đo thời gian có kiểm/sửa và chi phí Run đạt.

Ghi chú hiển thị: Mỗi báo cáo đạt cần đúng nguồn, số và phạm vi; thử sai quyền không có rò rỉ. Mục tiêu chất lượng phải chốt trước.

**Lời thuyết trình:**

Nghiệm thu phải dùng câu mới và người có chuyên môn, không chỉ dựa test phần mềm. Kiểm bốn mặt: chất lượng báo cáo, quyền dữ liệu, khả năng chịu lỗi và giá trị sử dụng. Đo thời gian từ lúc nhận việc đến khi cán bộ chấp nhận, gồm cả sửa; chi phí tính cả lần lỗi. API và local dùng cùng nguồn và tiêu chí. Các số test nội bộ trong phụ lục chứng minh một phần cơ chế, không có nghĩa hệ thống luôn đúng. Nhà trường cùng nhóm chốt ngưỡng trước khi đo.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Đề xuất dùng ít nhất 60 tình huống tách theo tra cứu, liên lĩnh vực, thiếu dữ liệu và sai quyền; bổ sung 30 tác vụ so năng suất nếu có đủ cán bộ. Kiểm số liệu, nguồn và suy luận bằng người chuyên môn, không chỉ dò từ khóa. Mục tiêu tham khảo là ít nhất 85% ca có dữ liệu đạt rubric; bộ kiểm quyền không có lần đọc/xuất trái phép; phép tính fixture đạt đầy đủ. Đây là ngưỡng đề xuất cần xác nhận, không phải kết quả đã đạt. Với vận hành, thử mất mạng, timeout, khởi động lại và phục hồi backup; đo p50/p95 cùng chi phí cho Run được chấp nhận. API và local phải dùng cùng câu/nguồn và cùng điều kiện chất lượng để so. Đo thêm năng suất bằng 30 tác vụ mới, hai cách tự làm/có AI với cùng nguồn; tính cả thời gian cán bộ sửa. Đơn vị dữ liệu xác nhận chỉ số; CNTT quản hệ thống và backup; nhóm phát triển chịu trách nhiệm release và test; người nghiệm thu chốt kết quả. Các con số 159 test, 30/30 hay 14/14 trước đó chỉ là bằng chứng nội bộ, không thay nghiệm thu độc lập.

**Căn cứ:** `PLAN.md:Tiêu chí kiểm tra`; `SECURITY_BENEFITS_DRAFT.md`

**Chuyển ý:** Từ nội dung này, chuyển sang: đề xuất lựa chọn và các quyết định cần chốt.

### Slide 15. Đề xuất lựa chọn và các quyết định cần chốt

**Thông điệp:** Bắt đầu bằng API cho dữ liệu được phép; benchmark local trước khi mua; bảo mật trước pilot.

**Nội dung trên slide:**

- **Chọn phạm vi** — Hai đầu mối Tuyển sinh/Đào tạo; công việc ưu tiên cụ thể.
- **Chọn dữ liệu** — Nguồn được duyệt, quyền và chính sách API/local.
- **Chọn ngân sách** — Tải dự kiến + nhân công + hạ tầng + dự phòng.
- **Chọn điều kiện mở rộng** — Câu hỏi độc lập, biên bản nghiệm thu và người vận hành.

**Lời thuyết trình:**

Để bắt đầu, nhóm cần hai đầu mối Tuyển sinh và Đào tạo, một phạm vi dữ liệu được duyệt, ngân sách thử có giới hạn và người nghiệm thu. Đề xuất dùng API cho phần được phép, thử local trước khi mua, hoàn thiện bảo mật trước pilot dữ liệu thật. Mục tiêu là đo được giá trị trên công việc cụ thể rồi mới mở rộng toàn trường. Em xin cảm ơn quý thầy cô.

**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**

Nhóm đề xuất giữ demo như bằng chứng cơ chế, dùng tài khoản API trực tiếp do Trường quản lý cho nguồn được phép xử lý bên ngoài, và dành một bài đo riêng cho model local. Chưa có căn cứ mua máy lớn chỉ từ bảng dự toán. Nhà trường cần cử đầu mối hai đơn vị, duyệt phạm vi dữ liệu, thống nhất chính sách xuất ra ngoài và giao nhóm CNTT quản vận hành. Chốt ngân sách theo mức dùng cùng dự phòng, bao gồm công triển khai/kiểm tra chứ không chỉ phí token. Lĩnh vực mở rộng được phê duyệt sau khi qua gate chất lượng và quyền. Kết quả mong muốn là một pilot đo được giá trị và chỉ ra rõ giới hạn, để quyết định đầu tư tiếp có căn cứ.

**Căn cứ:** `yeucauslide.txt`; `PLAN.md`; `COST_MODEL.json`

### Slide 16. A1 · Sáu lĩnh vực và trạng thái hiện tại

**Thông điệp:** Đã có hai AI lĩnh vực và AI Tổng hợp; các lĩnh vực khác mở theo điều kiện dữ liệu.

**Nội dung trên slide:**

| Phạm vi | Hiện trạng | Điều kiện tiếp theo |
| --- | --- | --- |
| Tuyển sinh | 70 văn bản · 19 truy vấn | Hiệu chỉnh với dữ liệu được duyệt |
| Đào tạo | 36 văn bản · 17 truy vấn | Chốt quy chế theo khóa, định nghĩa chỉ số |
| NCKH / HTQT | Khung tổng quát; chưa đủ nghiệp vụ | Nguồn học thuật, dữ liệu và rubric |
| Nhân sự / Hành chính | Chưa triển khai ứng dụng | Ma trận quyền và nguồn nội bộ |

Ghi chú hiển thị: AI Tổng hợp đang kết nối Tuyển sinh + Đào tạo. Số liệu nghiệp vụ hiện là giả lập.

**Lời thuyết trình:**

Hai lĩnh vực triển khai cụ thể hôm nay là Tuyển sinh và Đào tạo. AI Tuyển sinh có 70 văn bản và 19 truy vấn; AI Đào tạo có 36 văn bản và 17 truy vấn. AI Tổng hợp giao việc cho hai AI này. Bức tranh toàn dự án hướng tới sáu lĩnh vực: Tuyển sinh, Đào tạo, Nghiên cứu khoa học, Hợp tác quốc tế, Nhân sự và Hành chính. NCKH và HTQT mới có khung worker tổng quát, chưa có ứng dụng nghiệp vụ đầy đủ như hai lĩnh vực đang demo. Nhân sự và Hành chính cần dữ liệu và quyền phức tạp hơn nên làm sau. Mỗi lĩnh vực mới phải có đầu mối, bộ nguồn, truy vấn và bộ thử riêng. AI Tổng hợp là lớp phối hợp, không tính là lĩnh vực thứ bảy.

**Căn cứ:** `backend/app/apps.py:117`; `backend/app/planning.py`; `PLAN.md`

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
4. Giới hạn demo ở 2:30; nếu chưa xong thì tiếp tục slide. Dùng phụ lục ảnh kết quả và công khai đó là lượt đã lưu.
5. Không mở file chứa khóa/mật khẩu trên màn hình chiếu. Trang cài đặt vẫn yêu cầu mật khẩu riêng.
6. Phần hỏi đáp ngoài 15 phút có thể mở phụ lục cấu hình local, phép tính chi phí và chính sách dữ liệu.

## Giải thích mức tin cậy

- **Đã có/đã đo:** code, inventory public domain và các bản ghi/tệp test đã được kiểm tra trong phiên này hoặc phiên trước, ghi rõ phạm vi.
- **Giá tham khảo:** nguồn chính thức có ngày; không thay báo giá/hóa đơn của nhà cung cấp hoặc cổng trung gian.
- **Giả định dự toán:** token/Run, tải tháng, tỷ giá 27.000, máy 150 triệu và vận hành 3 triệu; thay được trong COST_MODEL.json.
- **Đề xuất pilot:** phân quyền, policy local-only, phục hồi, lịch 12 tuần và ngưỡng nghiệm thu; chưa phải toàn bộ đã triển khai.
