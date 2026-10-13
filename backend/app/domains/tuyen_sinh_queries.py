"""Danh mục truy vấn đã duyệt của cơ sở dữ liệu tuyển sinh (tác tử Dữ liệu của AI Tuyển sinh)."""
import sqlite3

from ..tools.data import Param, Query

NGANH = Param("ma_xet_tuyen", "nganh", "mã xét tuyển của ngành; bỏ trống là mọi ngành")
FILTER = "(:ma_xet_tuyen IS NULL OR n.ma_xet_tuyen = :ma_xet_tuyen)"


def _simulate(conn: sqlite3.Connection, p: dict) -> tuple[list[str], list[list]]:
    """Kịch bản điểm chuẩn: đổi điểm chuẩn của một ngành, một phương thức, giữ nguyên các ngành khác; mỗi thí sinh trúng
    nguyện vọng cao nhất vào Trường mà thí sinh đạt. Không tính thí sinh đã trúng nguyện vọng cao hơn ở trường khác."""
    majors = {r[0]: r for r in conn.execute("SELECT ma_xet_tuyen, diem_chuan_100, diem_chuan_200, diem_chuan_405, la_su_pham, chi_tieu FROM nganh")}

    def cutoff(ma: str, pt: str, override: bool) -> float | None:
        if override and ma == p["ma_xet_tuyen"] and pt == p["phuong_thuc"]:
            return p["diem_chuan"]
        m = majors[ma]
        return {"100": m[1], "402": m[1], "200": m[2], "405": m[3]}.get(pt)

    rows = conn.execute("""SELECT v.ma_ts, v.thu_tu, v.ma_xet_tuyen, v.phuong_thuc, v.diem_xet, s.thuong_tru_nghe_an
        FROM nguyen_vong v JOIN thi_sinh s ON s.ma_ts = v.ma_ts
        WHERE v.ma_ts NOT IN (SELECT ma_ts FROM nguyen_vong WHERE trang_thai = 'Trúng nguyện vọng cao hơn (trường khác)')
        ORDER BY v.ma_ts, v.thu_tu""").fetchall()

    def assign(override: bool) -> dict[str, str]:
        out = {}
        for ts, _, ma, pt, diem, thuong_tru in rows:
            if ts in out:
                continue
            if majors[ma][4] and not thuong_tru:
                continue
            c = cutoff(ma, pt, override)
            if pt == "301" or (c is not None and diem is not None and diem >= c):
                out[ts] = ma
        return out

    before, after = assign(False), assign(True)
    ma = p["ma_xet_tuyen"]
    n_before = sum(1 for v in before.values() if v == ma)
    n_after = sum(1 for v in after.values() if v == ma)
    moved = sum(1 for ts, v in after.items() if v == ma and before.get(ts) not in (None, ma))
    columns = ["ma_xet_tuyen", "phuong_thuc", "diem_chuan_hien_tai", "diem_chuan_mo_phong", "chi_tieu",
               "so_trung_tuyen_hien_tai", "so_trung_tuyen_mo_phong", "chenh_lech", "trong_do_chuyen_tu_nganh_khac_cua_truong"]
    return columns, [[ma, p["phuong_thuc"], cutoff(ma, p["phuong_thuc"], False), p["diem_chuan"], majors[ma][5],
                      n_before, n_after, n_after - n_before, moved]]


QUERIES = [
    Query("tong_quan", "Tổng quan mùa tuyển sinh đến thời điểm dữ liệu", """
        SELECT (SELECT COUNT(DISTINCT ma_ts) FROM nguyen_vong) AS so_thi_sinh_co_nguyen_vong,
               (SELECT COUNT(*) FROM nguyen_vong) AS so_nguyen_vong,
               (SELECT SUM(chi_tieu) FROM nganh) AS tong_chi_tieu,
               (SELECT COUNT(*) FROM trung_tuyen) AS trung_tuyen_dot_1,
               (SELECT COUNT(*) FROM xac_nhan) AS da_xac_nhan_nhap_hoc,
               (SELECT COUNT(*) FROM nhap_hoc) AS da_lam_thu_tuc_nhap_hoc,
               (SELECT SUM(chi_tieu) FROM nganh) - (SELECT COUNT(*) FROM xac_nhan) AS chi_tieu_chua_co_nguoi_xac_nhan"""),
    Query("nguyen_vong_theo_nganh", "Số thí sinh, số nguyện vọng 1, top 3 vào từng ngành, so với nguyện vọng 1 năm 2025", f"""
        SELECT n.ma_xet_tuyen AS ma_nganh, n.ten_nganh, n.chi_tieu, COUNT(DISTINCT v.ma_ts) AS so_thi_sinh,
               COALESCE(SUM(v.thu_tu = 1), 0) AS so_nv1, COALESCE(SUM(v.thu_tu <= 3), 0) AS so_trong_top3,
               l.so_nv1 AS so_nv1_2025, COALESCE(SUM(v.thu_tu = 1), 0) - l.so_nv1 AS chenh_nv1_so_voi_2025
        FROM nganh n LEFT JOIN nguyen_vong v ON v.ma_xet_tuyen = n.ma_xet_tuyen
        LEFT JOIN lich_su l ON l.ma_xet_tuyen = n.ma_xet_tuyen AND l.nam = 2025
        WHERE {FILTER} GROUP BY n.ma_xet_tuyen ORDER BY so_nv1 DESC""", (NGANH,),
          ghi_chu="so_nv1_2025 trống: ngành mới tuyển năm 2026",
          tong=("chi_tieu", "so_nv1", "so_nv1_2025", "chenh_nv1_so_voi_2025")),
    Query("nguyen_vong_theo_phuong_thuc", "Số nguyện vọng và điểm xét trung bình theo ngành và phương thức", f"""
        SELECT n.ten_nganh, v.phuong_thuc, COUNT(*) AS so_nguyen_vong, ROUND(AVG(v.diem_xet), 2) AS diem_xet_trung_binh
        FROM nguyen_vong v JOIN nganh n ON n.ma_xet_tuyen = v.ma_xet_tuyen
        WHERE {FILTER} GROUP BY n.ma_xet_tuyen, v.phuong_thuc ORDER BY n.ma_xet_tuyen, v.phuong_thuc""", (NGANH,),
          tong=("so_nguyen_vong",)),
    Query("loc_ao_theo_vong", "Điểm chuẩn dự kiến và số dự kiến trúng tuyển qua 6 vòng lọc ảo", f"""
        SELECT l.vong, n.ten_nganh, n.chi_tieu, l.diem_chuan_du_kien, l.so_du_kien_trung_tuyen,
               l.so_du_kien_trung_tuyen - LAG(l.so_du_kien_trung_tuyen) OVER (PARTITION BY l.ma_xet_tuyen ORDER BY l.vong) AS thay_doi_so_voi_vong_truoc
        FROM loc_ao l JOIN nganh n ON n.ma_xet_tuyen = l.ma_xet_tuyen
        WHERE {FILTER} ORDER BY n.ma_xet_tuyen, l.vong""", (NGANH,)),
    Query("mo_phong_diem_chuan", "Kịch bản: đổi điểm chuẩn một ngành, một phương thức thì số trúng tuyển thay đổi thế nào", params=(
        Param("ma_xet_tuyen", "nganh", "mã xét tuyển của ngành", required=True),
        Param("phuong_thuc", "phuong_thuc", "100, 200, 402 hoặc 405", required=True),
        Param("diem_chuan", "float", "điểm chuẩn giả định, thang 30", required=True, lo=10, hi=30)),
          compute=_simulate,
          ghi_chu="Tham khảo: tính trên nguyện vọng đợt 1 sau lọc ảo, giữ nguyên điểm chuẩn các ngành khác; điểm chuẩn do Hội đồng tuyển sinh quyết định."),
    Query("trung_tuyen_theo_phuong_thuc", "Số và tỷ lệ trúng tuyển đợt 1 toàn trường theo phương thức (100 điểm thi tốt nghiệp THPT, 200 học bạ, 301 tuyển thẳng, 402 ĐGNL/ĐGTD, 405 điểm thi kết hợp năng khiếu), kèm số đã xác nhận nhập học", """
        SELECT t.phuong_thuc, CASE t.phuong_thuc WHEN '100' THEN 'Điểm thi tốt nghiệp THPT' WHEN '200' THEN 'Học bạ THPT' WHEN '301' THEN 'Tuyển thẳng'
               WHEN '402' THEN 'Đánh giá năng lực, đánh giá tư duy' WHEN '405' THEN 'Điểm thi kết hợp năng khiếu' END AS ten_phuong_thuc,
               COUNT(*) AS trung_tuyen, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM trung_tuyen), 1) AS phan_tram_tong_trung_tuyen,
               COUNT(x.ma_ts) AS da_xac_nhan
        FROM trung_tuyen t LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts GROUP BY t.phuong_thuc ORDER BY t.phuong_thuc""",
          tong=("trung_tuyen", "da_xac_nhan")),
    Query("trung_tuyen_theo_nganh", "Số trúng tuyển đợt 1 theo ngành và phương thức (pt100 điểm thi, pt200 học bạ, pt301 tuyển thẳng, pt402 ĐGNL, pt405 năng khiếu), so với chỉ tiêu", f"""
        SELECT n.ma_xet_tuyen AS ma_nganh, n.ten_nganh, n.chi_tieu, COUNT(t.ma_ts) AS trung_tuyen,
               COALESCE(SUM(t.phuong_thuc = '100'), 0) AS pt100, COALESCE(SUM(t.phuong_thuc = '200'), 0) AS pt200,
               COALESCE(SUM(t.phuong_thuc = '301'), 0) AS pt301, COALESCE(SUM(t.phuong_thuc = '402'), 0) AS pt402,
               COALESCE(SUM(t.phuong_thuc = '405'), 0) AS pt405, ROUND(100.0 * COUNT(t.ma_ts) / n.chi_tieu, 1) AS phan_tram_chi_tieu
        FROM nganh n LEFT JOIN trung_tuyen t ON t.ma_xet_tuyen = n.ma_xet_tuyen
        WHERE {FILTER} GROUP BY n.ma_xet_tuyen ORDER BY phan_tram_chi_tieu""", (NGANH,),
          tong=("chi_tieu", "trung_tuyen", "pt100", "pt200", "pt301", "pt402", "pt405")),
    Query("xac_nhan_theo_nganh", "Xác nhận nhập học theo ngành: đã xác nhận, chưa xác nhận, chỉ tiêu chưa có người xác nhận", f"""
        SELECT n.ma_xet_tuyen AS ma_nganh, n.ten_nganh, n.chi_tieu, COUNT(t.ma_ts) AS trung_tuyen, COUNT(x.ma_ts) AS da_xac_nhan,
               COUNT(t.ma_ts) - COUNT(x.ma_ts) AS chua_xac_nhan,
               ROUND(100.0 * COUNT(x.ma_ts) / NULLIF(COUNT(t.ma_ts), 0), 1) AS phan_tram_da_xac_nhan,
               n.chi_tieu - COUNT(x.ma_ts) AS chi_tieu_chua_co_nguoi_xac_nhan,
               ROUND(100.0 * l.xac_nhan / NULLIF(l.trung_tuyen, 0), 1) AS phan_tram_xac_nhan_ca_dot_2025
        FROM nganh n LEFT JOIN trung_tuyen t ON t.ma_xet_tuyen = n.ma_xet_tuyen
        LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts
        LEFT JOIN lich_su l ON l.ma_xet_tuyen = n.ma_xet_tuyen AND l.nam = 2025
        WHERE {FILTER} GROUP BY n.ma_xet_tuyen ORDER BY chi_tieu_chua_co_nguoi_xac_nhan DESC""", (NGANH,),
          ghi_chu="Hạn xác nhận nhập học đợt 1: 17:00 ngày 21/08/2026; số còn tăng đến hạn.",
          tong=("chi_tieu", "trung_tuyen", "da_xac_nhan", "chua_xac_nhan", "chi_tieu_chua_co_nguoi_xac_nhan")),
    Query("xac_nhan_theo_ngay", "Số xác nhận nhập học từng ngày và lũy kế", f"""
        SELECT substr(x.thoi_diem, 1, 10) AS ngay, COUNT(*) AS xac_nhan_trong_ngay,
               SUM(COUNT(*)) OVER (ORDER BY substr(x.thoi_diem, 1, 10)) AS luy_ke
        FROM xac_nhan x JOIN trung_tuyen t ON t.ma_ts = x.ma_ts JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen
        WHERE {FILTER} GROUP BY ngay ORDER BY ngay""", (NGANH,),
          tong=("xac_nhan_trong_ngay",)),
    Query("danh_sach_chua_xac_nhan", "Danh sách thí sinh trúng tuyển đợt 1 chưa xác nhận nhập học", f"""
        SELECT t.ma_ts, s.ho_ten, s.sdt, n.ten_nganh, t.phuong_thuc, t.diem_xet, s.ma_can_bo_tu_van, s.can_bo_tu_van
        FROM trung_tuyen t JOIN thi_sinh s ON s.ma_ts = t.ma_ts JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen
        LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts
        WHERE x.ma_ts IS NULL AND {FILTER} ORDER BY n.ten_nganh, s.ma_can_bo_tu_van, t.diem_xet DESC""", (NGANH,),
          ca_nhan=True, group_by=("ten_nganh", "ma_can_bo_tu_van")),
    Query("doi_soat_trung_tuyen", "Rà soát danh sách trúng tuyển đợt 1: điểm xét dưới điểm chuẩn, ngành giáo viên mà không thường trú "
          "Nghệ An hoặc ở nguyện vọng thứ tự lớn hơn 5, trùng CCCD, không có nguyện vọng tương ứng", """
        SELECT t.ma_ts, s.ho_ten, n.ten_nganh, t.phuong_thuc, t.thu_tu_nv, t.diem_xet, 'Điểm xét dưới điểm chuẩn' AS loi
          FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
         WHERE (t.phuong_thuc IN ('100', '402') AND t.diem_xet < n.diem_chuan_100)
            OR (t.phuong_thuc = '200' AND t.diem_xet < n.diem_chuan_200) OR (t.phuong_thuc = '405' AND t.diem_xet < n.diem_chuan_405)
        UNION ALL
        SELECT t.ma_ts, s.ho_ten, n.ten_nganh, t.phuong_thuc, t.thu_tu_nv, t.diem_xet, 'Ngành giáo viên nhưng không thường trú Nghệ An'
          FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
         WHERE n.la_su_pham = 1 AND s.thuong_tru_nghe_an = 0
        UNION ALL
        SELECT t.ma_ts, s.ho_ten, n.ten_nganh, t.phuong_thuc, t.thu_tu_nv, t.diem_xet, 'Ngành giáo viên ở nguyện vọng thứ tự lớn hơn 5'
          FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
         WHERE n.la_su_pham = 1 AND t.thu_tu_nv > 5
        UNION ALL
        SELECT t.ma_ts, s.ho_ten, n.ten_nganh, t.phuong_thuc, t.thu_tu_nv, t.diem_xet, 'Trùng CCCD với thí sinh trúng tuyển khác'
          FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
         WHERE s.cccd IN (SELECT s2.cccd FROM trung_tuyen t2 JOIN thi_sinh s2 ON s2.ma_ts = t2.ma_ts GROUP BY s2.cccd HAVING COUNT(*) > 1)
        UNION ALL
        SELECT t.ma_ts, s.ho_ten, n.ten_nganh, t.phuong_thuc, t.thu_tu_nv, t.diem_xet, 'Không có nguyện vọng tương ứng'
          FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
         WHERE NOT EXISTS (SELECT 1 FROM nguyen_vong v WHERE v.ma_ts = t.ma_ts AND v.ma_xet_tuyen = t.ma_xet_tuyen AND v.phuong_thuc = t.phuong_thuc)
        ORDER BY loi, ten_nganh""", ca_nhan=True, group_by=("loi",),
          ghi_chu="Đã kiểm 5 quy tắc: điểm xét dưới điểm chuẩn; ngành giáo viên không thường trú Nghệ An; ngành giáo viên ở nguyện vọng thứ tự lớn hơn 5; trùng CCCD; không có nguyện vọng tương ứng. Quy tắc không có trong tong_hop là không phát hiện trường hợp nào."),
    Query("nhap_hoc_tong_hop", "Ngày nhập học 17/8: đã làm thủ tục, thiếu hồ sơ, học phí, đăng ký hỗ trợ theo NĐ 116", f"""
        SELECT n.ma_xet_tuyen AS ma_nganh, n.ten_nganh, COALESCE(SUM(x.thoi_diem <= '2026-08-17 17:00'), 0) AS da_xac_nhan_truoc_ngay_nhap_hoc,
               COUNT(h.ma_ts) AS da_lam_thu_tuc, COALESCE(SUM(h.trang_thai = 'Thiếu hồ sơ'), 0) AS thieu_ho_so,
               COALESCE(SUM(h.thieu = 'Bản chính minh chứng ưu tiên'), 0) AS thieu_minh_chung_uu_tien,
               COALESCE(SUM(h.da_nop_hoc_phi), 0) AS da_nop_hoc_phi, COALESCE(SUM(h.dang_ky_nd116), 0) AS dang_ky_nd116
        FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen
        LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts LEFT JOIN nhap_hoc h ON h.ma_ts = t.ma_ts
        WHERE {FILTER} GROUP BY n.ma_xet_tuyen ORDER BY n.ten_nganh""", (NGANH,),
          tong=("da_xac_nhan_truoc_ngay_nhap_hoc", "da_lam_thu_tuc", "thieu_ho_so", "thieu_minh_chung_uu_tien", "da_nop_hoc_phi", "dang_ky_nd116")),
    Query("xac_nhan_chua_nhap_hoc", "Danh sách đã xác nhận nhập học trước ngày 17/8 nhưng chưa làm thủ tục tại trường", f"""
        SELECT t.ma_ts, s.ho_ten, s.sdt, n.ten_nganh, x.thoi_diem AS thoi_diem_xac_nhan, s.ma_can_bo_tu_van, s.can_bo_tu_van
        FROM xac_nhan x JOIN trung_tuyen t ON t.ma_ts = x.ma_ts JOIN thi_sinh s ON s.ma_ts = t.ma_ts
        JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen LEFT JOIN nhap_hoc h ON h.ma_ts = t.ma_ts
        WHERE h.ma_ts IS NULL AND x.thoi_diem <= '2026-08-17 17:00' AND {FILTER} ORDER BY n.ten_nganh, s.ho_ten""", (NGANH,),
          ca_nhan=True, group_by=("ten_nganh",)),
    Query("ho_so_giay_tong_hop", "Hồ sơ giấy PT 402: theo kênh nộp, trạng thái và giấy tờ còn thiếu", """
        SELECT kenh_nop, trang_thai, NULLIF(thieu, '') AS giay_to_thieu, COUNT(*) AS so_ho_so
        FROM ho_so_giay GROUP BY kenh_nop, trang_thai, thieu ORDER BY kenh_nop, trang_thai""",
          tong=("so_ho_so",)),
    Query("ho_so_giay_can_xu_ly", "Danh sách hồ sơ giấy PT 402 thiếu giấy tờ hoặc trễ hạn", """
        SELECT h.ma_ho_so, s.ho_ten, s.sdt, h.kenh_nop, h.ngay_dau_buu_cuc, h.trang_thai, h.thieu
        FROM ho_so_giay h JOIN thi_sinh s ON s.ma_ts = h.ma_ts WHERE h.trang_thai <> 'Đủ' ORDER BY h.trang_thai, h.ma_ho_so""",
          ca_nhan=True, group_by=("trang_thai", "thieu")),
    Query("kenh_biet_den", "Kênh thí sinh biết đến Trường: số thí sinh, trúng tuyển, đã xác nhận", """
        SELECT s.kenh_biet_den, COUNT(DISTINCT s.ma_ts) AS so_thi_sinh,
               COUNT(DISTINCT CASE WHEN :ma_xet_tuyen IS NULL OR t.ma_xet_tuyen = :ma_xet_tuyen THEN t.ma_ts END) AS trung_tuyen,
               COUNT(DISTINCT CASE WHEN :ma_xet_tuyen IS NULL OR t.ma_xet_tuyen = :ma_xet_tuyen THEN x.ma_ts END) AS da_xac_nhan
        FROM thi_sinh s JOIN nguyen_vong v ON v.ma_ts = s.ma_ts
        LEFT JOIN trung_tuyen t ON t.ma_ts = s.ma_ts LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts
        WHERE (:ma_xet_tuyen IS NULL OR v.ma_xet_tuyen = :ma_xet_tuyen)
        GROUP BY s.kenh_biet_den ORDER BY so_thi_sinh DESC""", (NGANH,),
          tong=("so_thi_sinh", "trung_tuyen", "da_xac_nhan")),
    Query("truong_thpt", "Trường THPT có nhiều thí sinh: số thí sinh, trúng tuyển, đã xác nhận", """
        SELECT s.truong_thpt, s.tinh, s.dia_ban, COUNT(DISTINCT s.ma_ts) AS so_thi_sinh,
               COUNT(DISTINCT CASE WHEN :ma_xet_tuyen IS NULL OR t.ma_xet_tuyen = :ma_xet_tuyen THEN t.ma_ts END) AS trung_tuyen,
               COUNT(DISTINCT CASE WHEN :ma_xet_tuyen IS NULL OR t.ma_xet_tuyen = :ma_xet_tuyen THEN x.ma_ts END) AS da_xac_nhan
        FROM thi_sinh s JOIN nguyen_vong v ON v.ma_ts = s.ma_ts
        LEFT JOIN trung_tuyen t ON t.ma_ts = s.ma_ts LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts
        WHERE (:ma_xet_tuyen IS NULL OR v.ma_xet_tuyen = :ma_xet_tuyen)
        GROUP BY s.truong_thpt ORDER BY so_thi_sinh DESC LIMIT :top""",
          (NGANH, Param("top", "int", "số trường, mặc định 10", lo=1, hi=40, default=10))),
    Query("lich_su_tuyen_sinh", "Chỉ tiêu, nguyện vọng 1, trúng tuyển, xác nhận, nhập học các năm 2024–2026 theo ngành", f"""
        SELECT l.nam, n.ma_xet_tuyen AS ma_nganh, n.ten_nganh, l.chi_tieu, l.so_nv1, l.trung_tuyen, l.xac_nhan, l.nhap_hoc,
               ROUND(100.0 * l.nhap_hoc / l.chi_tieu, 1) AS phan_tram_nhap_hoc_tren_chi_tieu, l.ghi_chu
        FROM lich_su l JOIN nganh n ON n.ma_xet_tuyen = l.ma_xet_tuyen WHERE {FILTER}
        UNION ALL
        SELECT 2026, n.ma_xet_tuyen, n.ten_nganh, n.chi_tieu,
               (SELECT COUNT(*) FROM nguyen_vong v WHERE v.ma_xet_tuyen = n.ma_xet_tuyen AND v.thu_tu = 1),
               (SELECT COUNT(*) FROM trung_tuyen t WHERE t.ma_xet_tuyen = n.ma_xet_tuyen),
               (SELECT COUNT(*) FROM trung_tuyen t JOIN xac_nhan x ON x.ma_ts = t.ma_ts WHERE t.ma_xet_tuyen = n.ma_xet_tuyen),
               (SELECT COUNT(*) FROM trung_tuyen t JOIN nhap_hoc h ON h.ma_ts = t.ma_ts WHERE t.ma_xet_tuyen = n.ma_xet_tuyen),
               ROUND(100.0 * (SELECT COUNT(*) FROM trung_tuyen t JOIN nhap_hoc h ON h.ma_ts = t.ma_ts WHERE t.ma_xet_tuyen = n.ma_xet_tuyen) / n.chi_tieu, 1),
               'năm 2026: số đến thời điểm dữ liệu, đợt 1'
        FROM nganh n WHERE {FILTER}
        ORDER BY 3, 1""", (NGANH,)),
    Query("tu_van_tong_hop", "Lượt tư vấn theo kênh và chủ đề: số lượt, chưa trả lời, thời gian phản hồi trung bình", """
        SELECT kenh, chu_de, COUNT(*) AS so_luot, COALESCE(SUM(da_tra_loi = 0), 0) AS chua_tra_loi,
               ROUND(AVG(phut_phan_hoi), 0) AS phut_phan_hoi_trung_binh
        FROM tu_van WHERE (:thang IS NULL OR CAST(substr(thoi_diem, 6, 2) AS INTEGER) = :thang)
        GROUP BY kenh, chu_de ORDER BY so_luot DESC""", (Param("thang", "int", "tháng 3–8 năm 2026; bỏ trống là cả mùa", lo=1, hi=12),),
          tong=("so_luot", "chua_tra_loi")),
]
