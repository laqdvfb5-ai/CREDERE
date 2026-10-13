"""Chạy thật các câu hỏi mẫu của một AI qua trang demo (không cần mở trình duyệt), lưu bản ghi để phát lại khi trình bày.

    python scripts/record_demo.py [--app tuyen_sinh|dao_tao|hieu_truong] [--only 1,3] [--no-data]

In kế hoạch, trạng thái nghiệm thu, câu trả lời, số lời gọi, thời gian và chi phí của từng câu.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient  # noqa: E402

from app.apps import build_apps  # noqa: E402
from app.web import create_app  # noqa: E402

VND_PER_USD = 26_180


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default="tuyen_sinh")
    ap.add_argument("--only", help="số thứ tự câu hỏi (bắt đầu từ 1), cách nhau bằng dấu phẩy")
    ap.add_argument("--no-data", action="store_true", help="chỉ dùng văn bản công khai (giai đoạn 1)")
    args = ap.parse_args()
    apps = build_apps(with_data=not args.no_data)
    if args.app not in apps:
        print(f"Không có AI {args.app}; hiện có: {', '.join(apps)}")
        return 1
    questions = [s["q"] for s in apps[args.app].samples]  # như các nút trên trang
    picked = [int(i) for i in args.only.split(",")] if args.only else range(1, len(questions) + 1)
    client = TestClient(create_app(apps=apps))
    for i in picked:
        q = questions[i - 1]
        t0 = time.time()
        body = client.get("/api/ask", params={"q": q, "app": args.app}).text
        events = [json.loads(b.split("data: ", 1)[1]) for b in body.split("\n\n") if b.startswith("event: event")]
        done = json.loads(body.split("event: done\ndata: ", 1)[1].split("\n\n")[0])
        print(f"\n===== {i}. {q}  ({time.time() - t0:.0f} s)")
        for e in events:
            pad = "  "
            while e["event_type"] == "sub_event":  # bước bên trong AI con: thụt vào, ghi tên AI con
                pad += f"{e['detail']['ten']} › "
                e = e["detail"]["event"]
            d = e["detail"]
            if e["event_type"] == "plan_saved":
                for t in d["tasks"]:
                    print(f"{pad}KẾ HOẠCH {t['task_id']} [{t['worker_type']}] {t['goal']} refs={t['context']['refs']} sau={t['depends_on']}")
            elif e["event_type"] == "task_reviewed":
                print(f"{pad}NGHIỆM THU {e['task_id']} lần {d['attempt']}: {d['next']} {d['feedback'] or ''} {d['required_changes'] or ''}")
            elif e["event_type"] == "data_table":
                print(f"{pad}DANH SÁCH (chỉ tới màn hình): {d['title']}: {d['total']} dòng")
            elif e["event_type"] in ("plan_rejected", "task_blocked", "budget_exceeded", "report_checked", "report_failed"):
                print(f"{pad}{e['event_type']}: {json.dumps(d, ensure_ascii=False)[:300]}")
        u = done.get("usage") or {}
        print("  TRẢ LỜI:\n    " + (done.get("report") or "").replace("\n", "\n    "))
        if u:
            print(f"  {u['calls']} lời gọi, {u['input_tokens']:,} token vào, {u['output_tokens']:,} token ra, "
                  f"${u['cost_usd']:.4f} ≈ {u['cost_usd'] * VND_PER_USD:,.0f} đồng, phát lại: {done.get('replayed')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
