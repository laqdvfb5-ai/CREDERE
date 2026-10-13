"""OpenAlex: khóa API không được lọt ra kết quả, thông báo lỗi hay prompt (httpx giả lập, không gọi mạng)."""
import json

import httpx
import pytest

from app.graph import run
from app.llm import FakeClient
from app.tools import search as search_mod
from app.tools.search import OpenAlexSearch, SearchError
from test_graph import SOURCES, make_handler, prompts


def fake_get(status, body=None):
    def get(url, params, timeout):
        return httpx.Response(status, json=body, request=httpx.Request("GET", url, params=params))
    return get


def test_success_url_has_no_key(monkeypatch):
    monkeypatch.setattr(search_mod.httpx, "get", fake_get(200, {"meta": {"count": 42}}))
    hit = OpenAlexSearch(api_key="OA-SECRET-123").count_works("artificial intelligence", 2025)
    assert hit.count == 42 and "OA-SECRET-123" not in hit.url and "publication_year" in hit.url


@pytest.mark.parametrize("status", [403, 429, 500])
def test_http_error_message_has_no_key(monkeypatch, status):
    monkeypatch.setattr(search_mod.httpx, "get", fake_get(status))
    with pytest.raises(SearchError) as err:
        OpenAlexSearch(api_key="OA-SECRET-123").count_works("ai", 2025)
    assert str(status) in str(err.value) and "OA-SECRET-123" not in str(err.value)
    assert err.value.__cause__ is None and err.value.__suppress_context__


def test_key_never_reaches_state_or_prompts_on_quota_error(monkeypatch):
    monkeypatch.setattr(search_mod.httpx, "get", fake_get(429))
    llm = FakeClient(make_handler())
    state = run("Phân tích", llm, SOURCES, OpenAlexSearch(api_key="OA-SECRET-123"))
    assert state["status"]["T2"] == "failed"
    assert "OA-SECRET-123" not in json.dumps(state, ensure_ascii=False, default=str)
    assert all("OA-SECRET-123" not in p for p in prompts(llm, "search_queries:T2"))
