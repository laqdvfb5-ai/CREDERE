"""Chạy một yêu cầu qua cổng API và lưu hồ sơ lượt chạy ra ngoài OneDrive.

    python -m app.cli "Yêu cầu..." [--sources nguon.json] [--search openalex|none] [--config A|C] [--workers tuyen_sinh,analysis]

Mỗi lượt chạy có một thư mục trong ~/.credere/runs: events.jsonl ghi dần từng sự kiện (kế hoạch được ghi trước khi
tác tử thực thi chạy), record.json ghi khi kết thúc, kể cả khi lượt chạy lỗi. Khóa bí mật được che trước khi ghi.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .config import CONFIGS, RUNS_DIR, Limits, load_env, redact
from .graph import run
from .llm import GatewayClient
from .sources import load_sources
from .tools.search import OpenAlexSearch


def show(e: dict) -> None:
    kind, d = e["event_type"], e["detail"]
    if kind == "plan_saved":
        print("KẾ HOẠCH:")
        for t in d["tasks"]:
            deps = f" (sau {', '.join(t['depends_on'])})" if t["depends_on"] else ""
            print(f"  {t['task_id']} [{t['worker_type']}/{t['task_type']}] {t['goal']}{deps}")
    elif kind == "plan_rejected":
        print("KẾ HOẠCH BỊ TỪ CHỐI: " + "; ".join(d["errors"]))
    elif kind == "task_reviewed":
        print(f"  {e['task_id']} lần {d['attempt']}: {d['next']}" + (f" ({d['feedback']})" if d["feedback"] and d["next"] != "accepted" else ""))
    elif kind in ("task_blocked", "budget_exceeded", "wave_trimmed", "report_failed"):
        print(f"  {kind}: {e['task_id'] or ''} {json.dumps(d, ensure_ascii=False)}")


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Chạy tác tử điều phối Credere")
    ap.add_argument("request")
    ap.add_argument("--sources", help="tệp JSON: danh sách {source_id, title, text, access_scope}")
    ap.add_argument("--search", choices=["openalex", "none"], default="none")
    ap.add_argument("--config", choices=sorted(CONFIGS), default="A", help="A: cấu hình đã chốt; C: đối chứng, mọi vai trò dùng gpt-6-sol")
    ap.add_argument("--max-llm-calls", type=int, default=Limits().max_llm_calls)
    ap.add_argument("--workers", help="chỉ dùng các tác tử này, cách nhau bằng dấu phẩy, ví dụ tuyen_sinh,analysis")
    args = ap.parse_args(argv)

    onedrive = os.environ.get("OneDrive")
    if onedrive and RUNS_DIR.resolve().is_relative_to(Path(onedrive).resolve()):
        print(f"Thư mục hồ sơ {RUNS_DIR} nằm trong OneDrive; đặt CREDERE_HOME ra ngoài OneDrive.", file=sys.stderr)
        return 2
    sources = load_sources(args.sources) if args.sources else []
    env = load_env()
    search = OpenAlexSearch(env.get("OPENALEX_API_KEY")) if args.search == "openalex" else None
    llm = GatewayClient(CONFIGS[args.config], env)

    out = RUNS_DIR / f"run-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:6]}"
    out.mkdir(parents=True)
    state, error = {}, None
    try:
        with open(out / "events.jsonl", "a", encoding="utf-8") as events:
            def on_event(e: dict) -> None:
                events.write(redact(json.dumps(e, ensure_ascii=False), env) + "\n")
                events.flush()
                show(e)
            workers = set(args.workers.split(",")) if args.workers else None
            state = run(args.request, llm, sources, search, Limits(max_llm_calls=args.max_llm_calls), on_event, workers)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        raise
    finally:
        record = {k: state.get(k) for k in ("request", "plan", "plan_errors", "status", "results", "reviews", "history", "events", "report", "usage")}
        record.update(request=args.request, config=args.config, models=CONFIGS[args.config].__dict__, error=error,
                      ledger=[c.__dict__ for c in llm.ledger.calls], usage=state.get("usage") or llm.ledger.totals())
        (out / "record.json").write_text(redact(json.dumps(record, ensure_ascii=False, indent=1), env), encoding="utf-8")

    print("\n" + redact(state.get("report", ""), env))
    u = state["usage"]
    print(f"\n--- {u['calls']} lời gọi, {u['input_tokens']} token vào, {u['output_tokens']} token ra, ${u['cost_usd']:.4f}. "
          f"Trạng thái: {state.get('status')}. Hồ sơ: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
