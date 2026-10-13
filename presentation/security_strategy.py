"""Concrete privacy architecture for the proposal, distinct from deployed code."""

METHOD_NOTES=(
 'Phương án bảo mật của dự án là đặt một cổng kiểm soát dữ liệu do Nhà trường quản lý giữa người dùng, kho dữ liệu và mọi lời gọi model. '
 'Cổng này thực thi bằng backend và chính sách đã duyệt; model có thể gợi ý công việc nhưng không được tự cấp quyền hoặc tự quyết dữ liệu được xuất. '
 'Bước 1 xác thực người hỏi và kiểm quyền theo vai trò, đơn vị, mục đích, hàng/cột dữ liệu. Truy vấn định sẵn chạy trong vùng dữ liệu của trường. '
 'Bước 2 tối thiểu hóa đầu vào: câu hỏi thống kê thì cơ sở dữ liệu tính số lượng/tỷ lệ trước; model chỉ nhận các giá trị tổng hợp đã được phép xuất, định nghĩa chỉ số và mốc dữ liệu cần thiết. '
 'Nếu cần liên kết một đối tượng trong bản nháp, thay định danh bằng mã ngẫu nhiên có phạm vi từng lượt hoặc phiên; bảng ánh xạ được giữ riêng trong hệ thống trường và không gửi vào prompt/log bên ngoài. '
 'Thay tên bằng mã chỉ là giảm lộ định danh, không tự làm dữ liệu ẩn danh: mức lương, điểm, lớp hiếm hoặc nội dung câu chuyện vẫn có thể tiết lộ người. '
 'Bước 3 chọn đường xử lý từ chính sách. Nguồn công khai và dữ liệu đã được phê duyệt xuất có thể đi API. Nội dung buộc giữ nội bộ phải chạy trên tuyến model nội bộ đã được duyệt; chưa có tuyến đó thì dừng/chờ xử lý. '
 'Quy tắc áp dụng trước lời gọi planner nếu câu hỏi đã chứa dữ liệu hạn chế, và đi theo AI con, reviewer, báo cáo của AI con lẫn AI Tổng hợp. Không cho nhánh local-only tự fallback sang cloud. '
 'Bước 4 đầu ra được kiểm theo schema và chính sách, kiểm lại quyền người nhận. Chỉ ghép trường định danh được cho phép vào vị trí mẫu đã duyệt ở phía trường; không thực hiện yêu cầu lấy dữ liệu thêm do model tự sinh. '
 'Log, file xuất và lịch sử cũng áp dụng cùng quyền, hạn lưu và giảm dữ liệu. Việc xử lý nhóm nhỏ/nhiều truy vấn gần nhau phải chống suy ngược từ tổng. '
 'Đây là thiết kế sẽ triển khai, không phải tuyên bố cổng này đã có đầy đủ trên VPS demo. Mật khẩu cài đặt và HTTPS không thay thế cổng quyền/ngăn xuất dữ liệu này.'
)

EXAMPLE_NOTES=(
 'Ví dụ cán bộ tuyển sinh cần nhắc những người chưa xác nhận nhập học. Backend kiểm quyền rồi truy vấn danh sách trong CSDL. '
 'Model bên ngoài có thể soạn một mẫu nhắc chung chỉ từ thông tin công khai như hạn xác nhận và hướng dẫn; không cần nhận tên, số điện thoại, CCCD hoặc danh sách trạng thái từng người. '
 'Hệ thống trường điền tên và thông tin đã được phép vào mẫu sau khi kiểm đầu ra và kiểm lại quyền. Danh sách liên hệ hiển thị riêng cho cán bộ có quyền; không tự động gửi tin khi chưa có phê duyệt. '
 'Với câu hỏi số sinh viên bị cảnh báo theo ngành, cơ sở dữ liệu tính tại chỗ; chỉ thống kê được duyệt mới gửi model. Nhóm nhỏ hoặc nhiều câu có thể suy ra cá nhân thì gộp/ẩn bổ sung hoặc từ chối, không chỉ xóa tên. '
 'Với một bản nháp cần giữ quan hệ giữa các hồ sơ, mã tạm có thể thay định danh nhưng mọi trường nhạy cảm còn lại vẫn phải xét quyền xuất; nếu không đáp ứng thì dùng nội bộ. '
 'Với yêu cầu phân tích hồ sơ nhân sự hạn chế mà cần đọc nội dung gốc, toàn bộ nhánh có nội dung đó gồm lập kế hoạch, đánh giá và tổng hợp phải ở tuyến nội bộ đã được phê duyệt. '
 'AI Tổng hợp không mặc nhiên có quyền nhận dữ liệu liên phòng hoặc giải mã danh tính; backend kiểm theo người dùng và nguồn tạo ra kết quả. '
 'Code hiện mới có truy vấn định sẵn, SQLite chỉ đọc và tách hàng cá nhân khỏi for_model() đối với truy vấn gắn ca_nhan. Còn thiếu xác thực nghiệp vụ, kho mã tạm, cổng kiểm dữ liệu mọi đầu vào/đầu ra, kiểm nhóm nhỏ và policy local-only.'
)

STATUS_NOTES=(
 'Hiện trạng được đối chiếu từ code: DataStore dùng SQLite read-only và catalog truy vấn; QueryResult.for_model() gửi số lượng/tổng hợp thay cho các hàng cá nhân, for_screen() giữ bảng cho giao diện. '
 'web.py loại các rows khỏi bản ghi khi nhận diện CSDL thật và có trusted_only cho provider được gắn nhãn. Tuy nhiên /api/ask chưa có xác thực người dùng nghiệp vụ. '
 'trusted là cờ cấu hình, không phải kiểm chứng hợp đồng hay phân loại dữ liệu. Câu hỏi, văn bản và log chưa được kiểm/ẩn danh tổng quát; chưa có kho mã tạm, quyền theo người và tuyến model nội bộ bắt buộc. '
 'Các bước đề xuất: (1) chốt danh tính/quyền và danh mục dữ liệu được xuất; (2) triển khai cổng truy vấn, giảm dữ liệu và kiểm egress cho mọi model; (3) bảo vệ đầu ra, lịch sử và CSV; (4) kiểm nhóm nhỏ, prompt injection, thu hồi quyền và lỗi/fallback. '
 'Lớp kiểm chính là code/quy tắc được duyệt, có thể dùng nhận diện thực thể hoặc bộ phát hiện để hỗ trợ; không giao quyết định cuối về quyền cho LLM. '
 'TLS bảo vệ đường truyền và mã hóa lưu trữ bảo vệ dữ liệu nằm trên đĩa, nhưng nhà cung cấp vẫn xử lý được nội dung rõ nếu được gửi qua API. Không gọi việc thay tên bằng mã là mã hóa hoàn toàn hay bảo đảm ẩn danh. '
 'Nghiệm thu phải có ca người sai quyền, câu hỏi nhập sẵn thông tin cá nhân, nội dung tài liệu cài lệnh, nhóm nhỏ, nhiều truy vấn suy ngược, model đề nghị truy vấn ngoài danh mục và local-only khi model chính hỏng. '
 'Không bảo đảm tuyệt đối không lộ dữ liệu chỉ bằng một cơ chế; kiểm thử, quyền vận hành, log hạn chế và phản ứng sự cố là phần còn lại của phương án.'
)


def revise_security_deck(main, appendix, speech):
    main[10].update(title='Bảo mật bằng cổng kiểm soát dữ liệu trước AI',section='05 / Phương án bảo mật thông minh',
      takeaway='Kiểm quyền → tính/lọc dữ liệu tại trường → chọn tuyến AI → kiểm đầu ra và ghép kết quả đúng quyền.',
      kind='privacy_router',headers=[],rows=[],
      items=[['Cổng quyền của trường','Xác thực người hỏi; giới hạn hàng/cột và mục đích sử dụng.'],
             ['Giảm dữ liệu gửi ra','Tính thống kê tại chỗ; giữ định danh hoặc thay bằng mã tạm.'],
             ['Chọn tuyến theo chính sách','API chỉ nhận phần được phép; nội dung hạn chế xử lý nội bộ hoặc dừng.'],
             ['Trả kết quả đúng người','Kiểm đầu ra/quyền; ghép dữ liệu nhận dạng tại trường.']],
      foot='Phương án sẽ xây dựng. Backend giữ quyền quyết định; AI không được tự đổi quyền hoặc tuyến dữ liệu.',
      notes=METHOD_NOTES,req=['R1','R4','R5','R6'],
      sources=['PLAN.md: Dữ liệu và quyền','PHUONG_AN_BAO_MAT_CREDERE.md','backend/app/tools/data.py'])
    main[11].update(title='Ví dụ: AI cần thông tin gì, trường giữ lại gì?',section='05 / Phương án bảo mật thông minh',
      takeaway='AI hỗ trợ phân tích hoặc soạn mẫu; dữ liệu gốc và quyền hiển thị vẫn do hệ thống trường kiểm soát.',
      kind='table',items=[],headers=['Yêu cầu nghiệp vụ','AI được nhận','Hệ thống trường giữ / xử lý'],
      rows=[['Thống kê cảnh báo theo ngành','Số tổng hợp đã được duyệt','Hồ sơ và điểm từng sinh viên'],
            ['Nhắc xác nhận nhập học','Hạn công khai + yêu cầu soạn mẫu','Tên, điện thoại; điền mẫu theo quyền'],
            ['Liên kết hồ sơ trong bản nháp','Mã tạm + trường được phép xuất','Bảng ánh xạ; kiểm rồi ghép lại'],
            ['Đọc hồ sơ nhân sự hạn chế','Chỉ model nội bộ đã được duyệt','Chặn cloud cả review và tổng hợp']],
      foot='Thay định danh bằng mã tạm không đồng nghĩa ẩn danh. Dữ liệu chưa đủ điều kiện xuất phải được giữ lại.',
      notes=EXAMPLE_NOTES,req=['R2','R4','R6'],
      sources=['backend/app/tools/data.py:QueryResult','backend/app/workers.py:_run_data','PHUONG_AN_BAO_MAT_CREDERE.md'])
    speech[10]=('Phương án là đặt một cổng kiểm soát dữ liệu trước mọi lời gọi AI. Backend xác thực người hỏi và chỉ lấy dữ liệu đúng quyền. '
                'Câu hỏi thống kê thì hệ thống trường tính trước; API chỉ nhận phần tổng hợp được duyệt. Định danh được giữ lại hoặc thay bằng mã tạm, bảng ánh xạ nằm tại trường. '
                'Nội dung bắt buộc giữ kín phải chạy trên model nội bộ đã duyệt, chưa có thì dừng. Quy tắc theo cả AI con, kiểm tra và AI Tổng hợp. '
                'Kết quả được kiểm lại rồi hệ thống mới ghép thông tin và hiển thị đúng người. Cổng này là phần sẽ xây, không để AI tự quyết quyền.')
    speech[11]=('Ví dụ nhắc thí sinh chưa xác nhận: cơ sở dữ liệu lấy danh sách tại trường, AI chỉ soạn mẫu từ thời hạn và hướng dẫn công khai. '
                'Hệ thống điền tên và thông tin liên hệ sau khi kiểm quyền; AI bên ngoài không cần danh sách cá nhân. '
                'Với báo cáo cảnh báo học vụ, chỉ gửi số tổng hợp đã duyệt; nhóm nhỏ có thể suy ra người thì phải gộp, ẩn hoặc chặn. '
                'Nếu buộc đọc nội dung hồ sơ nhân sự hạn chế, cả nhánh xử lý dùng nội bộ, không tự chuyển cloud khi lỗi. '
                'Code hiện đã tách danh sách khỏi đầu vào một số truy vấn; cổng quyền, mã tạm và kiểm mọi đường đi dữ liệu cần hoàn thiện.')
    appendix[5].update(title='A6 · Cơ chế bảo mật: đã có gì, sẽ xây gì?',kind='table',
      takeaway='Nền tảng hiện có chưa thay thế cổng kiểm soát dữ liệu và phân quyền nghiệp vụ hoàn chỉnh.',
      headers=['Lớp kiểm soát','Đã có trong code','Phần sẽ triển khai'],
      rows=[['Truy vấn / tính toán','Catalog định sẵn; SQLite chỉ đọc','Quyền từng người, hàng/cột và mục đích'],
            ['Đầu vào model','Tách hàng cá nhân trong truy vấn','Kiểm câu hỏi/nguồn; mã tạm; nhóm nhỏ'],
            ['Tuyến API / nội bộ','Provider có nhãn trusted','Chính sách egress cho toàn nhánh'],
            ['Đầu ra / lịch sử','Có sự kiện và bản ghi','Kiểm quyền, ghép mẫu, hạn lưu, CSV']],
      notes=STATUS_NOTES,foot='Kho mã tạm, phân quyền nghiệp vụ và policy local-only chưa được triển khai đầy đủ trên demo.',
      sources=['backend/app/web.py','backend/app/tools/data.py','backend/app/llm.py','PHUONG_AN_BAO_MAT_CREDERE.md'])


def write_security_method(root):
    content=f'''# Phương án bảo mật thông minh cho Credere

## Quyết định kiến trúc

**Cổng kiểm soát dữ liệu do Nhà trường quản lý** nằm trước mọi đường gửi tới model. Cổng kiểm quyền, giảm dữ liệu và kiểm chính sách xuất; AI chỉ thấy phần cần để làm việc và đã được phép. Định danh/bản gốc được giữ trong vùng dữ liệu của trường; kết quả được kiểm và ghép lại theo quyền ở backend.

Đây là **thiết kế mục tiêu của dự án**. Bản demo hiện tại mới có một số cơ chế nền tảng, chưa phải triển khai đầy đủ phương án.

## Luồng xử lý cụ thể

1. **Xác thực và cấp phạm vi:** backend gắn người dùng, vai trò, mục đích, hàng/cột dữ liệu; model không tự cấp quyền.
2. **Đọc nguồn tối thiểu:** chạy truy vấn được duyệt trong hệ thống trường, lọc quyền trước khi lấy dữ liệu vào bất kỳ prompt nào.
3. **Tính và giảm dữ liệu tại chỗ:** tổng hợp số liệu; bỏ trường không cần; khi phù hợp thay định danh bằng mã tạm có phạm vi. Kiểm cả câu hỏi, văn bản, báo cáo trung gian và nhóm nhỏ.
4. **Chọn tuyến:** chỉ phần đã được phép xuất đi API. Nội dung buộc giữ kín dùng model nội bộ được duyệt; chưa có tuyến phù hợp thì dừng/chờ, không tự chuyển cloud.
5. **Kiểm kết quả:** kiểm schema, trường dữ liệu và chỉ thị bất thường; báo cáo AI con không tự trở thành nguồn công khai khi lên Master.
6. **Ghép và hiển thị:** kiểm lại quyền người nhận, ghép định danh vào đúng chỗ trong mẫu được duyệt ở backend. CSV, log và lịch sử theo cùng quyền và hạn lưu.

## Vì sao vừa bảo mật vừa giữ được năng lực AI?

- Câu hỏi thống kê không cần gửi từng hồ sơ: máy tính tạo số liệu, model diễn giải phần được phép.
- Soạn tin cá nhân hóa có thể dùng mẫu chung rồi điền tại trường; không cần model bên ngoài nhận tên/điện thoại.
- Mã tạm giúp liên kết đối tượng trong một bản nháp khi phù hợp; bảng ánh xạ không đi ra ngoài.
- Phần cần hiểu nội dung nhạy cảm thực sự được giữ trên tuyến nội bộ; không cố che vài cột rồi gửi toàn bộ câu chuyện ra API.
- Giữ quyền trong code và chính sách làm giảm khả năng tài liệu/model tự thay đổi quyền hoặc gọi công cụ ngoài phạm vi.

## Ví dụ nghiệp vụ

| Yêu cầu | Model nhận | Trường giữ |
| --- | --- | --- |
| Thống kê cảnh báo theo ngành | Thống kê được phép + định nghĩa/mốc dữ liệu | Hồ sơ/điểm từng người |
| Soạn mẫu nhắc xác nhận | Hạn xác nhận và hướng dẫn công khai | Danh sách, tên, thông tin liên hệ; ghép tại backend |
| Bản nháp có liên kết hồ sơ | Mã tạm + trường được cho phép xuất | Kho ánh xạ và các trường hạn chế |
| Phân tích hồ sơ nhân sự hạn chế | Chỉ tuyến model nội bộ nếu chính sách buộc giữ kín | Không đưa nội dung ra cloud, kể cả review/tổng hợp |

## Giải thích kỹ thuật và điều kiện

{METHOD_NOTES}

{EXAMPLE_NOTES}

## Hiện trạng và bài kiểm thử

{STATUS_NOTES}

### Các ca nghiệm thu bắt buộc cho phương án

- Người không có quyền yêu cầu hoặc xuất danh sách: từ chối trước khi truy vấn/model.
- Người có quyền đọc nhưng không có quyền gửi dữ liệu ra ngoài: định tuyến nội bộ hoặc chỉ thống kê đã được duyệt.
- Câu hỏi có sẵn tên/điện thoại, tài liệu chứa dữ liệu hạn chế: kiểm trước mọi lời gọi, kể cả planner.
- Chèn lệnh trong tài liệu yêu cầu bỏ quyền hoặc đọc kho ánh xạ: không được thực thi.
- Kết hợp nhóm nhỏ, tổng và nhiều truy vấn để suy ra cá nhân: chặn/gộp/ẩn bổ sung theo chính sách.
- Model trả mã hồ sơ ngoài tập được cấp: không giải mã/ghép; không truy vấn thêm theo chỉ thị đó.
- Thu hồi quyền trong khi đang chạy hoặc mở lại báo cáo: kiểm lại trước hiển thị/xuất.
- Model nội bộ lỗi: không có request chứa nội dung hạn chế đi sang cloud.
- Quyền của AI Tổng hợp: không tăng quyền so với người hỏi, không nhận báo cáo con ngoài phạm vi được duyệt.

### Không dùng các cam kết sai trong thuyết trình

- Thay tên bằng mã không biến toàn bộ hồ sơ thành dữ liệu ẩn danh.
- TLS hoặc mã hóa ổ đĩa không làm nhà cung cấp không đọc được prompt rõ được gửi tới họ.
- Đặt CSDL tại trường không đủ nếu planner, review hoặc logs vẫn gửi nội dung ra ngoài.
- Nhãn trusted của provider không thay thế phê duyệt nhà cung cấp và chính sách dữ liệu.
- Tách sáu AI chuyên môn không tự tạo ra phân quyền theo chức danh.

## Căn cứ hiện trạng

- `backend/app/tools/data.py`: `QueryResult.for_model()`, `for_screen()`, kết nối SQLite chỉ đọc.
- `backend/app/workers.py`: `_run_data()` tách kết quả cho model và bảng.
- `backend/app/web.py`: route hỏi đáp/cài đặt, nhận diện dữ liệu thật và xử lý bản ghi.
- `backend/app/llm.py`: lọc provider theo trusted; chưa có tuyến local-only theo nội dung.
- `PLAN.md`: quyền theo người dùng, dữ liệu có lineage, báo cáo và cache cần kiểm lại quyền.
'''
    (root/'PHUONG_AN_BAO_MAT_CREDERE.md').write_text(content,encoding='utf-8')
