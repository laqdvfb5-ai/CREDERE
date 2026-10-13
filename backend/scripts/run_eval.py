"""Chạy bộ câu hỏi đánh giá AI Tuyển sinh qua model thật và chấm tự động.

    python scripts/run_eval.py [--set <kho>/04_danh-gia/tuyen-sinh/poc-30.jsonl] [--only TS-Q01,TS-Q05] [--parallel 3]

Chấm từng câu: có đủ số liệu đúng (gold_numbers), có dẫn ít nhất một nguồn đúng (source_ids), không nêu số bị cấm
(forbidden_numbers), câu thiếu nguồn phải từ chối. Bộ chấm dựa trên quy tắc nên vẫn phải đọc tay các câu trượt
và một mẫu câu đạt trước khi báo cáo con số.
"""
import argparse
import json
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import CONFIGS, DATA_ROOT, Limits, load_env  # noqa: E402
from app.graph import run  # noqa: E402
from app.llm import GatewayClient  # noqa: E402
from app.retrieval import fold  # noqa: E402
from app.sources import load_sources  # noqa: E402
from app.web import PLAN_HINT, SYNTH_HINT, WORKERS  # noqa: E402

VND_PER_USD = 26_180
SCALE = {"nghìn": 1e3, "ngàn": 1e3, "triệu": 1e6, "tỷ": 1e9}
NUMBER = re.compile(r"(?<![\w.,-])(\d[\d.,]*\d|\d)(?:\s*(nghìn|ngàn|triệu|tỷ))?", re.I)
NOT_VALUES = re.compile(r"\[[^\]]*\]|(?i:(?:điều|khoản|mục|phụ lục)\s+\d+)")  # trích dẫn, số điều khoản không phải số liệu
REFUSE = re.compile(r"chưa (có|đủ|xác định)|không (có|tìm thấy|nêu|đề cập|được nêu|có thông tin|có dữ liệu|đủ căn cứ)|chưa được công bố|"
                    r"chưa công bố|liên hệ|hotline|0975", re.I)


def parse_number(text: str) -> float | None:
    """'41.925.000' -> 41925000; '18,85' -> 18.85; '18.85' -> 18.85; '1,5' -> 1.5."""
    t = text.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", t):
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", t):
        t = t.replace(",", "")
    else:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def numbers_in(answer: str) -> list[tuple[float, bool]]:
    """Mọi số trong câu trả lời; cờ True nghĩa là số viết gọn theo đơn vị (41,9 triệu) nên chỉ so gần đúng."""
    out = []
    for m in NUMBER.finditer(NOT_VALUES.sub(" ", answer)):
        value = parse_number(m.group(1))
        if value is not None:
            scale = SCALE.get((m.group(2) or "").lower())
            out.append((value * scale, True) if scale else (value, False))
    return out


def has_number(answer: str, gold: str) -> bool:
    g = parse_number(gold)
    return g is not None and any(abs(v - g) <= (0.005 * abs(g) if approx else 1e-9) for v, approx in numbers_in(answer))


def has_value(answer: str, gold: str) -> bool:
    """Ngày d/m (chấp nhận 14/07, '14 tháng 7'), số điện thoại (bỏ dấu chấm, khoảng trắng) hoặc số liệu."""
    if "/" in gold:
        d, m = (int(x) for x in gold.split("/")[:2])
        return re.search(rf"(?<!\d)0?{d}\s*(?:/|tháng)\s*0?{m}(?!\d)", answer) is not None
    if re.fullmatch(r"0\d{8,10}", gold):
        return gold in re.sub(r"[\s.]", "", answer)
    return has_number(answer, gold)


def grade(item: dict, report: str) -> dict:
    cited = set(re.findall(r"TS-\d{3}", report))
    checks = {}
    if item["type"] == "thieu_nguon":
        checks["tu_choi"] = bool(REFUSE.search(report))
    else:
        checks["dan_nguon_dung"] = bool(cited & set(item.get("source_ids") or [])) if item.get("source_ids") else bool(cited)
    if item.get("gold_numbers"):
        checks["dung_so_lieu"] = all(has_value(report, g) for g in item["gold_numbers"])
    if item.get("must_include"):  # câu tư vấn: phải nêu đủ các ngành; ngành không được gợi ý thì đọc tay
        folded = fold(report)
        checks["du_nganh"] = all(any(fold(alias) in folded for alias in name.split("|")) for name in item["must_include"])
    checks["khong_so_sai"] = not any(has_value(report, f) for f in item.get("forbidden_numbers") or [])
    return checks


def run_one(item: dict, sources, env) -> dict:
    llm = GatewayClient(CONFIGS["A"], env)
    t0 = time.time()
    try:
        state = run(item["question"], llm, sources, None, Limits(max_llm_calls=24), None, WORKERS, SYNTH_HINT, PLAN_HINT)  # như trang demo
        report, error = state.get("report", ""), None
    except Exception as e:  # lỗi ngoài dự kiến: ghi lại, không chấm là trượt về nội dung
        state, report, error = {}, "", f"{type(e).__name__}: {e}"[:300]
    gateway_error = error or next((x for x in state.get("plan_errors") or [] if "Lỗi gọi model" in x), None)
    checks = {} if gateway_error else grade(item, report)
    usage = llm.ledger.totals()
    return {**item, "report": report, "checks": checks, "passed": bool(checks) and all(checks.values()), "gateway_error": gateway_error,
            "status": state.get("status"), "usage": usage, "seconds": round(time.time() - t0, 1),
            "history": state.get("history")}  # từng lần thử và lý do nghiệm thu, để đọc lại câu trượt


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(DATA_ROOT / "04_danh-gia" / "tuyen-sinh" / "poc-30.jsonl"))
    ap.add_argument("--sources", default=str(DATA_ROOT / "03_xu-ly" / "tuyen_sinh" / "sources.json"))
    ap.add_argument("--only")
    ap.add_argument("--parallel", type=int, default=3)
    args = ap.parse_args()
    items = [json.loads(line) for line in Path(args.set).read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.only:
        items = [i for i in items if i["id"] in args.only.split(",")]
    sources, env = load_sources(args.sources), load_env()
    with ThreadPoolExecutor(args.parallel) as ex:
        rows = list(ex.map(lambda i: run_one(i, sources, env), items))

    out_dir = DATA_ROOT / "06_ket-qua" / "tuyen-sinh"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"eval-{datetime.now():%Y%m%d-%H%M}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    graded = [r for r in rows if r["checks"]]
    print(f"{len(rows)} câu, {len(graded)} chấm được, {len(rows) - len(graded)} lỗi cổng. Kết quả: {out}")
    if graded:
        print(f"ĐẠT: {sum(r['passed'] for r in graded)}/{len(graded)}")
        for t in sorted({r['type'] for r in graded}):
            rs = [r for r in graded if r["type"] == t]
            print(f"  {t}: {sum(r['passed'] for r in rs)}/{len(rs)}")
        costs = [r["usage"]["cost_usd"] for r in graded]
        secs = [r["seconds"] for r in graded]
        print(f"Chi phí trung bình ${statistics.mean(costs):.4f} ≈ {statistics.mean(costs) * VND_PER_USD:,.0f} đồng/câu "
              f"(cao nhất {max(costs) * VND_PER_USD:,.0f} đồng); thời gian trung vị {statistics.median(secs):.0f} s, cao nhất {max(secs):.0f} s")
    for r in rows:
        if not r["passed"]:
            print(f"\n--- {r['id']} [{r['type']}] {r['question']}\n    ĐÁP ÁN: {r['gold_answer']}\n    CHẤM: {r['checks']} {r['gateway_error'] or ''}"
                  f"\n    TRẢ LỜI: {r['report'][:700]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
