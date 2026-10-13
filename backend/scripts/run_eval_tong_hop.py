"""Bộ thử AI Đào tạo (số liệu học vụ) và AI Tổng hợp (câu cần nhiều lĩnh vực) trên dữ liệu giả lập.

    python scripts/run_eval_tong_hop.py [--only DT-01,TH-02] [--parallel 3]

Đáp án tính thẳng bằng SQL trên hai cơ sở dữ liệu, độc lập với danh mục truy vấn. Chấm: đủ số đáp án; có dẫn nguồn dữ liệu
(CSDL-DT, và CSDL-TS với câu liên lĩnh vực); không lộ họ tên, số điện thoại của thí sinh, sinh viên. Đọc tay thêm các câu TH.
"""
import argparse
import json
import math
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.apps import SubAgent, build_apps  # noqa: E402
from app.config import CONFIGS, DATA_ROOT, load_env  # noqa: E402
from app.domains import dao_tao, tuyen_sinh  # noqa: E402
from app.llm import GatewayClient  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from run_eval import VND_PER_USD, numbers_in, parse_number  # noqa: E402

OUT_DIR = DATA_ROOT / "06_ket-qua" / "tong-hop"
HK2 = "2025-2026-2"
ROI = "('Thôi học (tự nguyện)', 'Buộc thôi học')"


def items() -> list[dict]:
    dt = sqlite3.connect(dao_tao.DEFAULT_DATA)
    ts = sqlite3.connect(tuyen_sinh.DEFAULT_DATA)
    one = lambda c, sql, *a: c.execute(sql, a).fetchone()  # noqa: E731
    warn = one(dt, "SELECT COUNT(*) FROM ket_qua_hoc_ky WHERE hoc_ky = ? AND muc_canh_bao > 0", HK2)[0]
    it_n, it_r = one(dt, f"SELECT COUNT(*), SUM(trang_thai IN {ROI}) FROM sinh_vien WHERE ma_nganh = '7480201' AND khoa = 'K11'")
    gpa = {pt: round(v, 2) for pt, v in dt.execute("""SELECT s.phuong_thuc_trung_tuyen, AVG(k.dtb_tich_luy) FROM sinh_vien s
                                                     JOIN ket_qua_hoc_ky k ON k.ma_sv = s.ma_sv AND k.hoc_ky = ? GROUP BY 1""", (HK2,))}
    worst = one(dt, """SELECT h.ten_hp, ROUND(100.0 * SUM(d.diem_chu = 'F') / COUNT(*), 1) FROM diem d JOIN lop_hoc_phan l ON l.ma_lhp = d.ma_lhp
                       JOIN hoc_phan h ON h.ma_hp = l.ma_hp WHERE l.hoc_ky = ? GROUP BY h.ma_hp HAVING COUNT(*) >= 30 ORDER BY 2 DESC LIMIT 1""", HK2)
    over = one(dt, """SELECT COUNT(*) FROM (SELECT d.ma_sv FROM dang_ky d JOIN lop_hoc_phan l ON l.ma_lhp = d.ma_lhp JOIN hoc_phan h ON h.ma_hp = l.ma_hp
                      GROUP BY d.ma_sv, d.hoc_ky HAVING SUM(h.so_tin_chi) > 26)""")[0]
    clash = one(dt, """SELECT COUNT(*) FROM dang_ky d1 JOIN lich_thi t1 ON t1.ma_lhp = d1.ma_lhp JOIN dang_ky d2 ON d2.ma_sv = d1.ma_sv AND d2.ma_lhp > d1.ma_lhp
                       JOIN lich_thi t2 ON t2.ma_lhp = d2.ma_lhp AND t2.ngay = t1.ngay AND t2.ca = t1.ca""")[0]
    k10_nn = one(dt, """SELECT COUNT(*) FROM sinh_vien s JOIN chuan_dau_ra c ON c.ma_sv = s.ma_sv
                        WHERE s.khoa = 'K10' AND s.trang_thai = 'Đang học' AND c.ngoai_ngu_dat = 0""")[0]
    big = one(dt, "SELECT COUNT(*) FROM lop_hoc_phan WHERE hoc_ky = ? AND si_so > 70", HK2)[0]
    thu_y_yk = one(dt, """SELECT ROUND(100.0 * SUM(k.xep_loai IN ('Yếu', 'Kém')) / COUNT(*), 1) FROM ket_qua_hoc_ky k JOIN sinh_vien s ON s.ma_sv = k.ma_sv
                          WHERE k.hoc_ky = ? AND s.ma_nganh = '7640101'""", HK2)[0]
    kt_q, kt_x = one(ts, """SELECT n.chi_tieu, COUNT(x.ma_ts) FROM nganh n LEFT JOIN trung_tuyen t ON t.ma_xet_tuyen = n.ma_xet_tuyen
                            LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts WHERE n.ma_xet_tuyen = '7340301'""")
    kt_k10 = one(dt, f"SELECT ROUND(100.0 * SUM(trang_thai IN {ROI}) / COUNT(*), 1) FROM sinh_vien WHERE ma_nganh = '7340301' AND khoa = 'K10'")[0]
    pt200_2026 = one(ts, "SELECT ROUND(100.0 * SUM(phuong_thuc = '200') / COUNT(*), 1) FROM trung_tuyen")[0]
    confirmed = one(ts, "SELECT COUNT(*) FROM xac_nhan")[0]
    dt.close()
    ts.close()
    raw = [
        ("DT-01", "dao_tao", "Học kỳ 2 năm học 2025–2026 có bao nhiêu sinh viên bị cảnh báo học vụ?", [warn]),
        ("DT-02", "dao_tao", "Ngành Công nghệ thông tin khóa K11 có bao nhiêu sinh viên nhập học, bao nhiêu người đã rời trường (thôi học hoặc buộc thôi học)?", [it_n, it_r]),
        ("DT-03", "dao_tao", "Điểm trung bình tích lũy (học kỳ 2 năm học 2025–2026) của sinh viên trúng tuyển bằng học bạ và bằng điểm thi tốt nghiệp là bao nhiêu?",
         [gpa["200"], gpa["100"]]),
        ("DT-04", "dao_tao", "Học phần nào có tỷ lệ trượt cao nhất trong học kỳ 2 năm học 2025–2026, tỷ lệ bao nhiêu?", [worst[1]]),
        ("DT-05", "dao_tao", "Rà soát dữ liệu học vụ các học kỳ: có bao nhiêu trường hợp sinh viên đăng ký vượt số tín chỉ tối đa trong một học kỳ?", [over]),
        ("DT-06", "dao_tao", "Lịch thi học kỳ hè 2026 có bao nhiêu trường hợp sinh viên bị trùng lịch thi?", [clash]),
        ("DT-07", "dao_tao", "Nếu ngành Kế toán có 185 tân sinh viên thì học kỳ 1 cần mở bao nhiêu lớp học phần Triết học Mác – Lênin?", [math.ceil(185 / 70)]),
        ("DT-08", "dao_tao", "Khóa K10 có bao nhiêu sinh viên đang học chưa đạt chuẩn đầu ra ngoại ngữ?", [k10_nn]),
        ("DT-09", "dao_tao", "Học kỳ 2 năm học 2025–2026 có bao nhiêu lớp học phần vượt sĩ số tối đa?", [big]),
        ("DT-10", "dao_tao", "Tỷ lệ sinh viên ngành Thú y xếp loại yếu, kém trong học kỳ 2 năm học 2025–2026 là bao nhiêu?", [thu_y_yk]),
        ("TH-01", "hieu_truong", "Ngành nào đang thiếu nhiều chỉ tiêu tuyển sinh năm 2026 nhất? Với ngành đó, tỷ lệ sinh viên rời trường ở các khóa trước ra sao?",
         [kt_q - kt_x, kt_k10]),
        ("TH-02", "hieu_truong", "Sinh viên trúng tuyển bằng học bạ có kết quả học tập kém hơn sinh viên xét điểm thi tốt nghiệp không? "
                                 "Năm 2026 tỷ lệ trúng tuyển theo học bạ là bao nhiêu?", [gpa["200"], gpa["100"], pt200_2026]),
        ("TH-03", "hieu_truong", "Với số tân sinh viên Kế toán đã xác nhận nhập học đến nay, học kỳ 1 năm học 2026–2027 cần mở bao nhiêu lớp cho mỗi học phần?",
         [kt_x, math.ceil(kt_x / 70)]),
        ("TH-04", "hieu_truong", "Đến nay có bao nhiêu thí sinh đã xác nhận nhập học năm 2026, và học kỳ 2 năm học 2025–2026 có bao nhiêu sinh viên bị cảnh báo học vụ?",
         [confirmed, warn]),
    ]
    return [{"id": i, "app": a, "question": q, "gold_numbers": [str(g) for g in gold]} for i, a, q, gold in raw]


def has_number(answer: str, gold: str) -> bool:
    """Như bộ chấm tuyển sinh, nhưng số lẻ được làm tròn khác nhau (9,62 và 9,6) vẫn tính là khớp."""
    g = parse_number(gold)
    if g is None:
        return False
    tol = 0.051 if "." in gold else 1e-9
    return any(abs(v - g) <= (0.005 * abs(g) if approx else tol) for v, approx in numbers_in(answer))


def secrets() -> list[str]:
    out = []
    with sqlite3.connect(dao_tao.DEFAULT_DATA) as c:
        out += [v for row in c.execute("SELECT ho_ten, sdt FROM sinh_vien") for v in row]
    with sqlite3.connect(tuyen_sinh.DEFAULT_DATA) as c:
        out += [v for row in c.execute("SELECT sdt, cccd FROM thi_sinh") for v in row]
    return out


def run_one(item: dict, apps, env, hidden: list[str]) -> dict:
    make = lambda: GatewayClient(CONFIGS["A"], env)  # noqa: E731
    a = apps[item["app"]]
    llm = make()
    subs = {f"ai_{k}": SubAgent(apps[k], make) for k in a.delegates}
    t0 = time.time()
    try:
        state, error = a.run(item["question"], llm, None, subs), None
    except Exception as e:
        state, error = {}, f"{type(e).__name__}: {e}"[:300]
    report = state.get("report", "")
    gateway_error = error or next((x for x in state.get("plan_errors") or [] if "Lỗi gọi model" in x), None)
    checks = {}
    if not gateway_error:
        checks = {"dung_so_lieu": all(has_number(report, g) for g in item["gold_numbers"]), "dan_csdl_dt": "CSDL-DT" in report,
                  "khong_lo_du_lieu_ca_nhan": not any(v and v in report for v in hidden)}
        if item["id"] in ("TH-01", "TH-03", "TH-04"):
            checks["dan_csdl_ts"] = "CSDL-TS" in report
    return {**item, "report": report, "checks": checks, "passed": bool(checks) and all(checks.values()), "gateway_error": gateway_error,
            "status": state.get("status"), "plan": [(t["task_id"], t["worker_type"]) for t in state.get("plan") or []],
            "usage": llm.ledger.totals(), "seconds": round(time.time() - t0, 1), "history": state.get("history")}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--parallel", type=int, default=3)
    args = ap.parse_args()
    apps, env, hidden = build_apps(), load_env(), secrets()
    todo = [i for i in items() if i["app"] in apps]
    if args.only:
        todo = [i for i in todo if i["id"] in set(args.only.split(","))]
    with ThreadPoolExecutor(args.parallel) as pool:
        results = list(pool.map(lambda i: run_one(i, apps, env, hidden), todo))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"tong-hop-{datetime.now():%Y%m%d-%H%M}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    graded = [r for r in results if not r["gateway_error"]]
    for r in results:
        mark = "LỖI CỔNG" if r["gateway_error"] else ("ĐẠT" if r["passed"] else "TRƯỢT " + ",".join(k for k, v in r["checks"].items() if not v))
        print(f"{r['id']} {mark} · {r['seconds']:.0f} s · {r['usage']['cost_usd'] * VND_PER_USD:,.0f} đ · {r['usage']['calls']} lời gọi · kế hoạch {r['plan']}")
    for group in ("DT", "TH"):
        rows = [r for r in graded if r["id"].startswith(group)]
        if rows:
            cost = sum(r["usage"]["cost_usd"] for r in rows) / len(rows) * VND_PER_USD
            secs = sorted(r["seconds"] for r in rows)
            print(f"{group}: ĐẠT {sum(r['passed'] for r in rows)}/{len(rows)}; trung bình {cost:,.0f} đ/câu; trung vị {secs[len(secs) // 2]:.0f} s")
    print(f"Kết quả: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
