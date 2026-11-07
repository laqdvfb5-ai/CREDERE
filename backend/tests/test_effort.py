import httpx
import pytest

from app import llm
from app.llm import GatewayClient, LLMError, Provider


@pytest.mark.parametrize("setting,label,expected", [
    ("default", "plan", None), ("low", "review:T1#1", "low"),
    ("medium", "worker:T1#1", "medium"), ("high", "plan", "high"),
    ("auto", "plan", "medium"), ("auto", "plan_repair", "medium"),
    ("auto", "review:T1#1", "medium"), ("auto", "review_repair:T1#1", "medium"),
    ("auto", "worker:T1#1", "low"), ("auto", "synthesize", "low"),
])
def test_effort_payload_and_ledger(monkeypatch, setting, label, expected):
    def post(url, **kwargs):
        payload = kwargs["json"]
        assert payload.get("reasoning_effort") == expected
        assert ("reasoning_effort" in payload) == (expected is not None)
        return httpx.Response(200, json={"choices": [{"message": {"content": "OK"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50,
                      "completion_tokens_details": {"reasoning_tokens": 20}}})
    monkeypatch.setattr(llm, "_post", post)
    client = GatewayClient(env={"TEST_KEY": "test-key"},
        providers=[Provider("effort-test", "https://example.org", "TEST_KEY")], reasoning_effort=setting)
    assert client.complete("master", [], label=label) == "OK"
    call = client.ledger.calls[0]
    assert call.reasoning_effort == expected
    assert call.reasoning_tokens == 20
    assert call.output_tokens == 50  # Includes reasoning; do not charge it twice.


def test_invalid_effort_fails_before_request():
    with pytest.raises(LLMError, match="CREDERE_REASONING_EFFORT"):
        GatewayClient(env={"CREDERE_REASONING_EFFORT": "invalid"})
