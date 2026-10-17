"""Tạo cơ sở dữ liệu học vụ GIẢ LẬP để trình diễn AI Đào tạo (Phòng Quản lý đào tạo, giảng viên), khi chưa được nối dữ liệu thật.

    python scripts/make_gia_lap_dao_tao.py [--out <kho>/03_xu-ly/dao_tao/gia_lap/hoc_vu_gia_lap.sqlite] [--scale 1.0]

- Ngành lấy theo danh mục ngành của cơ sở dữ liệu tuyển sinh giả lập; sĩ số khóa K11 (2024) và K12 (2025) bằng đúng số nhập học 2024,
  2025 trong đó, để AI Tổng hợp ghép được số liệu hai lĩnh vực. Khóa K10 (2023) giả lập cùng cỡ.
- Thang điểm, xếp loại, ngưỡng cảnh báo học vụ theo Thông tư 08/2021/TT-BGDĐT (Điều 10, 11); tín chỉ tối đa, tối thiểu, trọng số
  điểm, buộc thôi học, sĩ số tối thiểu mở lớp theo quy chế của Trường (QĐ 620, QĐ 881; nguồn ghi trong bảng meta); riêng sĩ số tối đa
  lớp là tham số giả lập vì không có văn bản quy định.
- Sinh viên, giảng viên, điểm là giả: số điện thoại 0000.xxx.xxx, email @gia-lap.invalid. Cài sẵn vài lỗi (bảng _loi_cai_san).
- Dữ liệu chụp lúc 17:00 ngày 18/08/2026 (cùng thời điểm với dữ liệu tuyển sinh): năm học 2025–2026 đã xong, đang thi học kỳ hè.
"""
import argparse
import math
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import DATA_ROOT  # noqa: E402

OUT = DATA_ROOT / "03_xu-ly" / "dao_tao" / "gia_lap" / "hoc_vu_gia_lap.sqlite"
TS_DB = DATA_ROOT / "03_xu-ly" / "tuyen_sinh" / "gia_lap" / "tuyen_sinh_2026_gia_lap.sqlite"
SNAPSHOT = "17:00 ngày 18/08/2026"
TC_MAX, TC_MIN = 26, 14  # học kỳ chính: QĐ 620/QĐ-ĐHNA và QĐ 881/QĐ-ĐHKTNA, Điều 8 (DT-200, DT-203)
SI_SO_MAX, SI_SO_MIN = 70, 10  # tối thiểu 10 theo QĐ 881 Điều 9 (DT-203); tối đa không có văn bản quy định: tham số giả lập
W_QT, W_THI = 0.4, 0.6
KHOA = {"K10": 2023, "K11": 2024, "K12": 2025}
HOC_KY = ["2023-2024-1", "2023-2024-2", "2024-2025-1", "2024-2025-2", "2025-2026-1", "2025-2026-2"]
HE = "2025-2026-he"  # học kỳ hè 2026: học lại, thi từ 20/8 đến 28/8/2026

# (mã ngành, tên, khoa quản lý, nhóm, tổng tín chỉ CTĐT); CĐ GDMN và hai ngành sư phạm mới 2026 không có khóa K10–K12 ở đây
MAJORS = [
    ("7340301", "Kế toán", "Khoa Kế toán – Kiểm toán", "kinh_te", 129),
    ("7340101", "Quản trị kinh doanh", "Khoa Kinh tế – Quản trị kinh doanh", "kinh_te", 129),
    ("7340201", "Tài chính – Ngân hàng", "Khoa Tài chính – Ngân hàng", "kinh_te", 129),
    ("7310101", "Kinh tế", "Khoa Kinh tế – Quản trị kinh doanh", "kinh_te", 129),
    ("7340115", "Marketing", "Khoa Kinh tế – Quản trị kinh doanh", "kinh_te", 129),
    ("7340122", "Thương mại điện tử", "Khoa Kinh tế – Quản trị kinh doanh", "kinh_te", 129),
    ("7510605", "Logistics và Quản lý chuỗi cung ứng", "Khoa Kinh tế – Quản trị kinh doanh", "kinh_te", 129),
    ("7480201", "Công nghệ thông tin", "Khoa Công nghệ thông tin", "cong_nghe", 132),
    ("7220201", "Ngôn ngữ Anh", "Khoa Ngoại ngữ", "ngon_ngu", 130),
    ("7220204", "Ngôn ngữ Trung Quốc", "Khoa Ngoại ngữ", "ngon_ngu", 130),
    ("7640101", "Thú y", "Khoa Nông – Lâm – Ngư", "nong_lam", 155),
    ("7620101", "Nông nghiệp công nghệ cao", "Khoa Nông – Lâm – Ngư", "nong_lam", 130),
    ("7850103", "Quản lý đất đai", "Khoa Nông – Lâm – Ngư", "nong_lam", 130),
]
DAI_CUONG = [("Triết học Mác – Lênin", 3), ("Kinh tế chính trị Mác – Lênin", 2), ("Chủ nghĩa xã hội khoa học", 2),
             ("Lịch sử Đảng Cộng sản Việt Nam", 2), ("Tư tưởng Hồ Chí Minh", 2), ("Pháp luật đại cương", 2), ("Tin học đại cương", 3),
             ("Tiếng Anh 1", 3), ("Tiếng Anh 2", 3), ("Tiếng Anh 3", 3), ("Toán cao cấp", 3), ("Xác suất thống kê", 3)]
NHOM = {
    "kinh_te": ["Kinh tế vi mô", "Kinh tế vĩ mô", "Nguyên lý kế toán", "Nguyên lý thống kê", "Marketing căn bản", "Quản trị học",
                "Tài chính tiền tệ", "Luật kinh tế", "Kinh tế lượng", "Tài chính doanh nghiệp", "Quản trị nhân lực", "Thương mại điện tử căn bản"],
    "cong_nghe": ["Nhập môn lập trình", "Toán rời rạc", "Cấu trúc dữ liệu và giải thuật", "Kiến trúc máy tính", "Hệ điều hành",
                  "Cơ sở dữ liệu", "Mạng máy tính", "Lập trình hướng đối tượng", "Phân tích thiết kế hệ thống", "Lập trình web"],
    "ngon_ngu": ["Ngữ âm học", "Ngữ pháp", "Nghe 1", "Nói 1", "Đọc 1", "Viết 1", "Nghe 2", "Nói 2", "Đọc 2", "Viết 2", "Dẫn luận ngôn ngữ", "Văn hóa các nước"],
    "nong_lam": ["Sinh học đại cương", "Hóa học đại cương", "Sinh lý học", "Di truyền học", "Thổ nhưỡng", "Khí tượng nông nghiệp",
                 "Sinh thái học", "Thống kê sinh học", "Vi sinh vật học", "Hóa sinh"],
}
CHUYEN = {
    "7340301": ["Kế toán tài chính 1", "Kế toán tài chính 2", "Kế toán tài chính 3", "Kế toán quản trị", "Kiểm toán căn bản", "Thuế",
                "Hệ thống thông tin kế toán", "Kế toán hành chính sự nghiệp", "Phân tích báo cáo tài chính", "Kế toán ngân hàng"],
    "7480201": ["Công nghệ phần mềm", "Trí tuệ nhân tạo", "Học máy", "An toàn thông tin", "Lập trình di động", "Điện toán đám mây",
                "Kiểm thử phần mềm", "Phát triển ứng dụng web", "Xử lý ảnh", "Khai phá dữ liệu"],
    "7640101": ["Giải phẫu vật nuôi", "Dược lý thú y", "Bệnh truyền nhiễm thú y", "Ký sinh trùng thú y", "Chẩn đoán bệnh thú y",
                "Ngoại khoa thú y", "Sản khoa thú y", "Nội khoa thú y", "Vệ sinh an toàn thực phẩm", "Dịch tễ học thú y"],
    "7220201": ["Biên dịch 1", "Phiên dịch 1", "Biên dịch 2", "Phiên dịch 2", "Văn học Anh", "Tiếng Anh thương mại", "Ngôn ngữ học đối chiếu",
                "Phương pháp nghiên cứu", "Tiếng Anh du lịch", "Kỹ năng thuyết trình"],
    "7220204": ["Hán ngữ 1", "Hán ngữ 2", "Hán ngữ 3", "Biên dịch tiếng Trung", "Phiên dịch tiếng Trung", "Văn hóa Trung Quốc",
                "Tiếng Trung thương mại", "Chữ Hán", "Văn học Trung Quốc", "Tiếng Trung du lịch"],
}
HO = "Nguyễn Trần Lê Phạm Hoàng Phan Vũ Đặng Bùi Đỗ Hồ Ngô Dương Lý Thái Cao Hà Đinh".split()
DEM = "Văn Thị Đức Thu Minh Ngọc Quang Thanh Hữu Hồng Công Phương Tuấn Khánh".split()
TEN = "Anh Bình Chi Cường Dũng Duy Giang Hà Hải Hằng Hiếu Hoa Hùng Huyền Khoa Lan Linh Long Mai Minh Nam Ngân Nhung Phong Quân Sơn Thảo Trang Tùng Vy Yến".split()

SCHEMA = """
CREATE TABLE meta (khoa TEXT PRIMARY KEY, gia_tri TEXT);
CREATE TABLE nganh (ma_nganh TEXT PRIMARY KEY, ten_nganh TEXT, khoa_quan_ly TEXT, nhom TEXT, tong_tin_chi INTEGER);
CREATE TABLE giang_vien (ma_gv TEXT PRIMARY KEY, ho_ten TEXT, bo_mon TEXT, khoa_quan_ly TEXT);
CREATE TABLE sinh_vien (ma_sv TEXT PRIMARY KEY, ho_ten TEXT, ngay_sinh TEXT, gioi_tinh TEXT, sdt TEXT, email TEXT, ma_nganh TEXT,
    khoa TEXT, lop TEXT, phuong_thuc_trung_tuyen TEXT, diem_trung_tuyen REAL, trang_thai TEXT, ma_co_van TEXT);
CREATE TABLE hoc_phan (ma_hp TEXT PRIMARY KEY, ten_hp TEXT, so_tin_chi INTEGER, loai TEXT);
CREATE TABLE chuong_trinh (ma_nganh TEXT, ma_hp TEXT, hoc_ky_du_kien INTEGER, PRIMARY KEY (ma_nganh, ma_hp));
CREATE TABLE lop_hoc_phan (ma_lhp TEXT PRIMARY KEY, ma_hp TEXT, hoc_ky TEXT, ma_gv TEXT, ma_nganh TEXT, khoa TEXT, si_so INTEGER);
CREATE TABLE dang_ky (ma_sv TEXT, ma_lhp TEXT, hoc_ky TEXT, PRIMARY KEY (ma_sv, ma_lhp));
CREATE TABLE diem (ma_sv TEXT, ma_lhp TEXT, diem_qt REAL, diem_thi REAL, diem_hp REAL, diem_chu TEXT, diem_4 REAL, PRIMARY KEY (ma_sv, ma_lhp));
CREATE TABLE ket_qua_hoc_ky (ma_sv TEXT, hoc_ky TEXT, tc_dang_ky INTEGER, tc_dat INTEGER, tc_no_tich_luy INTEGER, dtb_hk REAL,
    dtb_tich_luy REAL, tc_tich_luy INTEGER, xep_loai TEXT, muc_canh_bao INTEGER, ly_do_canh_bao TEXT, PRIMARY KEY (ma_sv, hoc_ky));
CREATE TABLE chuan_dau_ra (ma_sv TEXT PRIMARY KEY, ngoai_ngu_dat INTEGER, tin_hoc_dat INTEGER);
CREATE TABLE lich_thi (hoc_ky TEXT, ma_lhp TEXT, ngay TEXT, ca INTEGER, phong TEXT, suc_chua INTEGER, PRIMARY KEY (hoc_ky, ma_lhp));
CREATE TABLE _loi_cai_san (doi_tuong TEXT, loi TEXT);
"""


def letter(x: float) -> tuple[str, float]:
    """Thang điểm theo TT 08/2021: điểm học phần thang 10 -> điểm chữ -> thang 4."""
    for lo, ch, four in ((8.5, "A", 4.0), (8.0, "B+", 3.5), (7.0, "B", 3.0), (6.5, "C+", 2.5), (5.5, "C", 2.0), (5.0, "D+", 1.5), (4.0, "D", 1.0)):
        if x >= lo:
            return ch, four
    return "F", 0.0


def rank(gpa: float) -> str:
    """Xếp loại học lực theo điểm trung bình thang 4 (TT 08/2021, Điều 10)."""
    return ("Xuất sắc" if gpa >= 3.6 else "Giỏi" if gpa >= 3.2 else "Khá" if gpa >= 2.5 else "Trung bình" if gpa >= 2.0
            else "Yếu" if gpa >= 1.0 else "Kém")


def tl_threshold(year_of_study: int) -> float:
    return {1: 1.2, 2: 1.4, 3: 1.6}.get(year_of_study, 1.8)


def cohort_sizes(scale: float) -> dict[tuple[str, str], int]:
    """Số nhập học 2024, 2025 lấy từ dữ liệu tuyển sinh giả lập (nếu có), để hai AI con khớp số."""
    sizes = {}
    if TS_DB.exists():
        with sqlite3.connect(TS_DB) as c:
            for nam, ma, nh in c.execute("SELECT nam, ma_xet_tuyen, nhap_hoc FROM lich_su"):
                khoa = {2024: "K11", 2025: "K12"}.get(nam)
                if khoa:
                    sizes[(ma, khoa)] = nh
    return {k: max(1, round(v * scale)) for k, v in sizes.items()}


def build(out: Path, scale: float = 1.0, seed: int = 2027) -> dict:
    rng = random.Random(seed)
    sizes = cohort_sizes(scale)
    # giảng viên: mỗi nhóm một bộ môn, đủ người đứng lớp
    lecturers, by_group = [], {}
    for g, n in (("dai_cuong", 30), ("kinh_te", 40), ("cong_nghe", 14), ("ngon_ngu", 16), ("nong_lam", 14)):
        for i in range(n):
            ma = f"GV{len(lecturers) + 1:03d}"
            lecturers.append((ma, f"{rng.choice(HO)} {rng.choice(DEM)} {rng.choice(TEN)}", {"dai_cuong": "Bộ môn Lý luận – Đại cương",
                              "kinh_te": "Bộ môn Kinh tế", "cong_nghe": "Bộ môn Công nghệ", "ngon_ngu": "Bộ môn Ngoại ngữ",
                              "nong_lam": "Bộ môn Nông nghiệp"}[g], g))
            by_group.setdefault(g, []).append(ma)

    # học phần và chương trình đào tạo
    courses, program = {}, {}

    def course(name: str, tc: int, loai: str) -> str:
        for ma, (ten, *_rest) in courses.items():
            if ten == name:
                return ma
        ma = f"HP{len(courses) + 1:04d}"
        courses[ma] = (name, tc, loai)
        return ma

    for ma_ng, ten, _k, nhom, tong in MAJORS:
        plan = [(course(n, tc, "Đại cương"), hk) for (n, tc), hk in zip(DAI_CUONG, [1, 1, 2, 2, 3, 1, 1, 1, 2, 3, 1, 2])]
        plan += [(course(n, 3, "Cơ sở ngành"), 2 + i // 3) for i, n in enumerate(NHOM[nhom])]
        specific = CHUYEN.get(ma_ng) or [f"{ten}: chuyên đề {i + 1}" for i in range(10)]
        plan += [(course(n, 3, "Chuyên ngành"), 4 + i // 3) for i, n in enumerate(specific)]
        program[ma_ng] = plan

    # sinh viên
    students = []
    for ma_ng, ten, _k, nhom, _t in MAJORS:
        for khoa, year in KHOA.items():
            n = sizes.get((ma_ng, khoa)) or max(1, round(rng.uniform(0.7, 1.0) * sizes.get((ma_ng, "K11"), 60)))
            cutoff = 16 if ma_ng not in ("7510605", "7220201", "7220204") else {"7510605": 18, "7220201": 18, "7220204": 22}[ma_ng]
            for i in range(n):
                pt = rng.choices(["100", "200", "402", "301"], weights=[58, 35, 4, 3])[0]
                diem = None if pt == "301" else round(max(cutoff, rng.gauss(cutoff + 2.0 + (0.8 if pt == "200" else 0), 1.8)) * 4) / 4
                ability = rng.gauss(0, 1) - (0.28 if pt == "200" else 0) + (0.12 * (diem - cutoff) if diem else 0.3)
                nam = rng.random() < 0.42
                students.append({"ma_sv": f"{year % 100:02d}{ma_ng}{i + 1:03d}",
                                 "ho_ten": f"{rng.choice(HO)} {rng.choice(DEM)} {rng.choice(TEN)}",
                                 "ngay_sinh": (date(year - 18, 1, 1) + timedelta(days=rng.randrange(365))).strftime("%d/%m/%Y"),
                                 "gioi_tinh": "Nam" if nam else "Nữ", "sdt": f"0000.{rng.randrange(1000):03d}.{rng.randrange(1000):03d}",
                                 "email": f"sv{year % 100:02d}{ma_ng}{i + 1:03d}@gia-lap.invalid", "ma_nganh": ma_ng, "khoa": khoa,
                                 "lop": f"{khoa}-{ma_ng[-3:]}-{i // 60 + 1}", "phuong_thuc_trung_tuyen": pt, "diem_trung_tuyen": diem,
                                 "trang_thai": "Đang học", "ma_co_van": rng.choice(by_group[nhom]), "_ability": ability, "_group": nhom})

    # từng học kỳ: đăng ký, lớp học phần, điểm, kết quả, cảnh báo
    sections: dict[tuple, tuple] = {}  # (mã lớp,) -> (học phần, học kỳ, giảng viên, ngành, khóa, sĩ số)
    regs, grades, results = [], [], []
    difficulty = {ma: rng.gauss(0, 0.6) for ma in courses}
    history = {s["ma_sv"]: {"tc_tl": 0, "sum4": 0.0, "owed": 0, "warn_streak": 0, "failed": []} for s in students}
    planted = []
    for hk_idx, hk in enumerate(HOC_KY):
        hk_year = 2023 + hk_idx // 2
        groups: dict[tuple, list[str]] = {}  # (học phần, ngành, khóa) -> sinh viên đăng ký trong học kỳ này
        for s in students:
            year = KHOA[s["khoa"]]
            sem_no = (hk_year - year) * 2 + hk_idx % 2 + 1  # học kỳ thứ mấy của khóa
            if sem_no < 1 or s["trang_thai"] != "Đang học":
                continue
            if rng.random() < 0.012:
                s["trang_thai"] = rng.choice(["Bảo lưu", "Thôi học (tự nguyện)"])
                continue
            h = history[s["ma_sv"]]
            due = [ma for ma, k in program[s["ma_nganh"]] if k == sem_no]
            retake = h["failed"][:2] if rng.random() < 0.6 else []
            take = due + [m for m in retake if m not in due]
            for ma_hp in take:
                groups.setdefault((ma_hp, s["ma_nganh"], s["khoa"]), []).append(s["ma_sv"])
        # chia lớp học phần theo sĩ số (tối đa 60 mỗi lớp khi xếp; lớp vượt sĩ số là lỗi cài sẵn ở dưới)
        for (ma_hp, ma_ng, khoa), svs in groups.items():
            nhom = next(m[3] for m in MAJORS if m[0] == ma_ng)
            g = "dai_cuong" if courses[ma_hp][2] == "Đại cương" else nhom
            n_lop = math.ceil(len(svs) / 60)
            for j in range(n_lop):
                ma_lhp = f"{ma_hp}-{hk[2:4]}{hk[-1]}-{ma_ng[-3:]}{khoa[-2:]}-{j + 1}"
                members = svs[j::n_lop]
                sections[(ma_lhp,)] = (ma_hp, hk, rng.choice(by_group[g]), ma_ng, khoa, len(members))
                for ma_sv in members:
                    regs.append((ma_sv, ma_lhp, hk))
        # tính điểm và kết quả học kỳ
        lhp_of = {}
        for ma_sv, ma_lhp, hkk in regs:
            if hkk == hk:
                lhp_of.setdefault(ma_sv, []).append(ma_lhp)
        by_id = {s["ma_sv"]: s for s in students}
        for ma_sv, lops in lhp_of.items():
            s, h = by_id[ma_sv], history[ma_sv]
            tc_dk = tc_dat = 0
            sum4 = 0.0
            for ma_lhp in lops:
                ma_hp = sections[(ma_lhp,)][0]
                tc = courses[ma_hp][1]
                base = 6.3 + 1.25 * s["_ability"] - difficulty[ma_hp]
                qt = round(min(10, max(0, rng.gauss(base + 0.8, 1.0))), 1)
                thi = round(min(10, max(0, rng.gauss(base, 1.4))), 1)
                hp = round(W_QT * qt + W_THI * thi, 1)
                ch, four = letter(hp)
                grades.append([ma_sv, ma_lhp, qt, thi, hp, ch, four])
                tc_dk += tc
                sum4 += four * tc
                if four > 0:
                    tc_dat += tc
                    if ma_hp in h["failed"]:
                        h["failed"].remove(ma_hp)
                        h["owed"] -= tc
                    h["tc_tl"] += tc
                    h["sum4"] += four * tc
                elif ma_hp not in h["failed"]:
                    h["failed"].append(ma_hp)
                    h["owed"] += tc
            year = KHOA[s["khoa"]]
            sem_no = (2023 + hk_idx // 2 - year) * 2 + hk_idx % 2 + 1
            dtb_hk = round(sum4 / tc_dk, 2) if tc_dk else 0.0
            dtb_tl = round(h["sum4"] / h["tc_tl"], 2) if h["tc_tl"] else 0.0
            reasons = []
            if tc_dk and (tc_dk - tc_dat) > 0.5 * tc_dk:
                reasons.append("Số tín chỉ không đạt trong học kỳ vượt 50% khối lượng đăng ký")
            if h["owed"] > 24:
                reasons.append("Tổng số tín chỉ nợ đọng vượt 24")
            if dtb_hk < (0.8 if sem_no == 1 else 1.0):
                reasons.append("Điểm trung bình học kỳ dưới ngưỡng")
            if dtb_tl < tl_threshold((sem_no + 1) // 2):
                reasons.append("Điểm trung bình tích lũy dưới ngưỡng")
            h["warn_streak"] = h["warn_streak"] + 1 if reasons else 0
            level = min(h["warn_streak"], 2)
            if h["warn_streak"] >= 3:  # tham số giả lập của Trường: cảnh báo 3 học kỳ liên tiếp thì buộc thôi học
                s["trang_thai"] = "Buộc thôi học"
            results.append([ma_sv, hk, tc_dk, tc_dat, h["owed"], dtb_hk, dtb_tl, h["tc_tl"], rank(dtb_hk), level, "; ".join(reasons)])

    # học kỳ hè 2026: đăng ký học lại, lịch thi 20–28/8/2026 (chưa có điểm)
    he_regs = {}
    for s in students:
        h = history[s["ma_sv"]]
        if s["trang_thai"] == "Đang học" and h["failed"] and rng.random() < 0.45:
            for ma_hp in h["failed"][:2]:
                he_regs.setdefault(ma_hp, []).append(s["ma_sv"])
    exam_rows = []
    for idx, (ma_hp, svs) in enumerate(sorted(he_regs.items())):
        n_lop = math.ceil(len(svs) / 60)
        for j in range(n_lop):
            ma_lhp = f"{ma_hp}-26H-{j + 1}"
            members = svs[j::n_lop]
            g = "dai_cuong" if courses[ma_hp][2] == "Đại cương" else rng.choice(["kinh_te", "cong_nghe", "ngon_ngu", "nong_lam"])
            sections[(ma_lhp,)] = (ma_hp, HE, rng.choice(by_group[g]), "", "", len(members))
            for ma_sv in members:
                regs.append((ma_sv, ma_lhp, HE))
            day = date(2026, 8, 20) + timedelta(days=(idx + j) % 9)
            exam_rows.append([HE, ma_lhp, day.isoformat(), 1 + (idx + j) % 4, f"A{1 + (idx * 3 + j) % 12}.{1 + j % 3:02d}", 60])

    # lỗi cài sẵn để trình diễn rà soát
    main = [s for s in students if s["trang_thai"] == "Đang học" and s["khoa"] == "K12"]
    last_hk = HOC_KY[-1]
    reg_by_sv = {}
    for ma_sv, ma_lhp, hkk in regs:
        if hkk == last_hk:
            reg_by_sv.setdefault(ma_sv, []).append(ma_lhp)
    extra_lops = [k[0] for k, v in sections.items() if len(k) == 1 and v[1] == last_hk and v[3] == "7480201"]
    for s in main[:3]:  # đăng ký vượt số tín chỉ tối đa
        added = 0
        for ma_lhp in extra_lops:
            if ma_lhp not in reg_by_sv.get(s["ma_sv"], []) and added < 4:
                regs.append((s["ma_sv"], ma_lhp, last_hk))
                added += 1
        planted.append((s["ma_sv"], "Đăng ký vượt số tín chỉ tối đa của học kỳ"))
    he_by_sv = {}
    for ma_sv, ma_lhp, hkk in regs:
        if hkk == HE:
            he_by_sv.setdefault(ma_sv, []).append(ma_lhp)
    doubles = [(sv, lops) for sv, lops in he_by_sv.items() if len(lops) >= 2][:2]
    for sv, lops in doubles:  # trùng lịch thi: đưa môn thứ hai về cùng ngày, cùng ca với môn thứ nhất
        first = next(r for r in exam_rows if r[1] == lops[0])
        second = next(r for r in exam_rows if r[1] == lops[1])
        second[2], second[3] = first[2], first[3]
        planted.append((sv, "Trùng lịch thi học kỳ hè"))
    big = [k for k, v in sections.items() if len(k) == 1 and v[1] == last_hk][:2]
    for k in big:  # lớp vượt sĩ số tối đa
        v = list(sections[k])
        v[5] = SI_SO_MAX + 8
        sections[k] = tuple(v)
        planted.append((k[0], "Lớp học phần vượt sĩ số tối đa"))
    wrong = next((g for g in grades if g[1].endswith("-2") and g[4] >= 5), None) or next(g for g in grades if g[4] >= 5)  # điểm không khớp công thức
    wrong[4] = round(wrong[4] + 1.5, 1)
    wrong[5], wrong[6] = letter(wrong[4])
    planted.append((wrong[0], "Điểm học phần không khớp điểm thành phần"))

    # chuẩn đầu ra ngoại ngữ, tin học (K10 sắp tốt nghiệp)
    outputs = [(s["ma_sv"], int(rng.random() < (0.72 if s["khoa"] == "K10" else 0.35)), int(rng.random() < 0.8)) for s in students]

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    meta = {"thoi_diem_du_lieu": SNAPSHOT, "nam_hoc_hien_tai": "2025–2026 (đã kết thúc học kỳ 2; đang học kỳ hè)",
            "ghi_chu": "DỮ LIỆU GIẢ LẬP để trình diễn; không phải dữ liệu thật của Trường. Thang điểm, xếp loại, ngưỡng cảnh báo theo TT 08/2021; "
                       "tham số đào tạo theo quy chế của Trường (xem nguon_tham_so), riêng sĩ số tối đa lớp là giả lập.",
            "tin_chi_toi_da_hoc_ky": str(TC_MAX), "tin_chi_toi_thieu_hoc_ky": str(TC_MIN), "si_so_toi_da_lop": str(SI_SO_MAX),
            "si_so_toi_thieu_mo_lop": str(SI_SO_MIN), "trong_so_diem": "quá trình 40%, thi 60%",
            "buoc_thoi_hoc": "cảnh báo quá 2 lần liên tiếp (quy chế còn tính quá 3 lần không liên tiếp; bản giả lập chỉ mô phỏng liên tiếp)",
            "nguon_tham_so": "tín chỉ tối đa 26, tối thiểu 14: QĐ 620 và QĐ 881 Điều 8; trọng số 0,4/0,6: QĐ 620 và QĐ 881 Điều 13; buộc thôi học: QĐ 620 và QĐ 881 Điều 17; sĩ số tối thiểu mở lớp 10: QĐ 881 Điều 9; sĩ số tối đa 70: giả lập (không có văn bản)",
            "hat_giong": str(seed), "ty_le": str(scale)}
    db.executemany("INSERT INTO meta VALUES (?, ?)", meta.items())
    db.executemany("INSERT INTO nganh VALUES (?,?,?,?,?)", MAJORS)
    db.executemany("INSERT INTO giang_vien VALUES (?,?,?,?)", [(m, t, b, g) for m, t, b, g in lecturers])
    cols = ["ma_sv", "ho_ten", "ngay_sinh", "gioi_tinh", "sdt", "email", "ma_nganh", "khoa", "lop", "phuong_thuc_trung_tuyen",
            "diem_trung_tuyen", "trang_thai", "ma_co_van"]
    db.executemany(f"INSERT INTO sinh_vien VALUES ({','.join('?' * len(cols))})", [tuple(s[c] for c in cols) for s in students])
    db.executemany("INSERT INTO hoc_phan VALUES (?,?,?,?)", [(m, *v) for m, v in courses.items()])
    db.executemany("INSERT INTO chuong_trinh VALUES (?,?,?)", [(ng, hp, hk) for ng, plan in program.items() for hp, hk in plan])
    db.executemany("INSERT INTO lop_hoc_phan VALUES (?,?,?,?,?,?,?)", [(k[0], *v) for k, v in sections.items() if len(k) == 1])
    db.executemany("INSERT OR IGNORE INTO dang_ky VALUES (?,?,?)", regs)
    db.executemany("INSERT INTO diem VALUES (?,?,?,?,?,?,?)", [tuple(g) for g in grades])
    db.executemany("INSERT INTO ket_qua_hoc_ky VALUES (?,?,?,?,?,?,?,?,?,?,?)", [tuple(r) for r in results])
    db.executemany("INSERT INTO chuan_dau_ra VALUES (?,?,?)", outputs)
    db.executemany("INSERT INTO lich_thi VALUES (?,?,?,?,?,?)", [tuple(r) for r in exam_rows])
    db.executemany("INSERT INTO _loi_cai_san VALUES (?,?)", planted)
    db.commit()
    db.close()
    return {"sinh_vien": len(students), "hoc_phan": len(courses), "lop_hoc_phan": sum(1 for k in sections if len(k) == 1),
            "dang_ky": len(regs), "diem": len(grades), "ket_qua_hoc_ky": len(results), "lich_thi": len(exam_rows), "loi_cai_san": len(planted)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Tạo cơ sở dữ liệu học vụ giả lập")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()
    counts = build(Path(args.out), args.scale)
    print(f"Đã ghi {args.out}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
