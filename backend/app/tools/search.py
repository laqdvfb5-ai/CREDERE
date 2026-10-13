"""Công cụ tìm kiếm học thuật. OpenAlex dùng cho chạy thật; FakeSearch dùng khi kiểm thử."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

import httpx


@dataclass
class SearchHit:
    query: str
    year: int
    count: int
    url: str
    retrieved_at: str


class SearchTool(Protocol):
    def count_works(self, query: str, year: int) -> SearchHit: ...


class SearchError(RuntimeError):
    pass


class OpenAlexSearch:
    BASE = "https://api.openalex.org/works"

    def __init__(self, api_key: str | None = None, timeout: float = 30):
        self.api_key = api_key
        self.timeout = timeout

    def count_works(self, query: str, year: int) -> SearchHit:
        params = {"search": query, "filter": f"publication_year:{year}", "per-page": 1}
        if self.api_key:
            params["api_key"] = self.api_key
        # Lỗi của httpx chứa URL có api_key, nên chỉ báo mã lỗi và bỏ ngoại lệ gốc (from None)
        try:
            r = httpx.get(self.BASE, params=params, timeout=self.timeout)
            r.raise_for_status()
            count = int(r.json()["meta"]["count"])
        except httpx.HTTPStatusError as e:
            raise SearchError(f"OpenAlex trả về HTTP {e.response.status_code}.") from None
        except httpx.HTTPError as e:
            raise SearchError(f"Không kết nối được OpenAlex: {type(e).__name__}.") from None
        except (ValueError, KeyError, TypeError):
            raise SearchError("Phản hồi OpenAlex không đúng định dạng.") from None
        public_url = str(httpx.URL(self.BASE, params={k: v for k, v in params.items() if k != "api_key"}))
        return SearchHit(query, year, count, public_url, datetime.now(timezone.utc).isoformat(timespec="seconds"))


class FakeSearch:
    def __init__(self, counts: dict[tuple[str, int], int]):
        self.counts = counts
        self.calls: list[tuple[str, int]] = []

    def count_works(self, query: str, year: int) -> SearchHit:
        self.calls.append((query, year))
        return SearchHit(query, year, self.counts.get((query, year), 0), f"fake://openalex?q={query}&y={year}", "2026-09-26T00:00:00+00:00")
