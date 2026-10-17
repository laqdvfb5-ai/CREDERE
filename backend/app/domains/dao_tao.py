"""AI Đào tạo: trợ lý cho cán bộ Phòng Quản lý đào tạo và giảng viên (quy chế, chương trình, tín chỉ, lịch thi; dữ liệu học vụ ở giai đoạn 2)."""
from ..config import DATA_ROOT
from ..tools.data import DataStore
from .dao_tao_queries import QUERIES

KEY = "dao_tao"
TEN = "AI Đào tạo"
DON_VI = "Phòng Quản lý đào tạo"
NGUOI_DUNG = "cán bộ Phòng Quản lý đào tạo và giảng viên"
LINH_VUC = ("đào tạo: quy chế đào tạo của Bộ và quy định của Trường, chương trình đào tạo, tín chỉ, đăng ký học phần, thang điểm, "
            "cảnh báo học vụ, xét tốt nghiệp, lịch thi; số liệu học vụ các khóa K10–K12 (nhập học 2023–2025): sĩ số, rời trường, "
            "kết quả học tập theo ngành và theo phương thức trúng tuyển, cảnh báo, lớp học phần, dự kiến số lớp cần mở")
SOURCE_ID = "CSDL-DT"
DEFAULT_SOURCES = DATA_ROOT / "03_xu-ly" / "dao_tao" / "sources.json"
DEFAULT_DATA = DATA_ROOT / "03_xu-ly" / "dao_tao" / "gia_lap" / "hoc_vu_gia_lap.sqlite"
WORKERS = {"dao_tao", "analysis"}


def open_store(path) -> DataStore:
    return DataStore(path, QUERIES, SOURCE_ID, "học vụ", person="sinh viên", majors_sql="SELECT ma_nganh, ten_nganh FROM nganh ORDER BY 1")


SYNTH_HINT = ("Người hỏi là cán bộ Phòng Quản lý đào tạo hoặc giảng viên của Trường Đại học Nghệ An. Trả lời như trợ lý nghiệp vụ, ngắn gọn: "
              "quy định thì nêu văn bản và điều, khoản; số liệu thì kèm nguồn. Khi quy chế của Bộ và quy định của Trường khác nhau, nêu cả hai "
              "và nói rõ văn bản nào áp dụng cho khóa nào. Phần nào không có trong tài liệu thì nói rõ và gợi ý nơi kiểm tra "
              "(văn bản gốc, phần mềm quản lý đào tạo, khoa quản lý ngành). Không kết luận xử lý học vụ cho một sinh viên cụ thể; "
              "chỉ nêu căn cứ và số liệu để cán bộ quyết định. Không tự viết ra dữ liệu cá nhân của sinh viên (tên, điểm từng người, số điện thoại).")
PLAN_HINT = ("Người yêu cầu là cán bộ Phòng Quản lý đào tạo hoặc giảng viên. Câu về quy chế, quy định, chương trình đào tạo giao cho dao_tao, "
             "đưa vào context.refs cả quy chế của Bộ và quy định của Trường liên quan để đối chiếu. Phép tính (tổng tín chỉ, số học kỳ, "
             "điểm trung bình theo công thức) giao cho analysis phụ thuộc nhiệm vụ lấy số liệu.")
DATA_PLAN_HINT = ("Tác tử du_lieu đọc cơ sở dữ liệu học vụ ({title}): sinh viên các khóa K10–K12, chương trình đào tạo, lớp học phần, "
                  "đăng ký, điểm, kết quả và cảnh báo từng học kỳ, chuẩn đầu ra, lịch thi học kỳ hè 2026, giảng viên (mã). "
                  "Câu về số liệu học vụ (đếm, so sánh, danh sách sinh viên, rà soát dữ liệu, dự kiến số lớp) giao cho du_lieu với task_type "
                  "truy_van_du_lieu, không cần context.refs, thường một nhiệm vụ là đủ; câu cần cả quy định và số liệu (ví dụ số sinh viên "
                  "bị cảnh báo và căn cứ cảnh báo) thì giao dao_tao và du_lieu song song. Câu hỏi cần mở bao nhiêu lớp học phần giao du_lieu "
                  "(truy vấn du_kien_mo_lop, dùng số sinh viên được nêu trong yêu cầu hoặc trong kết quả từ lĩnh vực khác; sĩ số tối đa là tham số "
                  "giả lập, xem truy vấn tham_so_dao_tao), không giao dao_tao. Tiêu chí nghiệm thu chỉ nêu đúng những gì được hỏi.")
DATA_SYNTH_HINT = ("Số liệu của tác tử dữ liệu dẫn [{source_id}] và nói rõ là theo dữ liệu lúc nào{synthetic}. Kết quả có danh sách từng "
                   "sinh viên: chỉ nêu số lượng, bảng đếm và nói danh sách chi tiết hiển thị bên dưới cho cán bộ có quyền. Sĩ số tối đa lớp "
                   "học phần trong dữ liệu là tham số giả lập (không có văn bản quy định) và phải ghi rõ như vậy.")


def app_config(data: DataStore | None) -> tuple[set[str], str, str]:
    if data is None:
        return WORKERS, SYNTH_HINT, PLAN_HINT
    synthetic = ", ghi rõ là dữ liệu giả lập" if data.synthetic else ""
    return (WORKERS | {"du_lieu"}, f"{SYNTH_HINT} {DATA_SYNTH_HINT.format(source_id=data.source_id, synthetic=synthetic)}",
            f"{PLAN_HINT} {DATA_PLAN_HINT.format(title=data.title())}")
