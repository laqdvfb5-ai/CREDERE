# Nội dung bổ sung: lợi ích và bảo mật Credere

Đối chiếu trực tiếp mã nguồn ngày 29/09/2026. Nhãn **ĐÃ CÓ** chỉ phần nhìn thấy trong code; **ĐỀ XUẤT PILOT** là việc phải xây dựng/kiểm chứng. Trạng thái VPS đang mở công khai và chỉ khóa trang cài đặt lấy từ trao đổi triển khai trong phiên này, chưa kiểm tra lại VPS. Không dùng tài liệu này như biên bản kiểm thử an toàn.

## Slide A — AI giảm công tổng hợp; cán bộ vẫn kiểm tra và quyết định

**Thông điệp:** Credere có thể rút ngắn các bước tìm, lọc, ghép và soạn báo cáo; mức tiết kiệm cần đo bằng tác vụ thật.

| Công đoạn | Cán bộ tự làm | Có Credere hỗ trợ | Trách nhiệm còn lại của con người |
|---|---|---|---|
| Làm rõ yêu cầu | Chia câu hỏi thành việc, xác định phòng cung cấp | Đề xuất kế hoạch và giao việc cho AI chuyên môn | Chốt phạm vi, kỳ dữ liệu và cách hiểu chỉ tiêu |
| Lấy số liệu | Mở báo cáo/Excel, lọc và đối chiếu | Chọn truy vấn được lập trình sẵn trên dữ liệu đã kết nối | Phòng dữ liệu xác nhận nguồn, định nghĩa và độ mới |
| Ghép hai phòng | Chờ từng phòng rồi ghép bảng | AI Tuyển sinh và AI Đào tạo xử lý độc lập khi có thể | Kiểm tra hai nguồn có cùng ngành, kỳ và mẫu số |
| Tính và viết báo cáo | Tính, tra quy định, viết bản nháp | Code thực hiện phép tính; AI soạn phân tích kèm nguồn | Rà soát phép suy luận, bổ sung bối cảnh và duyệt |
| Hành động | Ban hành/triển khai theo thẩm quyền | Đề xuất phương án và câu hỏi cần kiểm tra tiếp | Lãnh đạo/cán bộ quyết định; PoC chưa tự ban hành hay sửa dữ liệu |

**Lời nói:** “Giá trị không nằm ở việc có thêm một cửa sổ chat. Với câu hỏi liên phòng, cán bộ đang phải thu thập, thống nhất định nghĩa, tính và viết lại. Credere hỗ trợ phần thao tác lặp lại đó, đồng thời cho người dùng nhìn thấy ai đang làm việc gì và dữ liệu đến từ đâu. Chúng tôi chưa tuyên bố tiết kiệm một tỷ lệ thời gian cụ thể. Khi đưa vào thí điểm, phải tính cả thời gian cán bộ kiểm tra và sửa báo cáo, vì câu trả lời nhanh nhưng phải sửa nhiều có thể không tạo lợi ích.”

**Gợi ý trình bày:** Bảng 3–4 hàng trên slide; đưa hàng “làm rõ yêu cầu” và chi tiết vai trò vào Notes nếu chật. Tránh hình ảnh AI “thay thế” người phê duyệt.

## Slide B — Đo lợi ích bằng kết quả được cán bộ chấp nhận

**Thông điệp:** So sánh trên cùng nguồn dữ liệu, cùng câu hỏi và cùng tiêu chí nghiệm thu.

- **ĐỀ XUẤT PILOT:** 30 tác vụ đại diện — 10 tuyển sinh, 10 đào tạo, 10 liên phòng; dùng bộ đề chưa dùng để tinh chỉnh.
- Hai cách làm: cán bộ tự làm và cán bộ dùng Credere; đảo thứ tự, phân bổ người thực hiện để giảm hiệu ứng đã biết đáp án.
- Đo từ lúc nhận câu hỏi đến bản báo cáo **được chấp nhận**, gồm cả kiểm tra/sửa, thời gian chờ và lần chạy lỗi.
- Đánh giá số liệu đúng, nguồn đúng, thiếu sót quan trọng, tỷ lệ cần sửa, chi phí hoàn thành và phản hồi người dùng.
- Chỉ công bố mức cải thiện sau khi đo; hiện PoC chứng minh luồng xử lý, chưa chứng minh năng suất thực tế.

**Công thức dùng trong Notes:**

`Tiết kiệm thời gian = (T_tự_làm − T_có_AI) / T_tự_làm`, trong đó cả hai T đều tính tới lúc đạt cùng tiêu chí nghiệm thu. Báo cáo median/P90 cho thời gian, số lượng tác vụ hoàn thành và số lỗi nghiêm trọng. Với tiền, tính chi phí của các lần lỗi và sửa chia cho số tác vụ được chấp nhận; cộng công rà soát và phần hạ tầng/vận hành phân bổ. Không chỉ dùng phí token của câu trả lời thành công.

**Ngưỡng nghiệm thu đề xuất, cần BGH/phòng ban chốt trước pilot:** không chấp nhận lỗi nghiêm trọng về số liệu trong báo cáo cuối; không chấp nhận đọc/xuất dữ liệu trái quyền trong bộ thử; mức thời gian/chi phí mục tiêu chỉ chốt sau khi có số đo nền. Bộ thử đạt không chứng minh hết mọi tình huống ngoài thực tế.

**Lời nói:** “Một phép so sánh công bằng phải dùng cùng dữ liệu và tính đến bản báo cáo cuối đã được duyệt. Nếu AI trả lời trong một phút nhưng người dùng mất thêm hai mươi phút sửa, hai mươi phút đó phải tính. Chúng tôi dự kiến đo theo ba nhóm tác vụ và lưu cả lần lỗi. Nhờ đó nhà trường có thể quyết định dựa trên công sức thực sự giảm, độ đúng và chi phí cho một công việc hoàn thành.”

## Slide C — Bảo mật: bản demo đã có nền tảng, pilot cần kiểm soát truy cập

**Thông điệp:** Tách AI theo lĩnh vực giúp giới hạn công cụ; quyền truy cập của người dùng vẫn phải được xây dựng.

| ĐÃ CÓ trong code | Giới hạn hiện tại |
|---|---|
| SQLite chỉ đọc; model chọn truy vấn có sẵn và tham số được kiểm tra | Chưa có tài khoản, vai trò và lọc hàng/cột theo từng người dùng |
| AI Hiệu trưởng không nối trực tiếp kho tài liệu/CSDL; nhận kết quả AI con | Đây là cấu trúc điều phối, chưa phải cơ chế bảo mật theo chức danh |
| Danh sách gắn nhãn cá nhân gửi cho model dưới dạng đếm/tổng hợp | Chi tiết vẫn trả về màn hình; API hỏi đáp hiện chưa có kiểm tra quyền |
| Trang cài đặt có mật khẩu băm và phiên 30 phút; khóa API cấu hình | Mật khẩu cài đặt không bảo vệ dữ liệu hỏi đáp |
| Khi nhận diện CSDL thật, chỉ chọn nhà cung cấp được gắn `trusted` | Nhãn cấu hình không thay thế việc phê duyệt nhà cung cấp hay chính sách dữ liệu |

**ĐỀ XUẤT PILOT:** đăng nhập theo tài khoản trường; quyền phòng ban/chức trách; kiểm tra quyền ở API, nguồn dữ liệu và xuất CSV. Phê duyệt quyền AI Tổng hợp nhận dữ liệu liên phòng, chỉ cấp đúng phạm vi cần thiết.

**Lời nói:** “Chúng tôi phân biệt rất rõ chức năng đã chạy với điều kiện để dùng dữ liệu thật. Bản hiện tại đã hạn chế model bằng truy vấn chỉ đọc, và tách danh sách cá nhân khỏi dữ liệu truy vấn gửi cho model. Tuy nhiên, các tab Tuyển sinh, Đào tạo và Hiệu trưởng chưa phải phân quyền người dùng. Người có quyền mở trang hỏi đáp hiện chưa được kiểm tra theo chức trách. Vì vậy, bước pilot cần bổ sung đăng nhập và kiểm tra quyền ngay ở backend; không thể lấy mật khẩu trang cài đặt để kết luận dữ liệu của nhà trường đã được bảo vệ.”

**Chú thích không cần chiếu:** Bản demo công khai theo cấu hình triển khai được mô tả trong phiên này không phải môi trường nghiệm thu bảo mật. Không đưa mật khẩu, khóa API hay thông tin SSH lên slide.

## Slide D — Dữ liệu ở hệ thống trường; chỉ phần được duyệt mới ra dịch vụ AI

**Thông điệp:** Vị trí lưu CSDL và nơi xử lý AI là hai quyết định riêng.

**Toàn bộ slide là ĐỀ XUẤT PILOT.**

| Phân loại do trường phê duyệt | Ví dụ | Đường xử lý dự kiến |
|---|---|---|
| Công khai | Quy chế, thông báo đã công bố | Có thể dùng API được duyệt; tra nguồn và ngày hiệu lực |
| Nội bộ | Chỉ tiêu, thống kê vận hành chưa công bố | Theo quyền người dùng; API chỉ nhận phần đã được phép xuất |
| Hạn chế/nhạy cảm | Hồ sơ cá nhân, điểm, liên hệ, thông tin nhân sự | Giữ trong vùng kiểm soát của trường; xử lý nội bộ khi chính sách cấm ra ngoài |

**Luồng trên slide:**

`Người dùng đã xác thực → Kiểm tra quyền → CSDL/nguồn của trường → Cổng kiểm soát dữ liệu gửi ra → [AI nội bộ hoặc API được duyệt] → Kiểm tra đầu ra → Người có quyền`

- Trường quyết định trường dữ liệu nào được truy cập, tổng hợp hoặc xuất; kết quả AI con gửi lên AI Tổng hợp cũng phải qua kiểm tra quyền.
- Giảm dữ liệu gửi đi: chỉ trường cần thiết, đúng mục đích, đủ ngữ cảnh; không gửi toàn bộ CSDL.
- Gắn chính sách vào từng tác vụ. Việc “chỉ xử lý nội bộ” phải áp dụng xuyên suốt lập kế hoạch, tác tử, kiểm duyệt và tổng hợp.
- **Tác vụ nội bộ lỗi thì dừng/chờ hoặc chuyển model nội bộ khác đã được duyệt; không tự chuyển sang cloud.**

**Lời nói:** “Đặt database trong trường chưa có nghĩa dữ liệu không ra ngoài. Nếu ứng dụng lấy dữ liệu rồi gửi vào prompt của API, dữ liệu vẫn đi ra. Thiết kế đề xuất có một điểm kiểm soát rõ trước mọi lời gọi model. Một số câu hỏi chỉ cần thống kê đã được phê duyệt, còn hồ sơ nhạy cảm có thể phải xử lý hoàn toàn nội bộ. Quy tắc này phải theo cả lượt chạy, kể cả AI Hiệu trưởng khi nhận kết quả và cả model dự phòng. Hiện code mới có bộ lọc nhà cung cấp `trusted`, chưa có chính sách phân loại và tuyến nội bộ như slide này.”

## Slide E — Không gửi danh sách cá nhân vẫn cần chống suy ra danh tính

**Thông điệp:** Tổng hợp dữ liệu giảm mức phơi bày nhưng không tự động tạo ra dữ liệu ẩn danh.

**ĐÃ CÓ:** truy vấn đánh dấu cá nhân tách danh sách khỏi đầu vào model; model nhận số dòng, số người và tổng hợp. Khi lưu bản ghi của CSDL thật, code bỏ các dòng bảng trong sự kiện, kể cả sự kiện từ AI con.

**ĐỀ XUẤT PILOT:**

- Kiểm tra cả câu hỏi, đoạn tài liệu, tham số, bảng tổng hợp, báo cáo, log và dữ liệu phát lại; không chỉ xóa cột họ tên.
- Kiểm soát nhóm quá nhỏ; ví dụ gộp/ẩn nhóm dưới 5 người **chỉ là ngưỡng minh họa để trường chốt**, không phải bảo đảm ẩn danh.
- Kiểm tra khả năng suy ra ô bị ẩn từ tổng hoặc từ nhiều câu hỏi gần giống; áp dụng ẩn bổ sung hoặc chặn khi cần.
- Tải danh sách/CSV phải đúng quyền, đúng mục đích và có dấu vết; đặt hạn lưu, cơ chế xóa và quyền xem bản ghi.
- Xem nội dung tài liệu như dữ liệu không đáng tin; kiểm thử câu lệnh cài trong tài liệu để dụ AI bỏ quy tắc hoặc lấy sai nguồn.

**Lời nói:** “Một thống kê nói rằng có một sinh viên ở một lớp nhỏ thuộc nhóm cảnh báo vẫn có thể làm lộ người đó khi ghép với thông tin khác. Vì vậy, không gửi họ tên là cần thiết nhưng chưa đủ. Chúng tôi đề xuất kiểm soát cả nhóm nhỏ, phép suy ra từ tổng và nhiều truy vấn liên tiếp. Cũng cần bảo vệ lịch sử: hiện code bỏ dòng bảng khi ghi lại lượt chạy dữ liệu thật, nhưng câu hỏi và nội dung báo cáo vẫn có thể chứa thông tin nhạy cảm. Bản pilot phải có kiểm tra nội dung và thời hạn lưu cho toàn bộ đường đi dữ liệu.”

## Slide F — Vận hành an toàn là điều kiện trước khi mở rộng

**Toàn bộ hạng mục bên dưới là ĐỀ XUẤT PILOT, trừ nơi ghi rõ hiện trạng.**

| Lớp | Việc cần làm | Bằng chứng nghiệm thu |
|---|---|---|
| Mạng và máy chủ | TLS tới trình duyệt/API; CSDL không mở Internet; phân vùng mạng; tài khoản dịch vụ tối thiểu; cập nhật bản vá | Kiểm tra các cổng mở, quyền kết nối và cấu hình TLS |
| Danh tính và bí mật | SSO/tài khoản trường, MFA quản trị; kho secrets hoặc quyền file chặt; xoay/thu hồi khóa; không để khóa ở frontend/log/backup mở | Tài khoản sai quyền bị từ chối; diễn tập thu hồi khóa |
| Kiểm soát sử dụng | Hạn mức người dùng, giới hạn đồng thời/chi phí; quản trị chỉ từ kênh được phép | Thử quá hạn mức; người dùng thường không sửa cấu hình |
| Nhật ký và lưu trữ | Nhật ký ai hỏi/xem/xuất, nguồn và phiên bản dữ liệu; giảm/che nội dung nhạy cảm; thời hạn lưu | Truy ra một lượt truy cập; kiểm tra quyền xem và xóa log |
| Khôi phục và sự cố | Backup mã hóa; thử phục hồi; chọn RPO/RTO theo yêu cầu trường; quy trình cô lập, thu hồi khóa, đánh giá và khôi phục | Phục hồi thử thành công; diễn tập sự cố có người chịu trách nhiệm |

**Cổng chuyển sang pilot:** bộ thử phân quyền, xuất dữ liệu, chèn chỉ dẫn độc hại, định tuyến nội bộ và phục hồi đạt tiêu chí đã thống nhất; phòng CNTT và đơn vị chủ dữ liệu duyệt phạm vi.

**Lời nói:** “Bảo mật cần đi kèm người vận hành và bằng chứng kiểm tra. TLS chỉ bảo vệ đường truyền; không thay thế phân quyền. Backup chỉ có ý nghĩa khi phục hồi được. Nhóm dự án đề xuất thống nhất với phòng CNTT phạm vi triển khai, cách cấp quyền, thời hạn lưu và quy trình xử lý sự cố trước khi mở rộng. Hệ thống đã có một số lớp như che khóa và khóa cài đặt, nhưng bảng trên là kế hoạch hoàn thiện và nghiệm thu, không phải chứng nhận rằng bản demo hiện đã đáp ứng mọi mục.”

## Đối chiếu code dành cho người viết slide

- `backend/app/web.py:87–96`: nhận diện dữ liệu thật từ cờ synthetic của CSDL chính/AI con và lọc nhà cung cấp trusted; không phân loại nội dung câu hỏi/văn bản.
- `backend/app/web.py:150–220`: mật khẩu chỉ cho trang/API cài đặt; `/api/ask` không gọi `admin_only` và chưa có xác thực riêng.
- `backend/app/settings_auth.py`: PBKDF2-SHA256, 600.000 vòng; phiên máy chủ 1.800 giây; 5 lần sai trong 300 giây bị hạn chế. Chi tiết này dùng để đối chiếu, không cần chiếu hết.
- `backend/app/tools/data.py:62–87`: `for_model()` tách danh sách được gắn `ca_nhan`; vẫn gửi tham số và các nhóm đếm; không có ngưỡng nhóm nhỏ. `for_screen()` trả dữ liệu chi tiết.
- `backend/app/tools/data.py:119`: SQLite `mode=ro`; `run()` chỉ chọn truy vấn trong danh mục và kiểm tra tham số.
- `backend/app/workers.py:205–210`, `backend/app/graph.py:212`: kết quả model và bảng màn hình đi hai đường; bảng được gửi sau nghiệm thu. Đây chưa phải ACL.
- `backend/app/web.py:267–283`: xóa rows trong sự kiện bảng của bản ghi dữ liệu thật; vẫn ghi câu hỏi, báo cáo, history/ledger sau che khóa. Không khẳng định đã ẩn danh toàn bộ bản ghi.
- `backend/app/providers.py:32`, `backend/app/config.py:70`: cấu hình trả trạng thái có khóa thay vì khóa; che một số dạng API key. Không phải bộ lọc PII tổng quát.
- `backend/app/llm.py:157`: `trusted_only` lọc theo cờ của nhà cung cấp; phần chuyển dự phòng chưa có quy tắc local-only riêng.
- `backend/app/apps.py:129`: AI Tổng hợp có `sources=[]`, `data=None`, worker `analysis` và danh sách AI con; không có cơ chế suy ra quyền người dùng từ chức danh.
- `deploy/nginx-proxyllm.store.conf` còn Basic Auth trong file mẫu. Không lấy nó làm bằng chứng VPS hiện khóa truy cập vì phiên triển khai đã gỡ Basic Auth.

**Cách rút gọn nếu bộ slide dài:** giữ C và D ở phần chính; đưa E/F thành dự phòng nhưng người thuyết trình phải nói rõ kế hoạch vận hành và bảo vệ PII trong lời nói. Không gộp “ĐÃ CÓ” và “ĐỀ XUẤT PILOT” thành một danh sách không nhãn.
