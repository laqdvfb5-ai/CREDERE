"""Small paid gateway compatibility probe, not an end-to-end quality evaluation.

Run explicitly: python scripts/bench_effort.py
Each case/effort sends exactly one request without retries or provider fallback.
HTTP 200 only proves acceptance, not that the gateway honors reasoning_effort.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import PRICES, RUNS_DIR, load_env
from app.llm import load_providers, parse_json


def main():
    env = load_env()
    providers, _ = load_providers(env)
    cases = [
        ("gpt-6-sol", "plan", 'Return JSON only: {"tasks":[{"id":"A","depends_on":[]},{"id":"B","depends_on":[]},{"id":"C","depends_on":["A","B"]}]}. A gets admissions totals, B gets academic totals independently, C compares their results. Do not add tasks.'),
        ("gpt-6-luna", "query", 'Return JSON only. Catalog: xac_nhan_theo_nganh(ma_xet_tuyen optional), tong_quan(). Request: confirmed admissions for accounting, major code 7340301. Format: {"name":"query name","params":{}}.'),
    ]
    out = RUNS_DIR / "effort" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    results = []
    with httpx.Client(timeout=90) as client:
        for model, case, prompt in cases:
            provider = next(p for p in providers if p.model_id(model))
            for effort in ("low", "medium"):
                row = {"model": model, "case": case, "effort": effort, "provider": provider.name}
                start = time.perf_counter()
                try:
                    response = client.post(provider.url(), headers={"Authorization": "Bearer " + env[provider.key_env]},
                        json={"model": provider.model_id(model), "messages": [{"role": "user", "content": prompt}],
                              "max_tokens": 2000, "reasoning_effort": effort})
                    row["http_status"] = response.status_code
                    if response.status_code == 200:
                        body = response.json()
                        usage = body.get("usage") or {}
                        row["usage"] = usage
                        row["usage_present"] = bool(usage)
                        text = body["choices"][0]["message"].get("content") or ""
                        row["answer"] = text
                        row["finish_reason"] = body["choices"][0].get("finish_reason")
                        pin, pout = provider.prices.get(model) or PRICES[model]
                        row["estimated_usd"] = (usage.get("prompt_tokens", 0) * pin + usage.get("completion_tokens", 0) * pout) / 1e6
                        try:
                            obj = parse_json(text)
                            if case == "query":
                                row["passed"] = obj.get("name") == "xac_nhan_theo_nganh" and obj.get("params") == {"ma_xet_tuyen": "7340301"}
                            else:
                                tasks = obj.get("tasks", [])
                                row["passed"] = len(tasks) == 3 and {t["id"]: set(t["depends_on"]) for t in tasks} == {"A": set(), "B": set(), "C": {"A", "B"}}
                        except (ValueError, KeyError, TypeError):
                            row["passed"] = False
                    else:
                        row["passed"] = False
                except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
                    row.update(passed=False, error=type(error).__name__)
                row["seconds"] = round(time.perf_counter() - start, 3)
                results.append(row)
                (out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps(row, ensure_ascii=True), flush=True)
    print("Report: " + str(out), flush=True)


if __name__ == "__main__":
    main()
