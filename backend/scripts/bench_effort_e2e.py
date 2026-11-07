"""Paid end-to-end effort comparison using the existing synthetic/public fixtures.

python scripts/bench_effort_e2e.py --parallel 3
All failures stay in the denominator. Costs are estimates, including usage returned
on HTTP failures where available; network failures have unknown billing.
Legacy answer checks only match numbers, not their semantic binding; manual review
is mandatory. Provider acceptance does not prove underlying model identity.
"""
import argparse
import json
import random
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from app import llm as llm_module
from app.apps import SubAgent, build_apps
from app.config import CONFIGS, DATA_ROOT, PRICES, RUNS_DIR, load_env, redact
from app.graph import cited_ids
from app.llm import GatewayClient, load_providers
from run_eval import grade
from run_eval_tong_hop import has_number, items, secrets

_LOCAL = threading.local()
_POST = llm_module._post


def instrumented_post(url, **kwargs):
    observer = getattr(_LOCAL, "observer", None)
    if observer is None:
        return _POST(url, **kwargs)
    start = time.perf_counter()
    payload = kwargs["json"]
    row = {"label": _LOCAL.label, "effort": payload.get("reasoning_effort"),
           "model": payload["model"], "prompt_chars": sum(len(str(m.get("content", ""))) for m in payload["messages"])}
    try:
        response = _POST(url, **kwargs)
        row["http_status"] = response.status_code
        try:
            body = response.json()
            row["usage"] = body.get("usage") or {}
            choice = (body.get("choices") or [{}])[0]
            row["finish_reason"] = choice.get("finish_reason")
            if response.status_code != 200:
                row["error"] = str(body.get("error", {}))[:300]
        except (ValueError, AttributeError, IndexError, TypeError):
            row["usage"] = {}
        return response
    except Exception as error:
        row["error"] = type(error).__name__
        raise
    finally:
        row["seconds"] = round(time.perf_counter() - start, 3)
        observer.append(row)


class MeasuredClient(GatewayClient):
    def __init__(self, attempts, deadline, **kwargs):
        super().__init__(**kwargs)
        self.attempts = attempts
        self.deadline = deadline

    def complete(self, role, messages, max_tokens=2000, label=""):
        if time.monotonic() > self.deadline:
            raise RuntimeError("Benchmark run deadline reached")
        _LOCAL.observer, _LOCAL.label = self.attempts, label
        try:
            return super().complete(role, messages, max_tokens, label)
        finally:
            _LOCAL.observer = None


def cases():
    out = items()
    selected = {"TS-Q11", "TS-Q13", "TS-Q18", "TS-Q20", "TS-Q24", "TS-Q28"}
    fixture = DATA_ROOT / "04_danh-gia/tuyen-sinh/poc-30.jsonl"
    out += [{**json.loads(line), "app": "tuyen_sinh"} for line in fixture.read_text(encoding="utf-8").splitlines()
            if json.loads(line)["id"] in selected]
    return out


def run_one(case, effort, apps, env, providers, hidden, folder, deadline_seconds):
    started = time.perf_counter()
    deadline = time.monotonic() + deadline_seconds
    attempts, clients, events = [], [], []
    def make():
        client = MeasuredClient(attempts, deadline, models=CONFIGS["A"], env=env,
                                providers=providers, timeout=90, reasoning_effort=effort)
        clients.append(client)
        return client
    client = make()
    app = apps[case["app"]]
    subs = {"ai_" + key: SubAgent(apps[key], make) for key in app.delegates}
    def emit(event):
        if event["event_type"] != "data_table":
            events.append(event)
    state, error = {}, None
    try:
        state = app.run(case["question"], client, emit, subs)
    except Exception as exc:
        error = redact(str(exc), env)[:300]
    report = state.get("report", "")
    checks = grade(case, report) if case["id"].startswith("TS-") else {
        "gold_numbers_present": all(has_number(report, gold) for gold in case["gold_numbers"]),
        "cites_dt": "CSDL-DT" in cited_ids(report),
    }
    if case["id"] in {"TH-01", "TH-02", "TH-03", "TH-04"}:
        checks["cites_ts"] = "CSDL-TS" in cited_ids(report)
    checks["no_personal_data_in_report"] = not any(value and value in report for value in hidden)
    statuses = state.get("status") or {}
    checks["all_top_tasks_accepted"] = bool(statuses) and all(s == "accepted" for s in statuses.values())
    inner_reviews = []
    def visit(event):
        if event["event_type"] == "sub_event":
            visit(event["detail"]["event"])
        elif event["event_type"] == "task_reviewed":
            inner_reviews.append(event)
    for event in events:
        visit(event)
    checks["no_failed_inner_tasks"] = not any(e["detail"].get("next") in {"failed", "blocked", "budget_exceeded"} for e in inner_reviews)
    checks["no_exception"] = error is None and not state.get("plan_errors")
    checks["no_truncated_completions"] = not any(a.get("finish_reason") == "length" for a in attempts)
    usage = client.ledger.totals()
    estimated, unknown_billing = 0.0, 0
    for attempt in attempts:
        u = attempt.get("usage") or {}
        if not u:
            unknown_billing += 1
        pin, pout = providers[0].prices.get(attempt["model"]) or PRICES.get(attempt["model"], (0, 0))
        estimated += (u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout) / 1e6
    result = {"id": case["id"], "app": case["app"], "effort": effort, "question": case["question"],
              "gold_numbers": case.get("gold_numbers"), "report": report, "checks": checks,
              "passed": all(checks.values()), "error": error, "seconds": round(time.perf_counter() - started, 2),
              "usage": usage, "estimated_attempt_cost_usd": round(estimated, 8), "unknown_billing_attempts": unknown_billing,
              "http_attempts": attempts, "ledger": [asdict(call) for call in client.ledger.calls],
              "revisions": sum(e["detail"].get("attempt", 1) > 1 for e in inner_reviews),
              "max_prompt_chars": max((a["prompt_chars"] for a in attempts), default=0),
              "reasoning_tokens": sum((a.get("usage", {}).get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0 for a in attempts),
              "state": state, "events": events}
    path = folder / (case["id"] + "--" + effort + ".json")
    path.write_text(redact(json.dumps(result, ensure_ascii=False, indent=1), env), encoding="utf-8")
    return result


def summarize(results):
    out = {}
    for effort in ("low", "medium", "auto"):
        rows = [r for r in results if r["effort"] == effort]
        if not rows:
            continue
        out[effort] = {"runs": len(rows), "passed": sum(r["passed"] for r in rows),
            "median_seconds": round(statistics.median(r["seconds"] for r in rows), 2),
            "total_attempts": sum(len(r["http_attempts"]) for r in rows),
            "http_errors": sum(a.get("http_status") != 200 for r in rows for a in r["http_attempts"]),
            "revisions": sum(r["revisions"] for r in rows),
            "estimated_usd": round(sum(r["estimated_attempt_cost_usd"] for r in rows), 6),
            "unknown_billing_attempts": sum(r["unknown_billing_attempts"] for r in rows),
            "reasoning_tokens": sum(r["reasoning_tokens"] for r in rows),
            "max_prompt_chars": max(r["max_prompt_chars"] for r in rows),
            "failed_cases": [{"id": r["id"], "checks": [k for k, v in r["checks"].items() if not v]} for r in rows if not r["passed"]]}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--deadline-seconds", type=int, default=600)
    parser.add_argument("--only")
    args = parser.parse_args()
    env, apps, hidden = load_env(), build_apps(), secrets()
    providers, _ = load_providers(env)
    if not providers:
        raise RuntimeError("No usable provider")
    providers = providers[:1]  # Hold provider fixed across all three effort modes.
    todo = cases()
    if args.only:
        todo = [c for c in todo if c["id"] in args.only.split(",")]
    folder = RUNS_DIR / "effort-e2e" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(), "provider": providers[0].name,
                "modes": ["low", "medium", "auto"], "cases": todo, "parallel": args.parallel,
                "synthetic": {k: a.data.synthetic for k, a in apps.items() if a.data},
                "limitations": ["One sample per case/mode; no significance claim", "Legacy number matcher requires manual review", "Costs use configured prices; missing usage means unknown billing", "Identical 2000-token completion cap to live app"]}
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OUTPUT " + str(folder), flush=True)
    jobs = []
    for case in todo:
        modes = ["low", "medium", "auto"]
        random.Random(case["id"]).shuffle(modes)
        jobs.extend((case, effort) for effort in modes)
    llm_module._post = instrumented_post
    results = []
    try:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = [pool.submit(run_one, case, effort, apps, env, providers, hidden, folder, args.deadline_seconds) for case, effort in jobs]
            for future in as_completed(futures):
                row = future.result()
                results.append(row)
                summary = summarize(results)
                (folder / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps({"done": len(results), "total": len(jobs), "id": row["id"], "effort": row["effort"],
                    "passed": row["passed"], "failed_checks": [k for k, v in row["checks"].items() if not v],
                    "seconds": row["seconds"], "attempts": len(row["http_attempts"]),
                    "usd": row["estimated_attempt_cost_usd"], "max_prompt_chars": row["max_prompt_chars"]}), flush=True)
    finally:
        llm_module._post = _POST
    print(json.dumps(summarize(results)), flush=True)


if __name__ == "__main__":
    main()

