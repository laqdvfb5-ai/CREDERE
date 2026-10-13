"""Danh mục truy vấn đã duyệt của cơ sở dữ liệu học vụ (tác tử Dữ liệu của AI Đào tạo)."""
import math
import sqlite3

from ..tools.data import Param, Query

HOC_KY = ("2023-2024-1", "2023-2024-2", "2024-2025-1", "2024-2025-2", "2025-2026-1", "2025-2026-2", "2025-2026-he")
LATEST = "2025-2026-2"
HK = Param("hoc_ky", "choice", f"học kỳ, dạng năm học-số học kỳ ({', '.join(HOC_KY)}); mặc định {LATEST}", default=LATEST, choices=HOC_KY)
HK_ALL = Param("hoc_ky", "choice", "học kỳ; bỏ trống là mọi học kỳ", choices=HOC_KY)
KHOA = Param("khoa", "choice", "khóa K10 (nhập học 2023), K11 (2024), K12 (2025); bỏ trống là mọi khóa", choices=("K10", "K11", "K12"))
NG = Param("ma_nganh", "nganh", "mã ngành; bỏ trống là mọi ngành")
F_NG = "(:ma_nganh IS NULL OR s.ma_nganh = :ma_nganh)"
F_KHOA = "(:khoa IS NULL OR s.khoa = :khoa)"
META_INT = "(SELECT CAST(gia_tri AS INTEGER) FROM meta WHERE khoa = '{}')"
ROI_TRUONG = "('Thôi học (tự nguyện)', 'Buộc thôi học')"


def _open_classes(conn: sqlite3.Connection, p: dict) -> tuple[list[str], list[list]]:
    """Dự kiến số lớp học phần cho một học kỳ của chương trình đào tạo, với số sinh viên cho trước và sĩ số tối đa của Trường."""
    max_size = int(conn.execute("SELECT gia_tri FROM meta WHERE khoa = 'si_so_toi_da_lop'").fetchone()[0])
    rows = conn.execute("""SELECT h.ma_hp, h.ten_hp, h.so_tin_chi, h.loai FROM chuong_trinh c JOIN hoc_phan h ON h.ma_hp = c.ma_hp
                           WHERE c.ma_nganh = :ma_nganh AND c.hoc_ky_du_kien = :hoc_ky_thu ORDER BY h.loai, h.ma_hp""", p).fetchall()
    n = p["so_sinh_vien"]
    out = []
    for ma, ten, tc, loai in rows:
        lop = max(1, math.ceil(n / max_size))
        out.append([ma, ten, tc, loai, lop, math.ceil(n / lop)])
    return ["ma_hp", "ten_hp", "so_tin_chi", "loai", "so_lop_can_mo", "si_so_moi_lop"], out


QUERIES = [
    Query("tham_so_dao_tao", "Tham số đào tạo của Trường lưu trong hệ thống: tín chỉ tối đa, tối thiểu mỗi học kỳ, sĩ số tối đa lớp học phần, "
          "sĩ số tối thiểu để mở lớp, trọng số điểm, điều kiện buộc thôi học", """
        SELECT khoa AS tham_so, gia_tri FROM meta WHERE khoa IN ('tin_chi_toi_da_hoc_ky', 'tin_chi_toi_thieu_hoc_ky', 'si_so_toi_da_lop',
               'si_so_toi_thieu_mo_lop', 'trong_so_diem', 'buoc_thoi_hoc', 'nam_hoc_hien_tai', 'nguon_tham_so') ORDER BY khoa""",
          ghi_chu="Nguồn từng tham số xem dòng nguon_tham_so; sĩ số tối đa lớp là giả lập. Khi nối dữ liệu thật, lấy từ phần mềm quản lý đào tạo."),
    Query("tong_quan_hoc_vu", "Tổng quan học vụ: sinh viên theo tình trạng, số lớp học phần và cảnh báo học kỳ 2 năm học 2025–2026", f"""
        SELECT (SELECT COUNT(*) FROM sinh_vien WHERE trang_thai = 'Đang học') AS dang_hoc,
               (SELECT COUNT(*) FROM sinh_vien WHERE trang_thai = 'Bảo lưu') AS bao_luu,
               (SELECT COUNT(*) FROM sinh_vien WHERE trang_thai IN {ROI_TRUONG}) AS roi_truong,
               (SELECT COUNT(*) FROM sinh_vien WHERE trang_thai = 'Buộc thôi học') AS trong_do_buoc_thoi_hoc,
               (SELECT COUNT(*) FROM lop_hoc_phan WHERE hoc_ky = '{LATEST}') AS so_lop_hoc_phan_hk2,
               (SELECT COUNT(*) FROM ket_qua_hoc_ky WHERE hoc_ky = '{LATEST}' AND muc_canh_bao > 0) AS canh_bao_hk2,
               (SELECT ROUND(AVG(dtb_hk), 2) FROM ket_qua_hoc_ky WHERE hoc_ky = '{LATEST}') AS dtb_hk2_trung_binh"""),
    Query("si_so_theo_nganh_khoa", "Sĩ số theo ngành và khóa: nhập học, đang học, bảo lưu, thôi học, buộc thôi học, tỷ lệ rời trường", f"""
        SELECT n.ma_nganh, n.ten_nganh, s.khoa, COUNT(*) AS nhap_hoc, SUM(s.trang_thai = 'Đang học') AS dang_hoc, SUM(s.trang_thai = 'Bảo lưu') AS bao_luu,
               SUM(s.trang_thai = 'Thôi học (tự nguyện)') AS thoi_hoc, SUM(s.trang_thai = 'Buộc thôi học') AS buoc_thoi_hoc,
               ROUND(100.0 * SUM(s.trang_thai IN {ROI_TRUONG}) / COUNT(*), 1) AS phan_tram_roi_truong
        FROM sinh_vien s JOIN nganh n ON n.ma_nganh = s.ma_nganh
        WHERE {F_NG} AND {F_KHOA} GROUP BY n.ma_nganh, s.khoa ORDER BY n.ma_nganh, s.khoa""", (NG, KHOA),
          tong=("nhap_hoc", "dang_hoc", "bao_luu", "thoi_hoc", "buoc_thoi_hoc")),
    Query("ket_qua_hoc_tap_theo_nganh", "Kết quả học tập một học kỳ theo ngành: điểm trung bình, tỷ lệ xếp loại", f"""
        SELECT n.ma_nganh, n.ten_nganh, COUNT(*) AS so_sv, ROUND(AVG(k.dtb_hk), 2) AS dtb_hoc_ky, ROUND(AVG(k.dtb_tich_luy), 2) AS dtb_tich_luy,
               ROUND(100.0 * SUM(k.xep_loai IN ('Xuất sắc', 'Giỏi')) / COUNT(*), 1) AS pt_gioi_tro_len,
               ROUND(100.0 * SUM(k.xep_loai = 'Khá') / COUNT(*), 1) AS pt_kha, ROUND(100.0 * SUM(k.xep_loai = 'Trung bình') / COUNT(*), 1) AS pt_trung_binh,
               ROUND(100.0 * SUM(k.xep_loai IN ('Yếu', 'Kém')) / COUNT(*), 1) AS pt_yeu_kem, SUM(k.xep_loai IN ('Yếu', 'Kém')) AS so_sv_yeu_kem
        FROM ket_qua_hoc_ky k JOIN sinh_vien s ON s.ma_sv = k.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
        WHERE k.hoc_ky = :hoc_ky AND {F_NG} AND {F_KHOA} GROUP BY n.ma_nganh ORDER BY dtb_hoc_ky DESC""", (HK, KHOA, NG),
          ghi_chu="Xếp loại theo điểm trung bình học kỳ thang 4 (TT 08/2021, Điều 10).",
          tong=("so_sv", "so_sv_yeu_kem")),
    Query("ket_qua_theo_phuong_thuc", "Kết quả học tập, cảnh báo và rời trường theo khóa và phương thức trúng tuyển (100 điểm thi tốt nghiệp, 200 học bạ, 301 tuyển thẳng, 402 ĐGNL), kèm dòng tất cả các khóa; toàn trường hoặc một ngành", f"""
        SELECT s.khoa, s.phuong_thuc_trung_tuyen, COUNT(*) AS so_sv_nhap_hoc, ROUND(AVG(s.diem_trung_tuyen), 2) AS diem_trung_tuyen_tb,
               COUNT(k.ma_sv) AS so_sv_co_ket_qua_hk2, ROUND(AVG(k.dtb_tich_luy), 2) AS dtb_tich_luy_tb,
               COALESCE(SUM(k.muc_canh_bao > 0), 0) AS so_sv_canh_bao_hk2, ROUND(100.0 * SUM(k.muc_canh_bao > 0) / COUNT(k.ma_sv), 1) AS pt_canh_bao_hk2,
               SUM(s.trang_thai IN {ROI_TRUONG}) AS so_sv_roi_truong, ROUND(100.0 * SUM(s.trang_thai IN {ROI_TRUONG}) / COUNT(*), 1) AS pt_roi_truong
        FROM sinh_vien s LEFT JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = '{LATEST}'
        WHERE {F_NG} AND {F_KHOA} GROUP BY s.khoa, s.phuong_thuc_trung_tuyen
        UNION ALL
        SELECT 'Tất cả các khóa', s.phuong_thuc_trung_tuyen, COUNT(*) AS so_sv_nhap_hoc, ROUND(AVG(s.diem_trung_tuyen), 2) AS diem_trung_tuyen_tb,
               COUNT(k.ma_sv) AS so_sv_co_ket_qua_hk2, ROUND(AVG(k.dtb_tich_luy), 2) AS dtb_tich_luy_tb,
               COALESCE(SUM(k.muc_canh_bao > 0), 0) AS so_sv_canh_bao_hk2, ROUND(100.0 * SUM(k.muc_canh_bao > 0) / COUNT(k.ma_sv), 1) AS pt_canh_bao_hk2,
               SUM(s.trang_thai IN {ROI_TRUONG}) AS so_sv_roi_truong, ROUND(100.0 * SUM(s.trang_thai IN {ROI_TRUONG}) / COUNT(*), 1) AS pt_roi_truong
        FROM sinh_vien s LEFT JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = '{LATEST}'
        WHERE {F_NG} AND {F_KHOA} GROUP BY s.phuong_thuc_trung_tuyen
        ORDER BY 1, 2""", (NG, KHOA),
          ghi_chu=f"Điểm trung bình tích lũy và cảnh báo tính ở học kỳ {LATEST}; tỷ lệ rời trường tính trên số nhập học."),
    Query("ket_qua_theo_nganh_phuong_thuc", "Điểm trung bình tích lũy, cảnh báo, rời trường theo ngành và phương thức trúng tuyển (100 điểm thi, 200 học bạ)", f"""
        SELECT n.ma_nganh, n.ten_nganh, s.phuong_thuc_trung_tuyen, COUNT(*) AS so_sv_nhap_hoc, COUNT(k.ma_sv) AS so_sv_co_ket_qua_hk2,
               ROUND(AVG(k.dtb_tich_luy), 2) AS dtb_tich_luy_tb, COALESCE(SUM(k.muc_canh_bao > 0), 0) AS so_sv_canh_bao_hk2,
               ROUND(100.0 * SUM(k.muc_canh_bao > 0) / COUNT(k.ma_sv), 1) AS pt_canh_bao_hk2,
               SUM(s.trang_thai IN {ROI_TRUONG}) AS so_sv_roi_truong, ROUND(100.0 * SUM(s.trang_thai IN {ROI_TRUONG}) / COUNT(*), 1) AS pt_roi_truong
        FROM sinh_vien s JOIN nganh n ON n.ma_nganh = s.ma_nganh LEFT JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = '{LATEST}'
        WHERE s.phuong_thuc_trung_tuyen IN ('100', '200') AND {F_KHOA} GROUP BY n.ma_nganh, s.phuong_thuc_trung_tuyen
        ORDER BY n.ma_nganh, s.phuong_thuc_trung_tuyen""", (KHOA,),
          ghi_chu=f"Chỉ hai phương thức đông nhất (100, 200); học kỳ {LATEST}; lọc được theo một khóa.",
          tong=("so_sv_nhap_hoc", "so_sv_co_ket_qua_hk2", "so_sv_canh_bao_hk2", "so_sv_roi_truong")),
    Query("canh_bao_hoc_vu_theo_nganh", "Cảnh báo học vụ một học kỳ theo ngành và khóa: số sinh viên cảnh báo mức 1, mức 2 và lý do", f"""
        SELECT n.ma_nganh, n.ten_nganh, s.khoa, COUNT(*) AS so_sv, SUM(k.muc_canh_bao = 1) AS canh_bao_muc_1, SUM(k.muc_canh_bao = 2) AS canh_bao_muc_2,
               ROUND(100.0 * SUM(k.muc_canh_bao > 0) / COUNT(*), 1) AS phan_tram_canh_bao,
               SUM(k.ly_do_canh_bao LIKE '%tích lũy dưới%') AS ly_do_dtb_tich_luy, SUM(k.ly_do_canh_bao LIKE '%học kỳ dưới%') AS ly_do_dtb_hoc_ky,
               SUM(k.ly_do_canh_bao LIKE '%50%') AS ly_do_tin_chi_khong_dat, SUM(k.ly_do_canh_bao LIKE '%nợ đọng%') AS ly_do_no_dong
        FROM ket_qua_hoc_ky k JOIN sinh_vien s ON s.ma_sv = k.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
        WHERE k.hoc_ky = :hoc_ky AND {F_KHOA} AND {F_NG} GROUP BY n.ma_nganh, s.khoa ORDER BY n.ma_nganh, s.khoa""", (HK, KHOA, NG),
          ghi_chu="Mức 2: cảnh báo từ hai học kỳ liên tiếp trở lên. Ngưỡng theo TT 08/2021, Điều 11; một sinh viên có thể có nhiều lý do.",
          tong=("so_sv", "canh_bao_muc_1", "canh_bao_muc_2", "ly_do_dtb_tich_luy", "ly_do_dtb_hoc_ky", "ly_do_tin_chi_khong_dat", "ly_do_no_dong")),
    Query("danh_sach_canh_bao", "Danh sách sinh viên bị cảnh báo học vụ trong một học kỳ", f"""
        SELECT s.ma_sv, s.ho_ten, s.sdt, s.email, n.ten_nganh, s.lop, k.dtb_hk, k.dtb_tich_luy, k.tc_no_tich_luy, k.muc_canh_bao,
               k.ly_do_canh_bao, s.ma_co_van
        FROM ket_qua_hoc_ky k JOIN sinh_vien s ON s.ma_sv = k.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
        WHERE k.hoc_ky = :hoc_ky AND k.muc_canh_bao > 0 AND {F_NG} AND {F_KHOA} ORDER BY n.ten_nganh, k.muc_canh_bao DESC, s.ma_sv""",
          (HK, NG, KHOA), ca_nhan=True, group_by=("ten_nganh", "muc_canh_bao")),
    Query("hoc_phan_ty_le_truot", "Học phần có tỷ lệ trượt (điểm F) cao nhất trong một học kỳ", """
        SELECT h.ma_hp, h.ten_hp, h.loai, COUNT(*) AS so_luot_thi, SUM(d.diem_chu = 'F') AS so_luot_truot,
               ROUND(100.0 * SUM(d.diem_chu = 'F') / COUNT(*), 1) AS pt_truot,
               ROUND(AVG(d.diem_hp), 2) AS diem_hp_trung_binh
        FROM diem d JOIN lop_hoc_phan l ON l.ma_lhp = d.ma_lhp JOIN hoc_phan h ON h.ma_hp = l.ma_hp
        WHERE l.hoc_ky = :hoc_ky GROUP BY h.ma_hp HAVING COUNT(*) >= 30 ORDER BY pt_truot DESC LIMIT :top""",
          (HK, Param("top", "int", "số học phần, mặc định 10", lo=1, hi=40, default=10))),
    Query("chuong_trinh_dao_tao", "Chương trình đào tạo của một ngành: học phần theo học kỳ dự kiến, số tín chỉ, loại", """
        SELECT c.hoc_ky_du_kien, h.ma_hp, h.ten_hp, h.so_tin_chi, h.loai FROM chuong_trinh c JOIN hoc_phan h ON h.ma_hp = c.ma_hp
        WHERE c.ma_nganh = :ma_nganh AND (:hoc_ky_thu IS NULL OR c.hoc_ky_du_kien = :hoc_ky_thu) ORDER BY c.hoc_ky_du_kien, h.ma_hp""",
          (Param("ma_nganh", "nganh", "mã ngành", required=True), Param("hoc_ky_thu", "int", "học kỳ thứ mấy của khóa (1–8); bỏ trống là cả chương trình", lo=1, hi=8)),
          ghi_chu="Chương trình trong cơ sở dữ liệu giả lập là bản rút gọn; tổng tín chỉ chính thức xem văn bản chương trình đào tạo."),
    Query("lop_hoc_phan_tong_hop", "Lớp học phần của một học kỳ theo ngành: số lớp, sĩ số trung bình, lớp vượt sĩ số tối đa, lớp dưới sĩ số tối thiểu", f"""
        SELECT l.ma_nganh, COALESCE(n.ten_nganh, '(học kỳ hè, học lại chung)') AS ten_nganh, COUNT(*) AS so_lop, ROUND(AVG(l.si_so), 1) AS si_so_tb,
               MAX(l.si_so) AS si_so_lon_nhat, SUM(l.si_so > {META_INT.format('si_so_toi_da_lop')}) AS lop_vuot_si_so_toi_da,
               SUM(l.si_so < {META_INT.format('si_so_toi_thieu_mo_lop')}) AS lop_duoi_si_so_toi_thieu
        FROM lop_hoc_phan l LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
        WHERE l.hoc_ky = :hoc_ky AND (:ma_nganh IS NULL OR l.ma_nganh = :ma_nganh) GROUP BY l.ma_nganh ORDER BY so_lop DESC""", (HK, NG),
          ghi_chu="Sĩ số tối đa 70 là tham số giả lập (không có văn bản quy định); tối thiểu để mở lớp 10 theo QĐ 881 Điều 9.",
          tong=("so_lop", "lop_vuot_si_so_toi_da", "lop_duoi_si_so_toi_thieu")),
    Query("du_kien_mo_lop", "Kịch bản: với số sinh viên cho trước, một học kỳ của chương trình đào tạo cần mở bao nhiêu lớp học phần", params=(
        Param("ma_nganh", "nganh", "mã ngành", required=True),
        Param("so_sinh_vien", "int", "số sinh viên dự kiến (ví dụ số tân sinh viên đã xác nhận nhập học)", required=True, lo=1, hi=3000),
        Param("hoc_ky_thu", "int", "học kỳ thứ mấy của khóa, mặc định 1", lo=1, hi=8, default=1)),
          compute=_open_classes, ghi_chu="Số lớp = làm tròn lên (số sinh viên / sĩ số tối đa 70, tham số giả lập); tham khảo để lập kế hoạch. "
                                          "Danh sách học phần lấy từ chương trình rút gọn trong cơ sở dữ liệu giả lập; học phần chính thức xem văn bản chương trình đào tạo."),
    Query("lich_thi_tong_hop", "Lịch thi một học kỳ theo ngày: số môn thi, số lượt sinh viên, số phòng", """
        SELECT t.ngay, COUNT(*) AS so_mon_thi, SUM(l.si_so) AS so_luot_sinh_vien, COUNT(DISTINCT t.phong) AS so_phong
        FROM lich_thi t JOIN lop_hoc_phan l ON l.ma_lhp = t.ma_lhp WHERE t.hoc_ky = :hoc_ky GROUP BY t.ngay ORDER BY t.ngay""",
          (Param("hoc_ky", "choice", "học kỳ có lịch thi; hiện có 2025-2026-he (thi 20–28/8/2026)", default="2025-2026-he", choices=HOC_KY),),
          tong=("so_luot_sinh_vien",)),
    Query("doi_soat_hoc_vu", "Rà soát dữ liệu học vụ: đăng ký vượt tín chỉ tối đa, trùng lịch thi, điểm học phần không khớp điểm thành phần", f"""
        SELECT s.ma_sv, s.ho_ten, n.ten_nganh, d.hoc_ky, SUM(h.so_tin_chi) || ' tín chỉ' AS chi_tiet, 'Đăng ký vượt số tín chỉ tối đa' AS loi
          FROM dang_ky d JOIN lop_hoc_phan l ON l.ma_lhp = d.ma_lhp JOIN hoc_phan h ON h.ma_hp = l.ma_hp
          JOIN sinh_vien s ON s.ma_sv = d.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
         WHERE (:hoc_ky IS NULL OR d.hoc_ky = :hoc_ky) GROUP BY s.ma_sv, d.hoc_ky HAVING SUM(h.so_tin_chi) > {META_INT.format('tin_chi_toi_da_hoc_ky')}
        UNION ALL
        SELECT s.ma_sv, s.ho_ten, n.ten_nganh, t1.hoc_ky, t1.ngay || ' ca ' || t1.ca, 'Trùng lịch thi'
          FROM dang_ky d1 JOIN lich_thi t1 ON t1.ma_lhp = d1.ma_lhp JOIN dang_ky d2 ON d2.ma_sv = d1.ma_sv AND d2.ma_lhp > d1.ma_lhp
          JOIN lich_thi t2 ON t2.ma_lhp = d2.ma_lhp AND t2.ngay = t1.ngay AND t2.ca = t1.ca
          JOIN sinh_vien s ON s.ma_sv = d1.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
         WHERE (:hoc_ky IS NULL OR t1.hoc_ky = :hoc_ky)
        UNION ALL
        SELECT s.ma_sv, s.ho_ten, n.ten_nganh, l.hoc_ky, d.ma_lhp || ': ' || d.diem_hp || ' so với ' || ROUND(0.4 * d.diem_qt + 0.6 * d.diem_thi, 1),
               'Điểm học phần không khớp điểm thành phần'
          FROM diem d JOIN lop_hoc_phan l ON l.ma_lhp = d.ma_lhp JOIN sinh_vien s ON s.ma_sv = d.ma_sv JOIN nganh n ON n.ma_nganh = s.ma_nganh
         WHERE (:hoc_ky IS NULL OR l.hoc_ky = :hoc_ky) AND ABS(d.diem_hp - ROUND(0.4 * d.diem_qt + 0.6 * d.diem_thi, 1)) > 0.05
        ORDER BY loi, hoc_ky""", (HK_ALL,), ca_nhan=True, group_by=("loi",),
          ghi_chu="Đã kiểm 3 quy tắc: vượt tín chỉ tối đa của học kỳ (26, QĐ 620 Điều 8); trùng ngày và ca thi; điểm học phần khác 40% quá trình + 60% thi. "
                  "Quy tắc không có trong tong_hop là không phát hiện trường hợp nào. Lớp vượt sĩ số xem truy vấn lop_hoc_phan_tong_hop."),
    Query("tai_giang", "Tải giảng dạy một học kỳ theo giảng viên (mã giảng viên): số lớp, số tín chỉ, tổng sinh viên", """
        SELECT g.ma_gv, g.bo_mon, COUNT(*) AS so_lop, SUM(h.so_tin_chi) AS tong_tin_chi, SUM(l.si_so) AS tong_sinh_vien
        FROM lop_hoc_phan l JOIN giang_vien g ON g.ma_gv = l.ma_gv JOIN hoc_phan h ON h.ma_hp = l.ma_hp
        WHERE l.hoc_ky = :hoc_ky GROUP BY g.ma_gv ORDER BY tong_tin_chi DESC LIMIT :top""",
          (HK, Param("top", "int", "số giảng viên, mặc định 15", lo=1, hi=60, default=15))),
    Query("xet_tot_nghiep_du_kien", "Sinh viên một khóa có vấn đề cần xử lý trước xét tốt nghiệp: chưa đạt chuẩn ngoại ngữ, còn nợ học phần, điểm tích lũy dưới 2,0", f"""
        SELECT s.ma_sv, s.ho_ten, s.sdt, n.ten_nganh, s.lop, 'Chưa đạt chuẩn đầu ra ngoại ngữ' AS van_de, '' AS chi_tiet, s.ma_co_van
          FROM sinh_vien s JOIN nganh n ON n.ma_nganh = s.ma_nganh JOIN chuan_dau_ra c ON c.ma_sv = s.ma_sv
         WHERE s.khoa = :khoa AND s.trang_thai = 'Đang học' AND c.ngoai_ngu_dat = 0 AND {F_NG}
        UNION ALL
        SELECT s.ma_sv, s.ho_ten, s.sdt, n.ten_nganh, s.lop, 'Còn nợ học phần', k.tc_no_tich_luy || ' tín chỉ', s.ma_co_van
          FROM sinh_vien s JOIN nganh n ON n.ma_nganh = s.ma_nganh JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = '{LATEST}'
         WHERE s.khoa = :khoa AND s.trang_thai = 'Đang học' AND k.tc_no_tich_luy > 0 AND {F_NG}
        UNION ALL
        SELECT s.ma_sv, s.ho_ten, s.sdt, n.ten_nganh, s.lop, 'Điểm trung bình tích lũy dưới 2,0', k.dtb_tich_luy, s.ma_co_van
          FROM sinh_vien s JOIN nganh n ON n.ma_nganh = s.ma_nganh JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = '{LATEST}'
         WHERE s.khoa = :khoa AND s.trang_thai = 'Đang học' AND k.dtb_tich_luy < 2.0 AND {F_NG}
        ORDER BY van_de, ten_nganh""", (Param("khoa", "choice", "khóa, mặc định K10 (sắp tốt nghiệp)", default="K10", choices=("K10", "K11", "K12")), NG),
          ca_nhan=True, group_by=("van_de",),
          ghi_chu="Điều kiện tốt nghiệp đầy đủ xem quy chế đào tạo; một sinh viên có thể có nhiều vấn đề."),
    Query("lop_cua_giang_vien", "Sinh viên đang bị cảnh báo hoặc điểm tích lũy dưới 2,0 trong các lớp học phần của một giảng viên", """
        SELECT l.ma_lhp, h.ten_hp, s.ma_sv, s.ho_ten, k.dtb_tich_luy, k.muc_canh_bao
        FROM lop_hoc_phan l JOIN hoc_phan h ON h.ma_hp = l.ma_hp JOIN dang_ky d ON d.ma_lhp = l.ma_lhp
        JOIN sinh_vien s ON s.ma_sv = d.ma_sv JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = l.hoc_ky
        WHERE l.ma_gv = :ma_gv AND l.hoc_ky = :hoc_ky AND (k.muc_canh_bao > 0 OR k.dtb_tich_luy < 2.0)
        ORDER BY l.ma_lhp, k.dtb_tich_luy""",
          (Param("ma_gv", "text", "mã giảng viên, ví dụ GV045", required=True), HK), ca_nhan=True, group_by=("ma_lhp", "ten_hp")),
]
