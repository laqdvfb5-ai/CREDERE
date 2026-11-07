# Cost accounting

Reference: https://developers.openai.com/api/docs/pricing
Checked: 2026-11-07. Standard text processing, USD per million tokens.

| Model | Input | Cached input | Output | Status |
| --- | ---: | ---: | ---: | --- |
| gpt-6-luna | 0.10 | 0.01 | 0.50 | Official listed rate |
| gpt-5.6-sol | 4.00 | 0.40 | 20.00 | Official listed rate |
| gpt-6-sol | 2.00 | No discount assumed | 10.00 | Unverified legacy estimate; exact model not found on referenced page |

Cost = ((input - cached) * input_rate + cached * cached_rate + output * output_rate) / 1e6.
Reasoning tokens are already included in output tokens; do not bill them twice.
Provider-specific prices are ignored for this OpenAI-equivalent estimate. This is not a gateway invoice.

The ledger preserves cached_input_tokens (null when absent), pricing_basis, pricing_verified and price_date. Totals expose missing cache metadata and unverified pricing counts. Missing cache usage is conservatively charged at full input price, not represented as a verified zero-cache hit.

Existing saved reports and EFFORT_BENCHMARK.md are historical estimates and are not rewritten. They cannot be retroactively cache-adjusted without the original cache usage. No official gpt-6-sol price or model mapping is assumed.
