import importlib.util
from pathlib import Path

import httpx
import json
from app.contracts import Source


def load_bench(name="bench_effort_e2e.py"):
    path = Path(__file__).resolve().parents[1] / "scripts" / name
    spec = importlib.util.spec_from_file_location("effort_bench_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_attempt_observer_keeps_http_errors_and_usage(monkeypatch):
    bench = load_bench()
    rows = []
    bench._LOCAL.observer, bench._LOCAL.label = rows, "plan"
    monkeypatch.setattr(bench, "_POST", lambda *a, **k: httpx.Response(500, json={
        "usage": {"prompt_tokens": 123}, "error": {"message": "upstream"}}))
    response = bench.instrumented_post("https://example.org", json={"model": "x", "messages": [{"content": "abc"}], "reasoning_effort": "low"})
    assert response.status_code == 500
    assert rows[0]["usage"]["prompt_tokens"] == 123
    assert rows[0]["prompt_chars"] == 3
    bench._LOCAL.observer = None


def test_summary_keeps_failed_runs_in_denominator():
    bench = load_bench()
    rows = [{"id": "A", "effort": "low", "passed": success, "seconds": seconds,
             "http_attempts": [{"http_status": status}], "revisions": 0,
             "estimated_attempt_cost_usd": 0.1, "unknown_billing_attempts": 0,
             "reasoning_tokens": 10, "max_prompt_chars": 100,
             "checks": {"answer": success}} for success, seconds, status in [(True, 1, 200), (False, 9, 500)]]
    result = bench.summarize(rows)["low"]
    assert result["runs"] == 2 and result["passed"] == 1
    assert result["median_seconds"] == 5 and result["http_errors"] == 1
    assert result["estimated_usd"] == 0.2


def test_context_grader_requires_correct_value_source_and_verbatim_quote():
    bench = load_bench("bench_effort_context.py")
    quote = "The applicable tuition is 325000 VND per credit."
    sources = [Source(source_id="TS-200", title="Tuition", text=quote)]
    obj = {"marketing_fee": {"value": 325000, "source_id": "TS-200", "quote": quote}}
    checks = bench.check_answer(json.dumps(obj), sources)
    assert checks["marketing_fee_value"] and checks["marketing_fee_source"] and checks["marketing_fee_verbatim"]
    assert not all(checks.values())  # Other required facts are missing.
    obj["marketing_fee"]["source_id"] = "invented"
    checks = bench.check_answer(json.dumps(obj), sources)
    assert not checks["marketing_fee_source"] and not checks["marketing_fee_verbatim"]


def test_context_grader_rejects_invalid_json():
    bench = load_bench("bench_effort_context.py")
    assert bench.check_answer("not JSON", []) == {"valid_json": False}


def test_context_quote_heading_does_not_support_the_fee():
    bench = load_bench("bench_effort_context.py")
    quote = "Tuition for undergraduate enrollment"
    source = Source(source_id="TS-200", title="Tuition", text=quote)
    obj = {"marketing_fee": {"value": 325000, "source_id": "TS-200", "quote": quote}}
    checks = bench.check_answer(json.dumps(obj), [source])
    assert checks["marketing_fee_verbatim"] and checks["marketing_fee_value"]
    assert not checks["marketing_fee_evidence_anchor"]

