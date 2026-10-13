"""Kiểm thử client cổng API (httpx giả lập, không gọi mạng), đọc JSON, đọc .env và che khóa."""
import json

import httpx
import pytest

from app import llm as llm_mod
from app.config import ModelConfig, load_env, redact
from app.llm import GatewayClient, LLMError, Provider, load_providers, parse_json, provider_health, reset_health

KEY = "sk-THIS-IS-THE-GATEWAY-KEY-0123456789"
ENV = {"AIGW_BASE_URL": "https://gw.example", "AIGW_OPENAI_KEY": KEY}
OK = {"choices": [{"message": {"content": "Chào"}}], "usage": {"prompt_tokens": 1000, "completion_tokens": 100}}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    """Không đọc providers.json thật của máy; tình trạng nhà cung cấp không lan giữa các kiểm thử."""
    monkeypatch.setattr(llm_mod, "PROVIDERS_FILE", tmp_path / "khong-co.json")
    reset_health()
    yield
    reset_health()


@pytest.fixture
def gateway(monkeypatch):
    """Cổng giả: replies[model] là danh sách (mã HTTP, nội dung) trả lần lượt; ghi lại model đã gọi."""
    tried, replies = [], {}

    def post(url, timeout, headers, json):
        tried.append(json["model"])
        status, body = replies[json["model"]].pop(0)
        return httpx.Response(status, text=body if isinstance(body, str) else __import__("json").dumps(body))
    monkeypatch.setattr(llm_mod.httpx, "post", post)
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    return tried, replies


@pytest.fixture
def pool(monkeypatch):
    """Nhiều nhà cung cấp giả: replies[(nhà, model)] là danh sách (mã HTTP, nội dung); ghi lại (nhà, model, khóa) đã gọi."""
    tried, replies = [], {}
    hosts = {"https://a.example/v1/chat/completions": "a", "https://b.example/v1/chat/completions": "b",
             "https://c.example/v1/chat/completions": "c"}

    def post(url, timeout, headers, json):
        name = hosts[url]
        tried.append((name, json["model"], headers["Authorization"]))
        status, body = replies[(name, json["model"])].pop(0)
        return httpx.Response(status, text=body if isinstance(body, str) else __import__("json").dumps(body))
    monkeypatch.setattr(llm_mod.httpx, "post", post)
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    return tried, replies


POOL_ENV = {"A_KEY": "sk-aaaaaaaaaaaa", "B_KEY": "sk-bbbbbbbbbbbb", "C_KEY": "sk-cccccccccccc", "B_URL": "https://b.example"}


def providers(**kw):
    return [Provider("a", "https://a.example/v1", "A_KEY", **kw.get("a", {})),
            Provider("b", "https://b.example", "B_KEY", **kw.get("b", {})),
            Provider("c", "https://c.example/", "C_KEY", **kw.get("c", {}))]


def test_master_falls_back_when_primary_model_is_removed(gateway):
    tried, replies = gateway
    replies.update({"gpt-6-sol": [(404, '{"error": "model gpt-6-sol not found"}')], "gpt-5.6-sol": [(200, OK)]})
    client = GatewayClient(env=ENV)
    assert client.complete("master", [], label="plan") == "Chào"
    assert tried == ["gpt-6-sol", "gpt-5.6-sol"]
    call = client.ledger.calls[0]
    assert call.model == "gpt-5.6-sol" and call.cost_usd == pytest.approx((1000 * 2 + 100 * 10) / 1e6)


def test_retries_transient_errors_then_succeeds(gateway):
    tried, replies = gateway
    replies["gpt-6-luna"] = [(502, "Upstream"), (200, "không phải JSON"), (200, OK)]
    assert GatewayClient(env=ENV).complete("worker", []) == "Chào"
    assert tried == ["gpt-6-luna"] * 3


def test_auth_error_is_not_retried_and_key_is_masked_across_truncation(gateway):
    tried, replies = gateway
    replies["gpt-6-sol"] = [(401, "x" * 280 + f"invalid key {KEY} for model")]
    with pytest.raises(LLMError) as err:
        GatewayClient(env=ENV).complete("master", [])
    assert tried == ["gpt-6-sol"] and "sk-THIS" not in str(err.value)


def test_domain_worker_uses_its_own_model(gateway):
    tried, replies = gateway
    replies["gpt-6-sol"] = [(200, OK)]
    GatewayClient(ModelConfig(domain_worker="gpt-6-sol"), env=ENV).complete("domain_worker", [])
    assert tried == ["gpt-6-sol"]


def test_down_provider_hands_over_to_the_next_and_is_cooled_down(pool):
    tried, replies = pool
    replies.update({("a", "gpt-6-luna"): [(502, "x"), (503, "y")], ("b", "gpt-6-luna"): [(200, OK), (200, OK)]})
    client = GatewayClient(env=POOL_ENV, providers=providers())
    assert client.complete("worker", []) == "Chào"
    assert [(p, m) for p, m, _ in tried] == [("a", "gpt-6-luna")] * 2 + [("b", "gpt-6-luna")]
    assert tried[-1][2] == "Bearer sk-bbbbbbbbbbbb"  # mỗi nhà dùng khóa của nó
    assert client.ledger.calls[0].provider == "b" and client.ledger.totals()["providers"] == {"b": 1}
    assert "a/*" in provider_health()
    tried.clear()
    GatewayClient(env=POOL_ENV, providers=providers()).complete("worker", [])  # lượt sau: nhà a đang bị ngắt thì thử b trước
    assert [p for p, _, _ in tried] == ["b"]


def test_same_model_elsewhere_before_falling_back_to_a_weaker_model(pool):
    tried, replies = pool
    replies.update({("a", "gpt-6-sol"): [(404, "no such model")], ("b", "gpt-6-sol"): [(200, OK)]})
    GatewayClient(env=POOL_ENV, providers=providers()).complete("master", [])
    assert [(p, m) for p, m, _ in tried] == [("a", "gpt-6-sol"), ("b", "gpt-6-sol")]


def test_bad_key_disables_only_that_provider_and_is_masked(pool):
    tried, replies = pool
    replies.update({("a", "gpt-6-luna"): [(401, "invalid key sk-aaaaaaaaaaaa")], ("b", "gpt-6-luna"): [(200, OK)]})
    assert GatewayClient(env=POOL_ENV, providers=providers()).complete("worker", []) == "Chào"
    assert provider_health()["a/*"]["kind"] == "auth" and "sk-aaaa" not in json.dumps(provider_health())


def test_model_name_mapping_and_provider_prices(pool):
    tried, replies = pool
    replies[("c", "openai/gpt-6-luna")] = [(200, OK)]
    ps = providers(a={"models": {}}, b={"models": {"gpt-6-sol": "gpt-6-sol"}},
                   c={"models": {"gpt-6-luna": "openai/gpt-6-luna"}, "prices": {"gpt-6-luna": (1.0, 1.0)}})
    client = GatewayClient(env=POOL_ENV, providers=ps)
    client.complete("worker", [])
    assert tried[0][:2] == ("c", "openai/gpt-6-luna")
    call = client.ledger.calls[0]
    assert call.model == "gpt-6-luna" and call.cost_usd == pytest.approx(1100 / 1e6)


def test_round_robin_spreads_calls(pool):
    tried, replies = pool
    for name in "abc":
        replies[(name, "gpt-6-luna")] = [(200, OK)] * 3
    client = GatewayClient(env=POOL_ENV, providers=providers(), strategy="round_robin")
    for _ in range(3):
        client.complete("worker", [])
    assert sorted(p for p, _, _ in tried) == ["a", "b", "c"]


def test_trusted_only_uses_official_accounts(pool):
    tried, replies = pool
    replies[("b", "gpt-6-luna")] = [(200, OK)]
    GatewayClient(env=POOL_ENV, providers=providers(b={"trusted": True}), trusted_only=True).complete("worker", [])
    assert [p for p, _, _ in tried] == ["b"]
    with pytest.raises(LLMError, match="trusted"):
        GatewayClient(env=POOL_ENV, providers=providers(), trusted_only=True)


def test_providers_file_skips_keyless_entries_and_refuses_inline_keys(tmp_path):
    f = tmp_path / "providers.json"
    f.write_text(json.dumps({"strategy": "round_robin", "providers": [
        {"name": "a", "base_url": "https://a.example/v1", "key_env": "A_KEY", "trusted": True},
        {"name": "b", "base_url_env": "B_URL", "key_env": "B_KEY", "models": {"gpt-6-luna": "luna"}},
        {"name": "chua-co-khoa", "base_url": "https://x.example", "key_env": "X_KEY"},
        {"name": "tat", "base_url": "https://y.example", "key_env": "C_KEY", "enabled": False}]}), encoding="utf-8")
    ps, strategy = load_providers(POOL_ENV, f)
    assert [p.name for p in ps] == ["a", "b"] and strategy == "round_robin"
    assert ps[0].trusted and ps[1].base_url == "https://b.example" and ps[1].model_id("gpt-6-sol") is None
    f.write_text(json.dumps({"providers": [{"name": "a", "base_url": "https://a", "key_env": "A_KEY", "api_key": "sk-lo"}]}), encoding="utf-8")
    with pytest.raises(LLMError, match=".env"):
        load_providers(POOL_ENV, f)
    f.write_text(json.dumps({"providers": [{"name": "a", "base_url": "https://a", "key_env": "A_TOKEN"}]}), encoding="utf-8")
    with pytest.raises(LLMError, match="_KEY"):
        load_providers(POOL_ENV, f)


def test_unpriced_model_is_refused():
    with pytest.raises(LLMError, match="Chưa có giá"):
        GatewayClient(ModelConfig(worker="gpt-7-moi"), env=ENV)


@pytest.mark.parametrize("text, expected", [
    ('{"accepted": true}', {"accepted": True}),
    ('```json\n{"accepted": false}\n```', {"accepted": False}),
    (json.dumps({"data": {"ban_thao": "Mẫu:\n```\nĐiều 1\n```"}, "claims": []}), {"data": {"ban_thao": "Mẫu:\n```\nĐiều 1\n```"}, "claims": []}),
    ('{"accepted": true, "issues": []}\nGhi chú: định dạng {x}.', {"accepted": True, "issues": []}),
    ('Tôi dùng {refs}. Kết quả: {"accepted": true}', {"accepted": True}),
])
def test_parse_json_accepts_common_shapes(text, expected):
    assert parse_json(text) == expected


@pytest.mark.parametrize("text", ["", "không có JSON", "[1, 2]", "{hỏng"])
def test_parse_json_rejects_non_objects(text):
    with pytest.raises(ValueError):
        parse_json(text)


def test_load_env_handles_bom_spaces_quotes_and_comments(tmp_path):
    p = tmp_path / ".env"
    p.write_text('# chú thích\nAIGW_BASE_URL=https://gw\nAIGW_OPENAI_KEY = "sk-1"\nexport OPENALEX_API_KEY=\'oa\'\n\n', encoding="utf-8-sig")
    assert load_env(p) == {"AIGW_BASE_URL": "https://gw", "AIGW_OPENAI_KEY": "sk-1", "OPENALEX_API_KEY": "oa"}


def test_redact_masks_known_keys_bearer_and_api_key_param():
    env = {"AIGW_OPENAI_KEY": KEY, "AIGW_BASE_URL": "https://gw.example"}
    text = redact(f"key {KEY}; Authorization: Bearer abc.def; url ?search=x&api_key=OA-SECRET&y=1; https://gw.example", env)
    assert KEY not in text and "abc.def" not in text and "OA-SECRET" not in text and "https://gw.example" in text
