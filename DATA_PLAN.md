# Kế hoạch dữ liệu cho đề tài Credere

Cập nhật: 25/09/2026. Áp dụng cho đề tài 3 tháng (10–12/2026) theo [phiếu đề xuất](./De_xuat_de_tai_SV_2026-2027_Credere.docx) và [PLAN.md](./PLAN.md). Tên đơn vị lấy từ trang chủ nau.edu.vn ngày 25/09/2026.

**Nguyên tắc.**

- Chỉ xin dữ liệu phục vụ ba lĩnh vực của đề tài (Đào tạo, NCKH, HTQT) và kịch bản NCKH. Lấy nguồn công khai trước, chỉ xin phần không có công khai.
- Không xin dữ liệu cá nhân: hồ sơ, điểm, lịch cá nhân của sinh viên; lương, hồ sơ cán bộ. Kiểm thử phân quyền dùng tài khoản và hồ sơ mô phỏng. Như vậy đề tài không phải xử lý dữ liệu cá nhân theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15.
- Mỗi tài liệu phải có đơn vị sở hữu, số hiệu hoặc phiên bản, ngày hiệu lực và mức truy cập do đơn vị xác nhận.
- Tài liệu nội bộ chỉ được gửi tới dịch vụ mô hình bên ngoài (API) khi đơn vị sở hữu đồng ý, ghi nhận bằng email. Không đồng ý thì không nạp tài liệu đó vào hệ thống.

## 1. Cần nhà trường cung cấp

Ưu tiên A là bắt buộc để đạt chỉ tiêu trong phiếu đề xuất; B là nên có; C để sau đề tài.

**Khoa quản lý đề tài và giảng viên hướng dẫn.**

| # | Nội dung | Dùng để | Ưu tiên |
| --- | --- | --- | --- |
| K1 | Xác nhận đề tài và phạm vi dữ liệu; giấy giới thiệu làm việc với các phòng | Điều kiện để các phòng cung cấp tài liệu | A |
| K2 | Giới thiệu 3 người thẩm định, mỗi lĩnh vực một người; mỗi người duyệt khoảng 20 tình huống, dự kiến 2–3 giờ trong tháng 11 | Đáp án chuẩn cho bộ 60 tình huống | A |
| K3 | Chốt ngưỡng chỉ tiêu và tiêu chí chấm báo cáo | Nghiệm thu | A |

**Phòng Quản lý đào tạo.**

| # | Nội dung | Dùng để | Ưu tiên |
| --- | --- | --- | --- |
| D1 | Xác nhận Quy chế đào tạo (Quyết định 620 ngày 26/06/2025, đã có trên website) còn hiệu lực; các văn bản sửa đổi và quy định chuyển tiếp cho các khóa trước | Nguồn chính của tác tử Đào tạo | A |
| D2 | Chương trình đào tạo và chuẩn đầu ra bản mới nhất của 2–3 ngành mẫu, nếu bản trên website chưa đủ | Câu hỏi về chương trình, chuẩn đầu ra, tín chỉ | A |
| D3 | Quy định tổ chức thi; kế hoạch đào tạo năm học 2026–2027 | Câu hỏi về thi, lịch năm học | B |
| D4 | Số liệu tổng hợp không định danh 2023–2025: số sinh viên theo ngành/khóa, số tốt nghiệp | Bảng tính của tác tử phân tích | B |

**Phòng Quản lý Khoa học và Hợp tác quốc tế** (một phòng phụ trách cả hai lĩnh vực, nên chỉ cần một đầu mối).

| # | Nội dung | Dùng để | Ưu tiên |
| --- | --- | --- | --- |
| N1 | Quy định quản lý hoạt động khoa học và công nghệ: đề tài cấp trường, sinh viên NCKH, khen thưởng công bố | Nguồn chính của tác tử NCKH | A |
| N2 | Danh mục đề tài 2023–2025: tên, cấp, lĩnh vực, năm, kinh phí, trạng thái nghiệm thu. Không cần thông tin cá nhân ngoài tên chủ nhiệm đã công khai | Kịch bản NCKH, bảng so sánh | A |
| N3 | Danh mục công bố 2023–2025: bài báo, tạp chí hoặc hội thảo, năm, loại chỉ mục (quốc tế/trong nước), đơn vị | Số liệu “kết quả NCKH 3 năm qua” | A |
| N4 | Báo cáo tổng kết khoa học và công nghệ 2023–2025; kế hoạch năm tới | Đối chiếu số liệu, lộ trình | B |
| N5 | Các hoạt động hoặc đề tài có ứng dụng AI trong nghiên cứu tại trường, nếu có | Ứng viên cho 3 trường hợp so sánh | B |
| H1 | Danh sách đối tác và thỏa thuận hợp tác còn hiệu lực: tên, quốc gia, lĩnh vực, thời hạn | Nguồn chính của tác tử HTQT | A |
| H2 | Quy định về đoàn ra, đoàn vào, trao đổi sinh viên và giảng viên, học bổng quốc tế | Câu hỏi về thủ tục HTQT | A |
| H3 | Chương trình liên kết, học bổng đang mở; báo cáo tổng kết HTQT 2023–2025 | Câu hỏi tổng hợp, liên lĩnh vực | B |

**Phòng Kế hoạch – Tài chính.**

| # | Nội dung | Dùng để | Ưu tiên |
| --- | --- | --- | --- |
| T1 | Phần quy chế chi tiêu nội bộ về định mức chi khoa học và công nghệ: chi đề tài, thuê chuyên gia, hội thảo | Ước tính chi phí năm tới trong kịch bản NCKH | A |

Không xin lương, thu nhập hay dự toán chi tiết của đơn vị.

**Các đơn vị khác.**

| # | Đơn vị | Nội dung | Ưu tiên |
| --- | --- | --- | --- |
| O1 | Phòng Tổ chức – Hành chính | Cơ cấu tổ chức, chức năng nhiệm vụ các đơn vị, nếu website chưa đủ; dùng để thiết kế vai trò | B |
| O2 | Mỗi đơn vị giao tài liệu | Xác nhận mức truy cập và việc được gửi tới API mô hình cho từng tài liệu, theo bảng mẫu ở mục 4 | A |
| O3 | Trung tâm Số và Học liệu | Tài khoản SSO thử nghiệm, máy chủ hoặc chỗ lưu trữ của trường | C |

## 2. Nguồn tự thu thập, không cần xin

| Nguồn | Nội dung |
| --- | --- |
| nau.edu.vn | Quy chế đào tạo, Chương trình đào tạo, Kế hoạch đào tạo, Khoa học công nghệ, Đề tài khoa học, Tạp chí khoa học, trang các phòng ban, tuyển sinh; hoithao.nau.edu.vn |
| Dự án NAU-AI | 8 trang biểu mẫu/dịch vụ và Quyết định 620 đã đọc trong tháng 9/2026. Dùng lại danh sách URL nhưng phải tải và đọc lại bản mới |
| OpenAlex, Crossref, arXiv | Số liệu công bố về ứng dụng AI trong nghiên cứu 2023–2025 và công bố của trường nếu có trong chỉ mục. OpenAlex cần API key miễn phí |
| Văn bản pháp luật công khai | Luật, nghị định, thông tư về khoa học và công nghệ; văn bản định mức chi của Nhà nước (dùng khi thiếu T1) |

## 3. Cách tổ chức lấy dữ liệu

**Quy trình cho mỗi yêu cầu.**

1. Soạn phiếu đề nghị theo mẫu ở mục 6, ghi rõ mục cần, mục đích, cách lưu và thời hạn xóa.
2. Giảng viên hướng dẫn hoặc khoa ký giới thiệu; gửi email tới đầu mối của phòng, đồng gửi giảng viên hướng dẫn.
3. Chỉ nhận file qua email trường hoặc thư mục chia sẻ do trường cấp; không nhận qua Zalo, Messenger hay USB không rõ nguồn.
4. Ghi vào sổ nhận dữ liệu ngay khi nhận (mục 4).
5. Kiểm tra: đúng phiên bản và còn hiệu lực; là văn bản hay bản scan cần OCR; có dữ liệu cá nhân không. File có dữ liệu cá nhân không cần thiết thì đề nghị đơn vị gửi lại bản đã lược bỏ, không lưu bản gốc.
6. Đơn vị xác nhận mức truy cập và việc được gửi tới API mô hình.

**Lịch theo đề tài 3 tháng.**

| Thời gian | Việc | Kết quả |
| --- | --- | --- |
| Tuần 1 tháng 10 | Xin giấy giới thiệu (K1); gửi phiếu tới Phòng Quản lý đào tạo, Phòng Quản lý Khoa học và HTQT, Phòng Kế hoạch – Tài chính; tự thu thập nguồn công khai; đăng ký key OpenAlex | Phiếu đã gửi; bản đầu kho công khai |
| Tuần 2 | Gặp đầu mối, nhận đợt 1, nhắc mục còn thiếu | Sổ nhận dữ liệu có đợt 1 |
| Tuần 3 | Kiểm tra chất lượng, xin bổ sung; chốt danh mục 20–40 tài liệu và mức truy cập | documents.csv đã chốt |
| Tuần 4 | Hạn chót nhận mục A; mục chưa có chuyển sang phương án thay thế | Danh sách mục thiếu và cách xử lý |
| Tháng 11 | Soạn 60 tình huống nháp; gửi người thẩm định giữa tháng; nhận lại cuối tháng (K2) | Bộ nghiệm thu đã duyệt |
| Tháng 12 | Chỉ nhận bổ sung nhỏ; khóa phiên bản dữ liệu trước khi chạy đánh giá chính thức | Dữ liệu đã khóa, có checksum |

**Phương án khi không nhận được.**

| Mục thiếu | Thay thế | Ghi trong báo cáo |
| --- | --- | --- |
| N2, N3 | Trang “Đề tài khoa học”, “Tạp chí khoa học” công khai và OpenAlex | Số liệu chỉ phản ánh phần công khai |
| T1 | Văn bản định mức chi khoa học và công nghệ của Nhà nước đang có hiệu lực | Chi phí là ước tính theo giả định |
| H1, H2 | Tin bài HTQT công khai trên website | Phạm vi HTQT bị thu hẹp |
| K2 | Giảng viên hướng dẫn duyệt đáp án | Chưa có thẩm định của đơn vị chuyên môn |
| O2 | Coi tài liệu là nội bộ đơn vị và không gửi tới API | Tài liệu bị loại khỏi hệ thống |

## 4. Cách lưu trữ

**Vị trí.** Đặt ở `D:\credere-data\`, ngoài OneDrive và ngoài git. Không đồng bộ lên OneDrive hay Google Drive cá nhân. Bật BitLocker cho ổ D (có sẵn trên Windows 10 Pro), hoặc dùng một ổ mã hóa riêng cho phần nội bộ. Mỗi tuần sao lưu một bản mã hóa ra ổ ngoài. Chỉ hai thành viên nhóm được truy cập.

**Dung lượng máy cần xử lý trước.** Kiểm tra ngày 25/09/2026: ổ C còn khoảng 3,5 GB (dùng 99%), ổ D còn khoảng 16 GB. Bản thân dữ liệu tài liệu nhỏ, dưới 1 GB. Nhưng WSL2, Docker image, thư viện Python và model embedding/reranker theo PLAN.md ước tính cần thêm khoảng 20 GB trở lên. Cần giải phóng dung lượng trước M-1.

**Cấu trúc thư mục.**

```text
D:\credere-data\
├─ 00_quan-ly\            giấy giới thiệu, email xác nhận, so-nhan-du-lieu.csv, muc-truy-cap.csv
├─ 01_goc\                file nguyên bản, chỉ đọc, không sửa
│  ├─ cong-khai\<nguon>\<ma-tai-lieu>\<phien-ban>\
│  └─ noi-bo\<don-vi>\<ma-tai-lieu>\<phien-ban>\
├─ 02_danh-muc\           documents.csv: thông tin từng tài liệu
├─ 03_xu-ly\              văn bản trích xuất, đoạn (JSONL); tạo lại được từ 01_goc
├─ 04_danh-gia\
│  ├─ poc-20\             20 câu thử nghiệm, được dùng để chỉnh hệ thống
│  └─ nghiem-thu-60\      60 tình huống đã duyệt; không dùng để chỉnh prompt
├─ 05_mo-phong\           tài khoản, hồ sơ mô phỏng
└─ 06_ket-qua\            kết quả chạy đánh giá, trace đã xuất
```

Mã tài liệu theo lĩnh vực: `DT-001`, `NCKH-001`, `HTQT-001`, `TC-001`, `CK-001` (nguồn công khai chung). Tên file: `<don-vi>_<loai>_<so-hieu>_<ngay-ban-hanh>.<duoi>`, ví dụ `qldt_quyche_620_2025-06-26.pdf`. Tài liệu sửa đổi là phiên bản mới trong thư mục mới, không ghi đè bản cũ.

**Sổ nhận dữ liệu** (`00_quan-ly\so-nhan-du-lieu.csv`): ma_yeu_cau, don_vi, dau_moi, noi_dung, uu_tien, ngay_gui, han, ngay_nhan, ma_tai_lieu, trang_thai, ghi_chu.

**Danh mục tài liệu** (`02_danh-muc\documents.csv`): ma_tai_lieu, tieu_de, linh_vuc, don_vi_so_huu, loai_van_ban, so_hieu, ngay_ban_hanh, ngay_hieu_luc, ngay_het_hieu_luc, phien_ban, thay_the_cho, nguon (URL hoặc đơn vị giao), ngay_thu_thap, nguoi_giao, dinh_dang, sha256, muc_truy_cap, duoc_gui_api, chat_luong (văn bản/scan), trang_thai (chờ kiểm tra/đang dùng/hết hiệu lực/loại bỏ), ghi_chu.

**Mức truy cập** (đơn vị xác nhận trong `muc-truy-cap.csv`).

| Mức | Ý nghĩa | Ai được xem trong hệ thống |
| --- | --- | --- |
| P0 – Công khai | Đã đăng công khai | Mọi người, kể cả khách |
| P1 – Nội bộ trường | Dùng trong trường | Cán bộ, giảng viên, sinh viên đã đăng nhập |
| P2 – Nội bộ đơn vị | Chỉ đơn vị sở hữu | Đơn vị sở hữu, Ban Giám hiệu, người được cấp riêng |
| P3 – Hạn chế | Không phục vụ đề tài | Không nạp vào hệ thống |

Vai trò mô phỏng để kiểm thử quyền: khách, sinh viên, giảng viên, chuyên viên Phòng Quản lý đào tạo, chuyên viên Phòng Quản lý Khoa học và HTQT, Ban Giám hiệu. Mười tình huống “sai quyền” trong bộ nghiệm thu dựa trên các mức này.

**Nạp vào hệ thống.** Hệ thống chỉ đọc từ `01_goc` và `documents.csv`: Docling trích văn bản → kiểm tra chất lượng → chia đoạn → gắn mã tài liệu, phiên bản, ngày hiệu lực, mức truy cập → PostgreSQL → chỉ mục. Bằng chứng trong báo cáo dẫn về mã tài liệu, phiên bản và vị trí (trang, mục). Nguồn ngoài lưu thêm URL, thời điểm truy xuất và bản sao phản hồi gốc (trang HTML, JSON của OpenAlex) để chạy lại được.

**Bảo mật và vòng đời.**

- Khóa API và mật khẩu nằm trong file `.env` riêng, không để trong thư mục dữ liệu, không đưa lên git.
- Kho mã nguồn chỉ chứa bộ câu hỏi không trích nội dung nội bộ. Nếu kho mã nguồn công khai thì `04_danh-gia\nghiem-thu-60` không được đưa lên.
- Khóa phiên bản dữ liệu trước đánh giá chính thức bằng checksum trong `documents.csv`.
- Sau nghiệm thu, trả lại hoặc xóa dữ liệu nội bộ theo thỏa thuận với từng đơn vị. Chỉ giữ danh mục và kết quả đánh giá không chứa nội dung nội bộ.

## 5. Bộ tối thiểu nếu thiếu thời gian

Đủ để giữ các chỉ tiêu trong phiếu đề xuất: D1, D2 (Đào tạo); N1, N2, N3 (NCKH); H1, H2 (HTQT); T1 (chi phí); K1, K2, K3 và O2 cho các tài liệu nội bộ. Các mục B chỉ làm tăng độ phủ, có thể bỏ.

## 6. Mẫu phiếu đề nghị cung cấp tài liệu

> **Kính gửi:** [tên phòng]
>
> Nhóm sinh viên [họ tên], lớp [lớp], Khoa [khoa], đang thực hiện đề tài NCKH sinh viên “Xây dựng hệ thống trí tuệ nhân tạo đa tác tử theo kiến trúc điều phối – thực thi có kiểm chứng nguồn, hỗ trợ tra cứu, phân tích và lập báo cáo tại Trường Đại học Nghệ An” (giảng viên hướng dẫn: [họ tên]).
>
> Nhóm kính đề nghị Quý Phòng hỗ trợ cung cấp các tài liệu sau:
>
> 1. [mã – nội dung, ví dụ: N2 – Danh mục đề tài khoa học và công nghệ 2023–2025]
> 2. …
>
> **Mục đích:** chỉ dùng để thử nghiệm và đánh giá hệ thống trong đề tài; không công bố nội dung tài liệu nội bộ.
>
> **Lưu trữ:** trên máy có mã hóa của nhóm, ngoài dịch vụ đồng bộ cá nhân; xóa hoặc hoàn trả sau khi nghiệm thu (dự kiến tháng 12/2026).
>
> **Đề nghị Quý Phòng cho biết với từng tài liệu:** (a) mức truy cập: công khai, nội bộ trường, nội bộ đơn vị, hay không được sử dụng; (b) có đồng ý để nội dung được gửi tới dịch vụ mô hình AI bên ngoài trong quá trình thử nghiệm hay không. Nhóm dùng mô hình GPT của OpenAI thông qua một cổng API trung gian (api.aixingialaire.shop); nội dung sẽ đi qua cổng này trước khi tới nhà cung cấp mô hình.
>
> Nhóm không đề nghị cung cấp dữ liệu cá nhân của sinh viên hoặc cán bộ. Thời hạn mong muốn: [ngày].
>
> Liên hệ: [điện thoại, email]. Trân trọng cảm ơn.
