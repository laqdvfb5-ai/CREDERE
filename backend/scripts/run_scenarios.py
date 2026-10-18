"""Chạy các tình huống kiểm thử theo vai người dùng (ví dụ cán bộ Trung tâm Tuyển sinh) qua đúng luồng của trang demo.

    python scripts/run_scenarios.py [--file <kho>/04_danh-gia/tuyen-sinh/kich-ban-can-bo.json] [--only CB-01,CB-05] [--parallel 3]

Mỗi tình huống có câu hỏi, danh sách "cần có" và "không được" để người chấm đọc tay. Kết quả ghi thành báo cáo Markdown
trong <kho>/06_ket-qua/tuyen-sinh/, kèm tên hồ sơ lượt chạy của từng câu.
"""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient  # noqa: E402

from app.config import DATA_ROOT  # noqa: E402
from app.sources import load_sources  # noqa: E402
from app.web import DEFAULT_SOURCES, create_app  # noqa: E402

VND_PER_USD = 26_180


def ask(app, q: str) -> dict:
    t0 = time.time()
    body = TestClient(app).get("/api/ask", params={"q": q}).text
    events = [json.loads(b.split("data: ", 1)[1]) for b in body.split("\n\n") if b.startswith("event: event")]
    done = json.loads(body.split("event: done\ndata: ", 1)[1].split("\n\n")[0])
    return {"events": events, "done": done, "seconds": round(time.time() - t0)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(DATA_ROOT / "04_danh-gia" / "tuyen-sinh" / "kich-ban-can-bo.json"))
    ap.add_argument("--only")
    ap.add_argument("--parallel", type=int, default=3)
    args = ap.parse_args()
    items = json.loads(Path(args.file).read_text(encoding="utf-8"))
    if args.only:
        items = [i for i in items if i["id"] in args.only.split(",")]
    app = create_app(load_sources(DEFAULT_SOURCES))
    with ThreadPoolExecutor(args.parallel) as ex:
        results = list(ex.map(lambda i: ask(app, i["question"]), items))

    out_dir = DATA_ROOT / "06_ket-qua" / "tuyen-sinh"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = f"{datetime.now():%Y%m%d-%H%M}"
    (out_dir / f"kich-ban-{stamp}.json").write_text(json.dumps([{**i, **r} for i, r in zip(items, results)], ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    lines = [f"# Kiểm thử theo vai: {Path(args.file).stem}", "", f"Chạy lúc {datetime.now():%d/%m/%Y %H:%M}, {len(items)} tình huống.", ""]
    total = 0.0
    for item, r in zip(items, results):
        u = r["done"].get("usage") or {}
        total += u.get("cost_usd", 0)
        plan = next((e["detail"]["tasks"] for e in r["events"] if e["event_type"] == "plan_saved"), [])
        revisions = sum(1 for e in r["events"] if e["event_type"] == "task_reviewed" and e["detail"]["next"] == "revise")
        lines += [f"## {item['id']}. {item['loai']}", "", f"*{item['tinh_huong']}*", "", f"**Hỏi:** {item['question']}", "",
                  f"**Kế hoạch:** " + "; ".join(f"{t['task_id']} {t['worker_type']}: {t['goal']}" for t in plan), "",
                  f"**Trả lời** ({r['seconds']} giây, {u.get('calls', '?')} lượt gọi AI, {revisions} lần yêu cầu sửa, "
                  f"khoảng {u.get('cost_usd', 0) * VND_PER_USD:,.0f} đồng; hồ sơ lượt chạy: {r['done'].get('record', '—')}):", "",
                  "> " + (r["done"].get("report") or "").replace("\n", "\n> "), "",
                  "**Cần có:** " + "; ".join(item["can_co"]), "",
                  "**Không được:** " + ("; ".join(item["khong_duoc"]) or "—"), "", "**Chấm:** …", ""]
    lines.insert(3, f"Tổng chi phí khoảng {total * VND_PER_USD:,.0f} đồng.")
    report = out_dir / f"kich-ban-{stamp}.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Báo cáo: {report}")
    for item, r in zip(items, results):
        u = r["done"].get("usage") or {}
        print(f"\n===== {item['id']} {item['loai']} ({r['seconds']} s, {u.get('cost_usd', 0) * VND_PER_USD:,.0f} đồng)\n{r['done'].get('report')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
