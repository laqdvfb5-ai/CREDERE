"""AI Tuyển sinh: trợ lý cho cán bộ Trung tâm Tuyển sinh và Truyền thông (văn bản công khai; dữ liệu tuyển sinh ở giai đoạn 2)."""
from ..config import DATA_ROOT
from ..tools.data import DataStore
from .tuyen_sinh_queries import QUERIES

KEY = "tuyen_sinh"
TEN = "AI Tuyển sinh"
DON_VI = "Trung tâm Tuyển sinh và Truyền thông"
NGUOI_DUNG = "cán bộ Trung tâm Tuyển sinh và Truyền thông"
LINH_VUC = ("tuyển sinh: chỉ tiêu, phương thức, tổ hợp, điểm chuẩn các năm, học phí, học bổng, lịch và thủ tục tuyển sinh, nhập học; "
            "số liệu mùa tuyển sinh 2026: nguyện vọng, lọc ảo, trúng tuyển, xác nhận nhập học theo ngành, chỉ tiêu còn lại")
SOURCE_ID = "CSDL-TS"


def open_store(path) -> DataStore:
    return DataStore(path, QUERIES, SOURCE_ID, "tuyển sinh 2026", person="thí sinh")


DEFAULT_SOURCES = DATA_ROOT / "03_xu-ly" / "tuyen_sinh" / "sources.json"
DEFAULT_DATA = DATA_ROOT / "03_xu-ly" / "tuyen_sinh" / "gia_lap" / "tuyen_sinh_2026_gia_lap.sqlite"
WORKERS = {"tuyen_sinh", "analysis"}  # giai đoạn 1: văn bản công khai; bộ thử 30 câu và 10 tình huống chạy với tập này
# Hai câu về dữ liệu cá nhân đổi theo giai đoạn: chưa nối dữ liệu thì không tra; đã nối thì danh sách do hệ thống hiển thị cho cán bộ
PERSONAL_SYNTH = ("Không cung cấp dữ liệu cá nhân của thí sinh trong mọi trường hợp, vì đó là nguyên tắc "
                  "của hệ thống chứ không phải vì thiếu dữ liệu. ")
PERSONAL_SYNTH_DATA = ("Không tự viết ra dữ liệu cá nhân của thí sinh (tên, số điện thoại, CCCD); danh sách từng thí sinh do hệ thống "
                       "hiển thị riêng cho cán bộ có quyền. ")
PERSONAL_PLAN = ("Yêu cầu về dữ liệu cá nhân của thí sinh (danh sách, số điện thoại, số báo danh) thì chỉ lập một nhiệm vụ "
                 "kiểm tra nguồn công khai có quy định liên quan, không tra cứu dữ liệu cá nhân. ")
PERSONAL_PLAN_DATA = ("Yêu cầu danh sách thí sinh phục vụ việc của Trung tâm (ví dụ gọi nhắc xác nhận nhập học, rà soát) giao cho du_lieu; "
                      "danh sách chi tiết chỉ hiển thị cho cán bộ, không đi qua các tác tử. ")
SYNTH_HINT = ("Người hỏi là cán bộ Trung tâm Tuyển sinh và Truyền thông của Trường Đại học Nghệ An; thí sinh không dùng hệ thống trực tiếp. "
              "Trả lời như trợ lý nghiệp vụ: số liệu kèm nguồn, ngắn gọn, đúng việc cán bộ cần. Không khuyên cán bộ gọi hotline của Trường; "
              "phần nào không có trong tài liệu công khai thì nói rõ và gợi ý nơi kiểm tra (văn bản gốc, hệ thống quản lý tuyển sinh, "
              "đơn vị liên quan). Khi cán bộ nhờ soạn tin nhắn, bài đăng hay văn bản gửi thí sinh, phụ huynh: viết bản nháp sạch, không chèn "
              "mã nguồn vào nội dung, rồi ghi mục \"Nguồn\" riêng ở cuối liệt kê các mã đã dùng; dùng mọi thông tin đã có nguồn, "
              "chỉ để trống (……) phần thật sự chưa có; thông tin đã công bố cho cả năm (mã ngành, phương thức, tổ hợp, điều kiện) "
              "thì điền vào và chú thích cần xác nhận lại cho đợt đang soạn, chỉ để trống số liệu riêng của đợt đó; tin nhắn, bài đăng "
              "gửi thí sinh, phụ huynh kết thúc bằng kênh liên hệ chính thức của Trung tâm (hotline, website) nếu nguồn có. "
              + PERSONAL_SYNTH +
              "Không khẳng định thí sinh chắc chắn đỗ hay trượt. Khi được hỏi về năm chưa có "
              "số liệu (ví dụ điểm chuẩn năm sau), chỉ nói rõ chưa có và vì sao; không nêu số của năm khác thay thế, kể cả để tham khảo. "
              "Khi dùng văn bản có LƯU Ý PHIÊN BẢN: vẫn đưa số liệu đã có, ghi rõ theo văn bản ngày nào, và nhắc ngắn gọn là đã có văn bản cập nhật "
              "để cán bộ đối chiếu; không bỏ số liệu đã có chỉ vì có văn bản cập nhật.")
PLAN_HINT = ("Người yêu cầu là cán bộ Trung tâm Tuyển sinh. Nếu câu hỏi là về năm chưa có số liệu trong danh sách nguồn (ví dụ dự đoán "
             "điểm chuẩn năm sau), chỉ lập một nhiệm vụ kiểm tra nguồn có số liệu năm đó hay không; không lập nhiệm vụ lấy số của năm khác "
             "để ước đoán. " + PERSONAL_PLAN +
             "Yêu cầu đối chiếu các văn bản có khớp nhau không: đưa vào context.refs mọi loại văn bản có thể ghi thông tin đó "
             "(thông tin tuyển sinh, văn bản cập nhật, thông báo tuyển sinh, thông báo điểm trúng tuyển), không chỉ văn bản cập nhật. "
             "Yêu cầu soạn văn bản, tin nhắn: trước tiên lập nhiệm vụ trích đủ thông tin đã có nguồn cần cho văn bản "
             "(ngành, mã ngành, tổ hợp, phương thức, điều kiện, lệ phí, liên hệ), để chỉ phần thật sự chưa có mới phải để trống; "
             "văn bản dài thì chia việc trích thành 2–3 nhiệm vụ nhỏ theo nhóm thông tin, chạy song song.")
DATA_PLAN_HINT = ("Tác tử du_lieu đọc cơ sở dữ liệu tuyển sinh 2026 của Trung tâm ({title}): nguyện vọng, lọc ảo, trúng tuyển, "
                  "xác nhận nhập học, ngày nhập học, hồ sơ giấy, tư vấn, số liệu 2024–2025. Câu hỏi về số liệu của Trung tâm (đếm, so sánh, "
                  "danh sách thí sinh, rà soát danh sách, kịch bản điểm chuẩn) giao cho du_lieu với task_type truy_van_du_lieu, không cần "
                  "context.refs, thường một nhiệm vụ là đủ; tiêu chí nghiệm thu chỉ nêu đúng những gì cán bộ hỏi, không thêm số liệu cán bộ không hỏi. "
                  "Câu về văn bản, quy chế giao cho tuyen_sinh; phép tính thêm trên kết quả giao analysis.")
DATA_SYNTH_HINT = ("Số liệu của tác tử dữ liệu dẫn [{source_id}] và nói rõ là theo dữ liệu lúc nào{synthetic}. "
                   "Kết quả có danh sách từng thí sinh: chỉ nêu số lượng, bảng đếm và nói danh sách chi tiết hiển thị bên dưới cho cán bộ "
                   "có quyền; không tự liệt kê tên hay số điện thoại. Kịch bản điểm chuẩn là số tham khảo, điểm chuẩn do Hội đồng tuyển sinh quyết định.")


def app_config(data: DataStore | None) -> tuple[set[str], str, str]:
    """Tác tử và chỉ dẫn của trợ lý tuyển sinh; có cơ sở dữ liệu thì thêm tác tử Dữ liệu. Trang demo và bộ thử dùng chung."""
    if data is None:
        return WORKERS, SYNTH_HINT, PLAN_HINT
    plan_hint = f"{PLAN_HINT.replace(PERSONAL_PLAN, PERSONAL_PLAN_DATA)} {DATA_PLAN_HINT.format(title=data.title())}"
    synth_hint = (f"{SYNTH_HINT.replace(PERSONAL_SYNTH, PERSONAL_SYNTH_DATA)} "
                  f"{DATA_SYNTH_HINT.format(source_id=data.source_id, synthetic=', ghi rõ là dữ liệu giả lập' if data.synthetic else '')}")
    return WORKERS | {"du_lieu"}, synth_hint, plan_hint
