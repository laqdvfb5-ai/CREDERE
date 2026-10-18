"""Đo tốc độ thật trên các câu mẫu và so với bản ghi phát lại cũ (gọi model thật, có tính phí).

    python scripts/bench_speed.py [--pick hieu_truong:all,dao_tao:1-2,tuyen_sinh:1-2] [--extra "hieu_truong:Hôm nay tao mệt quá"]
                                  [--max-usd 2.5] [--out thư_mục]

Chạy qua cùng đường /api/ask như trang web, nhưng bản ghi mới lưu vào thư mục đo riêng: không ghi đè bản phát lại của buổi demo.
Dừng khi tổng chi phí chạm --max-usd. In bảng thời gian, số lời gọi, chi phí mới so với cũ; ghi report.json có cả hai câu trả lời
để đọc so chất lượng.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient  # noqa: E402

from app.apps import build_apps  # noqa: E402
from app.config import RUNS_DIR  # noqa: E402
from app.domains import tuyen_sinh  # noqa: E402
from app.web import create_app, question_key  # noqa: E402

DEMO_DIR = RUNS_DIR / "demo-tuyen-sinh"
VND_PER_USD = 27_000


def old_record(app_key: str, q: str) -> dict | None:
    path = DEMO_DIR / f"{'' if app_key == tuyen_sinh.KEY else app_key + '--'}{question_key(q)}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def wall_s(rec: dict) -> float | None:
    """Thời gian người dùng chờ: mốc của sự kiện cuối cùng trong bản ghi."""
    events = rec.get("events") or []
    return events[-1]["t"] if events else None


def summary(rec: dict) -> dict:
    ledger = rec.get("ledger") or []
    return {"wall_s": wall_s(rec), "calls": len(ledger), "cost_usd": round(sum(c.get("cost_usd") or 0 for c in ledger), 4),
            "output_tokens": sum(c.get("output_tokens") or 0 for c in ledger), "report": (rec.get("done") or {}).get("report", "")}


def picked(spec: str, apps: dict) -> list[tuple[str, str]]:
    out = []
    for part in filter(None, spec.split(",")):
        key, _, sel = part.partition(":")
        qs = [s["q"] for s in apps[key].samples]
        if sel in ("", "all"):
            idx = range(1, len(qs) + 1)
        else:
            lo, _, hi = sel.partition("-")
            idx = range(int(lo), int(hi or lo) + 1)
        out += [(key, qs[i - 1]) for i in idx if i <= len(qs)]
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", default="hieu_truong:all,dao_tao:1-2,tuyen_sinh:1-2")
    ap.add_argument("--extra", action="append", default=[], help="app:câu hỏi thêm ngoài câu mẫu")
    ap.add_argument("--max-usd", type=float, default=2.5)
    ap.add_argument("--out", default=str(RUNS_DIR / f"bench_{datetime.now():%Y%m%d-%H%M}"))
    args = ap.parse_args()
    out = Path(args.out)
    (out / "replays").mkdir(parents=True, exist_ok=True)
    apps = build_apps()
    todo = picked(args.pick, apps) + [tuple(x.split(":", 1)) for x in args.extra]
    client = TestClient(create_app(apps=apps, replay_dir=out / "replays"))
    rows, spent = [], 0.0
    for n, (key, q) in enumerate(todo, 1):
        if spent >= args.max_usd:
            print(f"Dừng: đã chi ${spent:.2f}, chạm trần ${args.max_usd}.")
            break
        t0 = time.time()
        body = client.get("/api/ask", params={"q": q, "app": key}).text
        elapsed = round(time.time() - t0, 1)
        done = json.loads(body.split("event: done\ndata: ", 1)[1].split("\n\n")[0]) if "event: done" in body else {}
        new_path = out / "replays" / f"{'' if key == tuyen_sinh.KEY else key + '--'}{question_key(q)}.json"
        new = summary(json.loads(new_path.read_text(encoding="utf-8"))) if new_path.exists() else {
            "wall_s": elapsed, "calls": 0, "cost_usd": 0.0, "output_tokens": 0, "report": done.get("report", "")}
        old_rec = old_record(key, q)
        old = summary(old_rec) if old_rec else None
        spent += new["cost_usd"]
        rows.append({"app": key, "question": q, "new": new, "old": old, "status": done.get("status"), "replayed": done.get("replayed")})
        o = f"{old['wall_s']:.0f}s/{old['calls']} gọi/${old['cost_usd']:.3f}" if old and old["wall_s"] else "chưa có"
        print(f"{n:2}. [{key}] {q[:70]}\n    MỚI {new['wall_s']:.0f}s/{new['calls']} gọi/${new['cost_usd']:.3f}   CŨ {o}"
              f"   trạng thái {done.get('status')}  phát lại: {done.get('replayed')}")
        (out / "report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    pairs = [r for r in rows if r["old"] and r["old"]["wall_s"] and r["new"]["calls"]]
    if pairs:
        by_app = {}
        for r in pairs:
            by_app.setdefault(r["app"], []).append(r)
        print("\nTrung bình theo AI (chỉ các câu có cả bản cũ và bản mới):")
        for key, rs in by_app.items():
            nw = sum(r["new"]["wall_s"] for r in rs) / len(rs)
            ow = sum(r["old"]["wall_s"] for r in rs) / len(rs)
            nc = sum(r["new"]["cost_usd"] for r in rs) / len(rs)
            oc = sum(r["old"]["cost_usd"] for r in rs) / len(rs)
            print(f"  {key}: {ow:.0f}s → {nw:.0f}s ({(nw - ow) / ow:+.0%}); ${oc:.3f} → ${nc:.3f} mỗi lượt; {len(rs)} câu")
    print(f"\nTổng chi: ${spent:.3f} ≈ {spent * VND_PER_USD:,.0f} đồng. Bản ghi và report.json: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
