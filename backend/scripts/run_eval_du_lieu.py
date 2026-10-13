"""Bộ thử câu hỏi số liệu (giai đoạn 2) trên cơ sở dữ liệu giả lập: đáp án tính thẳng bằng SQL, độc lập với danh mục truy vấn.

    python scripts/run_eval_du_lieu.py [--only DL-01,DL-05] [--parallel 3]

Chấm: câu trả lời có đủ số đáp án; có dẫn [CSDL-TS]; không lộ họ tên, số điện thoại, CCCD của thí sinh nào.
Câu DL-14 cần cả văn bản (điểm chuẩn) và số liệu, để thử việc phối hợp hai tác tử.
"""
import argparse
import json
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import CONFIGS, DATA_ROOT, Limits, load_env  # noqa: E402
from app.graph import run  # noqa: E402
from app.llm import GatewayClient  # noqa: E402
from app.sources import load_sources  # noqa: E402
from app.tools.data import DataStore  # noqa: E402
from app.web import open_store  # noqa: E402
from app.web import DEFAULT_DATA, DEFAULT_SOURCES, app_config  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from run_eval import VND_PER_USD, has_number  # noqa: E402

OUT_DIR = DATA_ROOT / "06_ket-qua" / "tuyen-sinh"


def one(conn, sql: str, *args):
    return conn.execute(sql, args).fetchone()


def items(db: Path) -> list[dict]:
    """Câu hỏi và đáp án; đáp án đọc từ cơ sở dữ liệu nên luôn khớp với bản giả lập hiện có."""
    c = sqlite3.connect(db)
    per_major = """SELECT n.ten_nganh, n.chi_tieu, COUNT(t.ma_ts), COUNT(x.ma_ts) FROM nganh n
                   LEFT JOIN trung_tuyen t ON t.ma_xet_tuyen = n.ma_xet_tuyen LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts
                   WHERE n.ma_xet_tuyen = ? GROUP BY n.ma_xet_tuyen"""
    _, _, thu_y_tt, thu_y_xn = one(c, per_major, "7640101")
    gap = sorted(((q - xn, name) for name, q, _, xn in
                  c.execute("""SELECT n.ten_nganh, n.chi_tieu, 0, COUNT(x.ma_ts) FROM nganh n LEFT JOIN trung_tuyen t ON t.ma_xet_tuyen = n.ma_xet_tuyen
                               LEFT JOIN xac_nhan x ON x.ma_ts = t.ma_ts GROUP BY n.ma_xet_tuyen""")), reverse=True)[0]
    v2, v3 = (one(c, "SELECT so_du_kien_trung_tuyen FROM loc_ao WHERE vong = ? AND ma_xet_tuyen = '7220201'", r)[0] for r in (2, 3))
    nv1_kt = one(c, "SELECT COUNT(*) FROM nguyen_vong WHERE ma_xet_tuyen = '7340301' AND thu_tu = 1")[0]
    nv1_kt_2025 = one(c, "SELECT so_nv1 FROM lich_su WHERE nam = 2025 AND ma_xet_tuyen = '7340301'")[0]
    kenh, kenh_n = one(c, """SELECT s.kenh_biet_den, COUNT(DISTINCT s.ma_ts) FROM thi_sinh s JOIN nguyen_vong v ON v.ma_ts = s.ma_ts
                            GROUP BY s.kenh_biet_den ORDER BY 2 DESC LIMIT 1""")
    chua_nh_cntt = one(c, """SELECT COUNT(*) FROM xac_nhan x JOIN trung_tuyen t ON t.ma_ts = x.ma_ts LEFT JOIN nhap_hoc h ON h.ma_ts = t.ma_ts
                            WHERE h.ma_ts IS NULL AND x.thoi_diem <= '2026-08-17 17:00' AND t.ma_xet_tuyen = '7480201'""")[0]
    thu_tuc, thieu = one(c, "SELECT COUNT(*), SUM(trang_thai = 'Thiếu hồ sơ') FROM nhap_hoc")
    kt_gap = one(c, per_major, "7340301")
    kt_gap = kt_gap[1] - kt_gap[3]
    # kịch bản: trúng tuyển Thú y nếu điểm chuẩn PT 100 là 14 (cùng quy tắc với truy vấn mô phỏng, viết lại độc lập)
    rows = c.execute("""SELECT v.ma_ts, v.ma_xet_tuyen, v.phuong_thuc, v.diem_xet, s.thuong_tru_nghe_an, n.la_su_pham,
                               n.diem_chuan_100, n.diem_chuan_200, n.diem_chuan_405
                        FROM nguyen_vong v JOIN thi_sinh s ON s.ma_ts = v.ma_ts JOIN nganh n ON n.ma_xet_tuyen = v.ma_xet_tuyen
                        WHERE v.ma_ts NOT IN (SELECT ma_ts FROM nguyen_vong WHERE trang_thai LIKE 'Trúng nguyện vọng cao hơn (trường khác)')
                        ORDER BY v.ma_ts, v.thu_tu""").fetchall()
    got = {}
    for ts, ma, pt, diem, tt, sp, c100, c200, c405 in rows:
        if ts in got or (sp and not tt):
            continue
        cut = 14 if (ma == "7640101" and pt == "100") else {"100": c100, "402": c100, "200": c200, "405": c405}.get(pt)
        if pt == "301" or (cut is not None and diem is not None and diem >= cut):
            got[ts] = ma
    thu_y_14 = sum(1 for m in got.values() if m == "7640101")
    out = [
        ("DL-01", "Đến giờ có bao nhiêu thí sinh đã xác nhận nhập học?", [one(c, "SELECT COUNT(*) FROM xac_nhan")[0]]),
        ("DL-02", "Ngành Thú y có bao nhiêu thí sinh trúng tuyển đợt 1, đã xác nhận nhập học bao nhiêu?", [thu_y_tt, thu_y_xn]),
        ("DL-03", "Ngành nào còn nhiều chỉ tiêu chưa có người xác nhận nhập học nhất, còn bao nhiêu?", [gap[0]]),
        ("DL-04", "Có bao nhiêu thí sinh đặt ngành Công nghệ thông tin là nguyện vọng 1?",
         [one(c, "SELECT COUNT(*) FROM nguyen_vong WHERE ma_xet_tuyen = '7480201' AND thu_tu = 1")[0]]),
        ("DL-05", "Sau lần lọc ảo thứ 3, số dự kiến trúng tuyển ngành Ngôn ngữ Anh là bao nhiêu, giảm bao nhiêu so với vòng 2?", [v3, v2 - v3]),
        ("DL-06", "Nếu điểm chuẩn ngành Thú y phương thức 100 là 14 thì dự kiến trúng tuyển bao nhiêu thí sinh?", [thu_y_14]),
        ("DL-07", "Có bao nhiêu hồ sơ giấy phương thức 402 bị trễ hạn?", [one(c, "SELECT COUNT(*) FROM ho_so_giay WHERE trang_thai = 'Trễ hạn'")[0]]),
        ("DL-08", "Thí sinh biết đến Trường qua kênh nào nhiều nhất, bao nhiêu thí sinh?", [kenh_n]),
        ("DL-09", "Rà soát danh sách trúng tuyển: có bao nhiêu trường hợp trúng tuyển ngành giáo viên nhưng không thường trú Nghệ An?",
         [one(c, """SELECT COUNT(*) FROM trung_tuyen t JOIN nganh n ON n.ma_xet_tuyen = t.ma_xet_tuyen JOIN thi_sinh s ON s.ma_ts = t.ma_ts
                    WHERE n.la_su_pham = 1 AND s.thuong_tru_nghe_an = 0""")[0]]),
        ("DL-10", "Lập danh sách thí sinh ngành Công nghệ thông tin đã xác nhận nhập học trước ngày 17/8 nhưng chưa làm thủ tục tại trường.", [chua_nh_cntt]),
        ("DL-11", "Ngày nhập học 17/8 có bao nhiêu tân sinh viên đã làm thủ tục, bao nhiêu người còn thiếu hồ sơ?", [thu_tuc, thieu]),
        ("DL-12", "Tháng 8 có bao nhiêu lượt tư vấn chưa được trả lời?",
         [one(c, "SELECT COUNT(*) FROM tu_van WHERE da_tra_loi = 0 AND substr(thoi_diem, 6, 2) = '08'")[0]]),
        ("DL-13", "So với năm 2025, số thí sinh đặt ngành Kế toán là nguyện vọng 1 tăng hay giảm bao nhiêu?", [abs(nv1_kt - nv1_kt_2025)]),
        ("DL-14", "Ngành Kế toán còn bao nhiêu chỉ tiêu chưa có người xác nhận nhập học, và điểm chuẩn đợt 1 theo phương thức 100 là bao nhiêu?",
         [kt_gap, 16]),
    ]
    c.close()
    return [{"id": i, "question": q, "gold_numbers": [str(g) for g in gold], "kenh_top": kenh if i == "DL-08" else None} for i, q, gold in out]


def personal_values(db: Path) -> list[str]:
    with sqlite3.connect(db) as c:
        return [v for row in c.execute("SELECT ho_ten, sdt, cccd FROM thi_sinh") for v in row]


def run_one(item: dict, sources, data: DataStore, env, secrets: list[str]) -> dict:
    llm = GatewayClient(CONFIGS["A"], env)
    workers, synth_hint, plan_hint = app_config(data)
    t0 = time.time()
    try:
        state = run(item["question"], llm, sources, None, Limits(max_llm_calls=24), None, workers, synth_hint, plan_hint, data)
        report, error = state.get("report", ""), None
    except Exception as e:
        state, report, error = {}, "", f"{type(e).__name__}: {e}"[:300]
    gateway_error = error or next((x for x in state.get("plan_errors") or [] if "Lỗi gọi model" in x), None)
    checks = {}  # việc dữ liệu cá nhân không vào prompt được kiểm ở kiểm thử tự động (sổ ghi lời gọi không giữ nội dung)
    if not gateway_error:
        checks = {"dung_so_lieu": all(has_number(report, g) for g in item["gold_numbers"]), "dan_csdl": "[CSDL" in report or "CSDL]" in report,
                  "khong_lo_du_lieu_ca_nhan": not any(v and v in report for v in secrets)}
        if item.get("kenh_top"):
            checks["dung_kenh"] = item["kenh_top"].split()[0].lower() in report.lower()
    return {**item, "report": report, "checks": checks, "passed": bool(checks) and all(checks.values()), "gateway_error": gateway_error,
            "status": state.get("status"), "plan": [(t["task_id"], t["worker_type"]) for t in state.get("plan") or []],
            "tables": [e["detail"]["total"] for e in state.get("events", []) if e["event_type"] == "data_table"],
            "usage": llm.ledger.totals(), "seconds": round(time.time() - t0, 1), "history": state.get("history")}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    ap.add_argument("--only")
    ap.add_argument("--parallel", type=int, default=3)
    args = ap.parse_args()
    data, sources, env = open_store(args.data), load_sources(DEFAULT_SOURCES), load_env()
    todo = items(data.path)
    if args.only:
        todo = [i for i in todo if i["id"] in set(args.only.split(","))]
    secrets = personal_values(data.path)
    with ThreadPoolExecutor(args.parallel) as pool:
        results = list(pool.map(lambda i: run_one(i, sources, data, env, secrets), todo))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"du-lieu-{datetime.now():%Y%m%d-%H%M}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    graded = [r for r in results if not r["gateway_error"]]
    for r in results:
        mark = "LỖI CỔNG" if r["gateway_error"] else ("ĐẠT" if r["passed"] else "TRƯỢT " + ",".join(k for k, v in r["checks"].items() if not v))
        print(f"{r['id']} {mark} · {r['seconds']:.0f} s · {r['usage']['cost_usd'] * VND_PER_USD:,.0f} đ · kế hoạch {r['plan']} · danh sách {r['tables']}")
    cost = sum(r["usage"]["cost_usd"] for r in results)
    print(f"ĐẠT {sum(r['passed'] for r in graded)}/{len(graded)} (lỗi cổng {len(results) - len(graded)}); "
          f"trung bình {cost / max(len(results), 1) * VND_PER_USD:,.0f} đ/câu; kết quả {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
