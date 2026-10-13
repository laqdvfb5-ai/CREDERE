"""Tạo cơ sở dữ liệu tuyển sinh 2026 GIẢ LẬP để trình diễn tác tử Dữ liệu (giai đoạn 2), khi chưa được nối dữ liệu thật.

    python scripts/make_gia_lap.py [--out <kho>/03_xu-ly/tuyen_sinh/gia_lap/tuyen_sinh_2026_gia_lap.sqlite] [--scale 1.0]

Ngành, mã xét tuyển, chỉ tiêu, điểm chuẩn đợt 1 lấy từ văn bản công khai (TS-100, TS-202, TS-309). Mọi thứ về thí sinh
(họ tên, CCCD, số điện thoại, nguyện vọng, điểm, xác nhận nhập học…) là giả, sinh ngẫu nhiên có hạt giống cố định:
số điện thoại dạng 0000.xxx.xxx, CCCD bắt đầu bằng GL để không trùng người thật.
Dữ liệu chụp lúc 17h ngày 18/8/2026: sau ngày nhập học 17/8, trước hạn xác nhận nhập học 17h ngày 21/8.
Cài sẵn vài lỗi trong danh sách trúng tuyển (bảng _loi_cai_san) để trình diễn việc rà soát.
"""
import argparse
import random
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import DATA_ROOT  # noqa: E402

OUT = DATA_ROOT / "03_xu-ly" / "tuyen_sinh" / "gia_lap" / "tuyen_sinh_2026_gia_lap.sqlite"
SNAPSHOT = datetime(2026, 8, 18, 17, 0)
CONFIRM_DEADLINE = datetime(2026, 8, 21, 17, 0)

# mã, tên, nhóm, chỉ tiêu (QĐ 140; ba ngành giáo viên theo TB 876), điểm chuẩn PT 100 và PT 200 (TS-100), số thí sinh quan tâm,
# tỷ lệ xác nhận nhập học cuối cùng. Hai cột cuối là tham số giả lập.
MAJORS = [
    ("7340301", "Kế toán", "kinh_te", 450, 16, 17, 730, 0.62),
    ("7340101", "Quản trị kinh doanh", "kinh_te", 250, 16, 17, 520, 0.74),
    ("7340201", "Tài chính – Ngân hàng", "kinh_te", 80, 16, 17, 55, 0.72),
    ("7310101", "Kinh tế", "kinh_te", 150, 16, 17, 250, 0.70),
    ("7340115", "Marketing", "kinh_te", 200, 16, 17, 420, 0.76),
    ("7340122", "Thương mại điện tử", "kinh_te", 70, 16, 17, 40, 0.74),
    ("7510605", "Logistics và Quản lý chuỗi cung ứng", "kinh_te", 100, 18.85, 19.85, 150, 0.80),
    ("7480201", "Công nghệ thông tin", "cong_nghe", 300, 16, 17, 640, 0.76),
    ("7220201", "Ngôn ngữ Anh", "ngon_ngu", 200, 18, 19, 470, 0.80),
    ("7220204", "Ngôn ngữ Trung Quốc", "ngon_ngu", 200, 23.25, 24.25, 480, 0.84),
    ("7640101", "Thú y", "nong_lam", 150, 15, 16, 260, 0.58),
    ("7620101", "Nông nghiệp công nghệ cao", "nong_lam", 30, 15, 16, 60, 0.60),
    ("7850103", "Quản lý đất đai", "nong_lam", 30, 15, 16, 55, 0.62),
    ("7140202", "Sư phạm Tiểu học", "su_pham", 150, 23, None, 480, 0.88),
    ("7140247", "Sư phạm Khoa học tự nhiên", "su_pham", 150, 20, None, 300, 0.72),
    ("51140201", "Giáo dục Mầm non (cao đẳng)", "su_pham", 120, None, None, 260, 0.86),
]
PT405_CUTOFF = 20.75  # CĐ Giáo dục Mầm non, PT 405 (TS-100)
NEW_2026 = {"7140202", "7140247"}  # không có trong bảng điểm 2025 (TS-101)
MORNING = {"kinh_te", "cong_nghe"}  # nhập học 7h30; nhóm còn lại 13h30 (TS-310)

HO = "Nguyễn Trần Lê Phạm Hoàng Phan Vũ Đặng Bùi Đỗ Hồ Ngô Dương Lý Thái Cao Hà Đinh".split()
DEM_NAM = "Văn Đức Minh Quang Hữu Công Tuấn Đình Xuân Thành".split()
DEM_NU = "Thị Thu Ngọc Thanh Hồng Phương Khánh Minh Bảo Mai".split()
TEN_NAM = "Anh Bình Cường Dũng Duy Hải Hiếu Hoàng Hùng Khoa Kiên Long Mạnh Nam Phong Quân Sơn Tài Thắng Trung Tùng Việt Vinh".split()
TEN_NU = "An Anh Chi Diệp Giang Hà Hằng Hiền Hoa Huyền Lan Linh Loan Ly My Nga Ngân Nhung Oanh Phương Quỳnh Thảo Trang Vy Yến".split()
DIA_BAN = ["Vinh", "Cửa Lò", "Nghi Lộc", "Hưng Nguyên", "Nam Đàn", "Diễn Châu", "Quỳnh Lưu", "Yên Thành", "Đô Lương",
           "Thanh Chương", "Anh Sơn", "Tân Kỳ", "Nghĩa Đàn", "Quỳ Hợp", "Con Cuông", "Hoàng Mai", "Thái Hòa"]
THPT = {  # tên trường THPT theo địa bàn (chỉ dùng làm nhãn; thí sinh là giả)
    "Vinh": ["THPT Huỳnh Thúc Kháng", "THPT Hà Huy Tập", "THPT Lê Viết Thuật"], "Cửa Lò": ["THPT Cửa Lò"],
    "Nghi Lộc": ["THPT Nghi Lộc 1", "THPT Nghi Lộc 2"], "Hưng Nguyên": ["THPT Hưng Nguyên"], "Nam Đàn": ["THPT Nam Đàn 1", "THPT Kim Liên"],
    "Diễn Châu": ["THPT Diễn Châu 2", "THPT Diễn Châu 3"], "Quỳnh Lưu": ["THPT Quỳnh Lưu 1", "THPT Quỳnh Lưu 2"],
    "Yên Thành": ["THPT Yên Thành 2", "THPT Phan Đăng Lưu"], "Đô Lương": ["THPT Đô Lương 1", "THPT Đô Lương 3"],
    "Thanh Chương": ["THPT Thanh Chương 1", "THPT Đặng Thai Mai"], "Anh Sơn": ["THPT Anh Sơn 1"], "Tân Kỳ": ["THPT Tân Kỳ"],
    "Nghĩa Đàn": ["THPT Nghĩa Đàn"], "Quỳ Hợp": ["THPT Quỳ Hợp 1"], "Con Cuông": ["THPT Con Cuông"],
    "Hoàng Mai": ["THPT Hoàng Mai"], "Thái Hòa": ["THPT Thái Hòa"],
}
OTHER_PROVINCES = [("Hà Tĩnh", "THPT Hồng Lĩnh"), ("Hà Tĩnh", "THPT Can Lộc"), ("Thanh Hóa", "THPT Tĩnh Gia 1"), ("Quảng Bình", "THPT Đồng Hới")]
KENH = [("Fanpage Facebook", 30), ("TikTok", 18), ("Tư vấn tại trường THPT", 22), ("Người quen giới thiệu", 15), ("Website", 10), ("Khác", 5)]
CAN_BO = [("TV01", "Nguyễn Thị Hạnh"), ("TV02", "Trần Văn Hùng"), ("TV03", "Lê Thị Mai"), ("TV04", "Phạm Quang Huy"),
          ("TV05", "Hoàng Thị Lan"), ("TV06", "Võ Đức Thắng"), ("TV07", "Đặng Thu Trang"), ("TV08", "Bùi Minh Tuấn")]  # tên giả
RELATED = {"kinh_te": ["kinh_te", "cong_nghe"], "cong_nghe": ["cong_nghe", "kinh_te"], "ngon_ngu": ["ngon_ngu", "kinh_te"],
           "nong_lam": ["nong_lam", "kinh_te"], "su_pham": ["su_pham"]}

SCHEMA = """
CREATE TABLE meta (khoa TEXT PRIMARY KEY, gia_tri TEXT);
CREATE TABLE nganh (ma_xet_tuyen TEXT PRIMARY KEY, ten_nganh TEXT, nhom TEXT, trinh_do TEXT, chi_tieu INTEGER,
    diem_chuan_100 REAL, diem_chuan_200 REAL, diem_chuan_405 REAL, la_su_pham INTEGER);
CREATE TABLE thi_sinh (ma_ts TEXT PRIMARY KEY, ho_ten TEXT, ngay_sinh TEXT, gioi_tinh TEXT, cccd TEXT, sdt TEXT, tinh TEXT,
    dia_ban TEXT, truong_thpt TEXT, khu_vuc TEXT, doi_tuong TEXT, thuong_tru_nghe_an INTEGER, kenh_biet_den TEXT,
    ma_can_bo_tu_van TEXT, can_bo_tu_van TEXT);
CREATE TABLE nguyen_vong (ma_ts TEXT, thu_tu INTEGER, ma_xet_tuyen TEXT, phuong_thuc TEXT, diem_xet REAL, trang_thai TEXT,
    PRIMARY KEY (ma_ts, thu_tu));
CREATE TABLE loc_ao (vong INTEGER, ma_xet_tuyen TEXT, diem_chuan_du_kien REAL, so_du_kien_trung_tuyen INTEGER,
    PRIMARY KEY (vong, ma_xet_tuyen));
CREATE TABLE trung_tuyen (ma_ts TEXT PRIMARY KEY, ma_xet_tuyen TEXT, phuong_thuc TEXT, thu_tu_nv INTEGER, diem_xet REAL, dot INTEGER,
    ngay_cong_bo TEXT);
CREATE TABLE xac_nhan (ma_ts TEXT PRIMARY KEY, thoi_diem TEXT);
CREATE TABLE nhap_hoc (ma_ts TEXT PRIMARY KEY, thoi_diem TEXT, trang_thai TEXT, thieu TEXT, da_nop_hoc_phi INTEGER,
    dang_ky_nd116 INTEGER);
CREATE TABLE ho_so_giay (ma_ho_so TEXT PRIMARY KEY, ma_ts TEXT, phuong_thuc TEXT, kenh_nop TEXT, ngay_dau_buu_cuc TEXT,
    ngay_nhan TEXT, trang_thai TEXT, thieu TEXT);
CREATE TABLE tu_van (id INTEGER PRIMARY KEY, thoi_diem TEXT, kenh TEXT, chu_de TEXT, ma_xet_tuyen TEXT, da_tra_loi INTEGER,
    phut_phan_hoi INTEGER);
CREATE TABLE lich_su (nam INTEGER, ma_xet_tuyen TEXT, chi_tieu INTEGER, so_nv1 INTEGER, trung_tuyen INTEGER, xac_nhan INTEGER,
    nhap_hoc INTEGER, ghi_chu TEXT, PRIMARY KEY (nam, ma_xet_tuyen));
CREATE TABLE _loi_cai_san (ma_ts TEXT, loi TEXT);
"""


def weighted(rng: random.Random, pairs):
    return rng.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]


def fake_person(rng: random.Random, i: int) -> dict:
    nam = rng.random() < 0.45
    ho_ten = f"{rng.choice(HO)} {rng.choice(DEM_NAM if nam else DEM_NU)} {rng.choice(TEN_NAM if nam else TEN_NU)}"
    ngay_sinh = (datetime(2008, 1, 1) + timedelta(days=rng.randrange(366))).strftime("%d/%m/%Y")
    if rng.random() < 0.86:
        tinh, dia_ban = "Nghệ An", rng.choice(DIA_BAN)
        truong = rng.choice(THPT[dia_ban])
    else:
        tinh, truong = rng.choice(OTHER_PROVINCES)
        dia_ban = ""
    can_bo = rng.choice(CAN_BO)
    return {"ma_ts": f"TS{i:05d}", "ho_ten": ho_ten, "ngay_sinh": ngay_sinh, "gioi_tinh": "Nam" if nam else "Nữ",
            "cccd": f"GL{rng.randrange(10**9, 10**10)}", "sdt": f"0000.{rng.randrange(1000):03d}.{rng.randrange(1000):03d}",
            "tinh": tinh, "dia_ban": dia_ban, "truong_thpt": truong,
            "khu_vuc": weighted(rng, [("KV1", 18), ("KV2-NT", 55), ("KV2", 22), ("KV3", 5)]),
            "doi_tuong": weighted(rng, [("", 92), ("UT2", 6), ("UT1", 2)]),
            "thuong_tru_nghe_an": int(tinh == "Nghệ An" or rng.random() < 0.05), "kenh_biet_den": weighted(rng, KENH),
            "ma_can_bo_tu_van": can_bo[0], "can_bo_tu_van": can_bo[1]}


def score(rng: random.Random, center: float, spread: float) -> float:
    return round(min(29.5, max(10.0, rng.gauss(center, spread))) * 20) / 20  # bội số 0,05 như điểm thật


def cutoff(m: dict, pt: str) -> float | None:
    return {"100": m["c100"], "402": m["c100"], "200": m["c200"], "405": PT405_CUTOFF}.get(pt)


def build(out: Path, scale: float = 1.0, seed: int = 2026) -> dict:
    rng = random.Random(seed)
    majors = {r[0]: {"ma": r[0], "ten": r[1], "nhom": r[2], "chi_tieu": r[3], "c100": r[4], "c200": r[5], "demand": r[6], "confirm": r[7],
                     "sp": r[2] == "su_pham"} for r in MAJORS}
    by_group: dict[str, list[str]] = {}
    for m in majors.values():
        by_group.setdefault(m["nhom"], []).append(m["ma"])

    people, wishes = [], []
    i = 0
    for m in majors.values():
        for _ in range(max(1, round(m["demand"] * scale))):
            i += 1
            p = fake_person(rng, i)
            people.append(p)
            first = 1 if rng.random() < 0.34 else rng.randint(2, 9)  # vị trí của nguyện vọng đầu tiên vào NAU trong 15 nguyện vọng
            chosen = [m["ma"]] + rng.sample([x for g in RELATED[m["nhom"]] for x in by_group[g] if x != m["ma"]], k=rng.choice([0, 0, 1, 2]))
            pos = first
            for ma in chosen:
                mj = majors[ma]
                if ma == "51140201":
                    pt = "301" if rng.random() < 0.03 else "405"
                elif mj["sp"]:
                    pt = weighted(rng, [("100", 90), ("402", 7), ("301", 3)])
                else:
                    pt = weighted(rng, [("100", 70), ("200", 22), ("402", 6), ("301", 2)])
                c = cutoff(mj, pt)
                diem = None if pt == "301" else score(rng, (c or 16) + (1.6 if pt == "200" else 0.9), 2.6)
                wishes.append({"ma_ts": p["ma_ts"], "thu_tu": pos, "ma_xet_tuyen": ma, "phuong_thuc": pt, "diem_xet": diem})
                pos += rng.randint(1, 3)

    # Lọc ảo: thí sinh trúng nguyện vọng cao hơn ở trường khác thì bị loại, ở vòng nào đó từ 1 đến 6.
    wish_by_person: dict[str, list[dict]] = {}
    for w in wishes:
        wish_by_person.setdefault(w["ma_ts"], []).append(w)
    person = {p["ma_ts"]: p for p in people}
    removed_round: dict[str, int] = {}
    for ts, ws in wish_by_person.items():
        first = min(w["thu_tu"] for w in ws)
        p_other = 0.12 if first == 1 else 0.45 if first <= 3 else 0.68
        if rng.random() < p_other:
            removed_round[ts] = rng.choices([1, 2, 3, 4, 5, 6], weights=[40, 22, 14, 10, 8, 6])[0]

    def eligible(w: dict) -> bool:
        mj, p = majors[w["ma_xet_tuyen"]], person[w["ma_ts"]]
        if mj["sp"] and (not p["thuong_tru_nghe_an"] or w["thu_tu"] > 5):  # ngành giáo viên: thường trú Nghệ An, nguyện vọng 1–5
            return False
        return w["phuong_thuc"] == "301" or w["diem_xet"] >= cutoff(mj, w["phuong_thuc"])

    assigned = {}  # nguyện vọng cao nhất vào NAU mà thí sinh đạt
    for ts, ws in wish_by_person.items():
        ok = [w for w in sorted(ws, key=lambda w: w["thu_tu"]) if eligible(w)]
        if ok:
            assigned[ts] = ok[0]
    rounds = []
    for r in range(1, 7):
        counts = {ma: 0 for ma in majors}
        for ts, w in assigned.items():
            if removed_round.get(ts, 99) > r:
                counts[w["ma_xet_tuyen"]] += 1
        for ma, n in counts.items():
            mj = majors[ma]
            rounds.append({"vong": r, "ma_xet_tuyen": ma, "diem_chuan_du_kien": mj["c100"] if mj["c100"] else PT405_CUTOFF,
                           "so_du_kien_trung_tuyen": n})
    admitted = {ts: w for ts, w in assigned.items() if ts not in removed_round}

    # Lỗi cài sẵn trong danh sách trúng tuyển, để trình diễn rà soát
    planted = []
    no_residence = [ts for ts, ws in wish_by_person.items() if ts not in admitted and ts not in removed_round and not person[ts]["thuong_tru_nghe_an"]
                    and any(w["ma_xet_tuyen"] == "7140247" and w["phuong_thuc"] == "100" for w in ws)]
    for ts in no_residence[:2]:
        w = next(w for w in wish_by_person[ts] if w["ma_xet_tuyen"] == "7140247" and w["phuong_thuc"] == "100")
        w["diem_xet"] = max(w["diem_xet"], 21.5)
        admitted[ts] = w
        planted.append((ts, "Trúng tuyển ngành giáo viên nhưng không thường trú Nghệ An"))
    below = [w for ts, ws in wish_by_person.items() if ts not in admitted and ts not in removed_round for w in ws
             if w["ma_xet_tuyen"] == "7340301" and w["phuong_thuc"] == "100" and 15.0 <= w["diem_xet"] < 16]
    if below:
        admitted[below[0]["ma_ts"]] = below[0]
        planted.append((below[0]["ma_ts"], "Điểm xét dưới điểm chuẩn"))
    late = [w for ts, ws in wish_by_person.items() if ts not in admitted and ts not in removed_round for w in ws
            if w["ma_xet_tuyen"] == "7140202" and w["thu_tu"] > 5 and w["phuong_thuc"] == "100" and w["diem_xet"] >= 23
            and person[ts]["thuong_tru_nghe_an"]]
    if late:
        admitted[late[0]["ma_ts"]] = late[0]
        planted.append((late[0]["ma_ts"], "Trúng tuyển ngành giáo viên ở nguyện vọng thứ tự lớn hơn 5"))

    def status(w: dict) -> str:  # trạng thái từng nguyện vọng sau lần xử lý cuối, như dữ liệu Hệ thống trả về
        if w["ma_ts"] in removed_round:
            return "Trúng nguyện vọng cao hơn (trường khác)"
        got = admitted.get(w["ma_ts"])
        if got is w:
            return "Trúng tuyển"
        if got is not None and got["thu_tu"] < w["thu_tu"]:
            return "Trúng nguyện vọng cao hơn (tại Trường)"
        return "Không trúng tuyển"

    # Xác nhận nhập học (10/8 – 21/8), chỉ giữ những lần trước thời điểm chụp dữ liệu; ngày nhập học 17/8
    confirms, checkins = {}, {}
    for ts, w in admitted.items():
        mj = majors[w["ma_xet_tuyen"]]
        if rng.random() < mj["confirm"]:
            t = datetime(2026, 8, 10, 8) + timedelta(hours=min(rng.expovariate(1 / 90), (CONFIRM_DEADLINE - datetime(2026, 8, 10, 8)).total_seconds() / 3600))
            if t <= SNAPSHOT:
                confirms[ts] = t
    for ts, t in confirms.items():
        if t <= datetime(2026, 8, 17, 17) and rng.random() < 0.88:
            mj = majors[admitted[ts]["ma_xet_tuyen"]]
            start = 7.5 if mj["nhom"] in MORNING else 13.5
            thieu = ""
            if person[ts]["doi_tuong"] and rng.random() < 0.3:
                thieu = "Bản chính minh chứng ưu tiên"
            elif rng.random() < 0.06:
                thieu = rng.choice(["Học bạ THPT", "Giấy chứng nhận tốt nghiệp tạm thời", "Ảnh 3x4"])
            checkins[ts] = {"thoi_diem": datetime(2026, 8, 17) + timedelta(hours=start + rng.random() * 3.5), "thieu": thieu,
                            "da_nop_hoc_phi": int(mj["sp"] or rng.random() < 0.86), "dang_ky_nd116": int(mj["sp"] and rng.random() < 0.72)}

    # Hồ sơ giấy của PT 402 (bưu điện hoặc nộp trực tiếp; hạn 17h ngày 17/7 theo dấu bưu cục, TS-309)
    paper = []
    for n, w in enumerate(sorted({w["ma_ts"]: w for w in wishes if w["phuong_thuc"] == "402"}.values(), key=lambda w: w["ma_ts"]), 1):
        post = rng.random() < 0.6
        stamp = datetime(2026, 7, 3) + timedelta(hours=rng.random() * 15 * 24)
        missing = rng.choice(["Bản sao giấy chứng nhận kết quả ĐGNL", "Phiếu đăng ký xét tuyển có chữ ký", "Bản sao CCCD"]) if rng.random() < 0.16 else ""
        late_ = post and stamp > datetime(2026, 7, 17, 17)
        paper.append({"ma_ho_so": f"HS402-{n:04d}", "ma_ts": w["ma_ts"], "phuong_thuc": "402", "kenh_nop": "Bưu điện" if post else "Trực tiếp",
                      "ngay_dau_buu_cuc": stamp.strftime("%Y-%m-%d %H:%M") if post else None,
                      "ngay_nhan": (stamp + timedelta(days=rng.randint(1, 3) if post else 0)).strftime("%Y-%m-%d"),
                      "trang_thai": "Trễ hạn" if late_ else "Thiếu giấy tờ" if missing else "Đủ", "thieu": missing})

    # Nhật ký tư vấn 3–8/2026
    topics = [("Điểm chuẩn", 22), ("Học phí", 16), ("Tổ hợp, phương thức", 15), ("Hồ sơ, thủ tục", 14), ("Học bổng", 9),
              ("Ký túc xá", 8), ("Nhập học", 10), ("Khác", 6)]
    consult = []
    for n in range(1, round(2400 * scale) + 1):
        month = rng.choices([3, 4, 5, 6, 7, 8], weights=[6, 7, 9, 14, 30, 34])[0]
        t = datetime(2026, month, 1) + timedelta(hours=rng.random() * 28 * 24)
        if t > SNAPSHOT:
            continue
        answered = int(rng.random() < (0.9 if month >= 7 else 0.97))
        consult.append({"id": n, "thoi_diem": t.strftime("%Y-%m-%d %H:%M"), "kenh": weighted(rng, [("Hotline", 30), ("Zalo", 32), ("Fanpage", 26), ("Email", 6), ("Trực tiếp", 6)]),
                        "chu_de": weighted(rng, topics), "ma_xet_tuyen": rng.choice(list(majors)) if rng.random() < 0.6 else None,
                        "da_tra_loi": answered, "phut_phan_hoi": int(rng.expovariate(1 / (45 if month >= 7 else 20))) if answered else None})

    # Lịch sử 2024, 2025 (giả lập theo cùng cỡ); 2024 của ngành kinh tế, nông lâm là số của Trường ĐH Kinh tế Nghệ An (mã CEA),
    # của CĐ Giáo dục Mầm non là số của Trường CĐSP Nghệ An, trước sáp nhập
    history = []
    for m in majors.values():
        if m["ma"] in NEW_2026:
            continue
        for year, factor in ((2024, 0.88), (2025, 0.95)):
            quota = round(m["chi_tieu"] * rng.uniform(0.85, 1.05) / 10) * 10
            nv1 = round(m["demand"] * scale * 0.34 * factor * rng.uniform(0.85, 1.2))
            adm = round(quota * rng.uniform(0.7, 1.05))
            conf = round(adm * min(0.95, m["confirm"] + rng.uniform(-0.05, 0.08)))
            note = ("Trường CĐSP Nghệ An, trước sáp nhập" if m["ma"] == "51140201" and year == 2024
                    else "Trường ĐH Kinh tế Nghệ An (mã CEA), trước sáp nhập" if year == 2024 else "mã trường CEA")
            history.append({"nam": year, "ma_xet_tuyen": m["ma"], "chi_tieu": quota, "so_nv1": nv1, "trung_tuyen": adm,
                            "xac_nhan": conf, "nhap_hoc": round(conf * rng.uniform(0.9, 0.97)), "ghi_chu": note})

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    meta = {"thoi_diem_du_lieu": SNAPSHOT.strftime("%H:%M ngày %d/%m/%Y"), "han_xac_nhan": "17:00 ngày 21/08/2026",
            "ghi_chu": "DỮ LIỆU GIẢ LẬP để trình diễn; không phải dữ liệu thật của Trường. Ngành, mã, chỉ tiêu, điểm chuẩn lấy từ văn bản công khai (TS-100, TS-202, TS-309); thí sinh, nguyện vọng, xác nhận nhập học là giả.",
            "hat_giong": str(seed), "ty_le": str(scale)}
    db.executemany("INSERT INTO meta VALUES (?, ?)", meta.items())
    db.executemany("INSERT INTO nganh VALUES (?,?,?,?,?,?,?,?,?)",
                   [(m["ma"], m["ten"], m["nhom"], "Cao đẳng" if m["ma"] == "51140201" else "Đại học", m["chi_tieu"], m["c100"], m["c200"],
                     PT405_CUTOFF if m["ma"] == "51140201" else None, int(m["sp"])) for m in majors.values()])
    cols = list(people[0])
    db.executemany(f"INSERT INTO thi_sinh ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", [tuple(p[c] for c in cols) for p in people])
    db.executemany("INSERT INTO nguyen_vong VALUES (?,?,?,?,?,?)",
                   [(w["ma_ts"], w["thu_tu"], w["ma_xet_tuyen"], w["phuong_thuc"], w["diem_xet"], status(w)) for w in wishes])
    db.executemany("INSERT INTO loc_ao VALUES (?,?,?,?)", [(r["vong"], r["ma_xet_tuyen"], r["diem_chuan_du_kien"], r["so_du_kien_trung_tuyen"]) for r in rounds])
    db.executemany("INSERT INTO trung_tuyen VALUES (?,?,?,?,?,1,'2026-08-10')",
                   [(ts, w["ma_xet_tuyen"], w["phuong_thuc"], w["thu_tu"], w["diem_xet"]) for ts, w in admitted.items()])
    db.executemany("INSERT INTO xac_nhan VALUES (?,?)", [(ts, t.strftime("%Y-%m-%d %H:%M")) for ts, t in confirms.items()])
    db.executemany("INSERT INTO nhap_hoc VALUES (?,?,?,?,?,?)",
                   [(ts, c["thoi_diem"].strftime("%Y-%m-%d %H:%M"), "Thiếu hồ sơ" if c["thieu"] else "Hoàn tất", c["thieu"], c["da_nop_hoc_phi"], c["dang_ky_nd116"])
                    for ts, c in checkins.items()])
    db.executemany("INSERT INTO ho_so_giay VALUES (?,?,?,?,?,?,?,?)", [tuple(h.values()) for h in paper])
    db.executemany("INSERT INTO tu_van VALUES (?,?,?,?,?,?,?)", [tuple(c.values()) for c in consult])
    db.executemany("INSERT INTO lich_su VALUES (?,?,?,?,?,?,?,?)", [tuple(h.values()) for h in history])
    db.executemany("INSERT INTO _loi_cai_san VALUES (?,?)", planted)
    db.commit()
    db.close()
    return {"thi_sinh": len(people), "nguyen_vong": len(wishes), "trung_tuyen": len(admitted), "xac_nhan": len(confirms),
            "nhap_hoc": len(checkins), "ho_so_giay": len(paper), "tu_van": len(consult), "loi_cai_san": len(planted)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Tạo cơ sở dữ liệu tuyển sinh 2026 giả lập")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()
    counts = build(Path(args.out), args.scale)
    print(f"Đã ghi {args.out}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
