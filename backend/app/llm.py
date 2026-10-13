"""Gọi model qua nhiều nhà cung cấp (định dạng OpenAI) theo vai trò; ghi sổ token và chi phí từng lời gọi (NFR2, NFR3).

Danh sách nhà cung cấp nằm trong ~/.credere/providers.json (xem backend/providers.example.json), khóa nằm trong .env.
Không có providers.json thì chỉ dùng cổng AIGW như trước. Mỗi model được thử lần lượt ở các nhà cung cấp có model đó;
nhà cung cấp lỗi bị tạm ngắt (dùng chung cho mọi lượt chạy trong tiến trình), lỗi khóa thì ngắt lâu hơn.
Sổ ghi nằm trên client, nên mỗi lượt chạy dùng một client riêng; không dùng chung một client cho nhiều lượt chạy đồng thời.
"""
import itertools
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Protocol

import httpx

from .config import PRICES, PROVIDERS_FILE, ModelConfig, load_env, redact

Role = Literal["master", "worker", "domain_worker"]


@dataclass
class LLMCall:
    role: Role
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_s: float
    label: str = ""
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
    provider: str = ""


@dataclass
class Ledger:
    calls: list[LLMCall] = field(default_factory=list)

    def totals(self, start: int = 0) -> dict:
        calls = self.calls[start:]
        providers: dict[str, int] = {}
        for c in calls:
            if c.provider:
                providers[c.provider] = providers.get(c.provider, 0) + 1
        return {"calls": len(calls),
                "input_tokens": sum(c.input_tokens for c in calls),
                "output_tokens": sum(c.output_tokens for c in calls),
                "cost_usd": round(sum(c.cost_usd for c in calls), 6),
                "providers": providers}


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    ledger: Ledger

    def complete(self, role: Role, messages: list[dict], max_tokens: int = 2000, label: str = "") -> str: ...


@dataclass
class Provider:
    name: str
    base_url: str
    key_env: str                                   # tên biến trong .env chứa khóa; phải kết thúc bằng _KEY để redact() che được
    models: dict[str, str] | None = None           # tên model của hệ thống -> tên ở nhà cung cấp; None: dùng cùng tên
    prices: dict[str, tuple[float, float]] = field(default_factory=dict)  # giá riêng của nhà này (USD/1 triệu token); thiếu thì dùng PRICES
    trusted: bool = False                          # tài khoản chính thức; khi nối dữ liệu thật chỉ dùng nhà có trusted

    def model_id(self, model: str) -> str | None:
        return model if self.models is None else self.models.get(model)

    def url(self) -> str:
        base = self.base_url.rstrip("/")
        return (base if base.endswith("/v1") else base + "/v1") + "/chat/completions"


DEFAULT_PROVIDERS = {"providers": [{"name": "aigw", "base_url_env": "AIGW_BASE_URL", "key_env": "AIGW_OPENAI_KEY"}]}


def load_providers(env: dict[str, str], path: Path | None = None) -> tuple[list[Provider], str]:
    """Nhà cung cấp dùng được (có địa chỉ và khóa trong .env) theo thứ tự ưu tiên, và cách chọn ("failover" hoặc "round_robin")."""
    path = path or PROVIDERS_FILE
    spec = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else DEFAULT_PROVIDERS
    out = []
    for p in spec.get("providers", []):
        name = p.get("name", "?")
        if {"api_key", "key"} & p.keys():
            raise LLMError(f"{name}: khóa phải nằm trong ~/.credere/.env, không ghi trong providers.json")
        if not str(p.get("key_env", "")).endswith("_KEY"):
            raise LLMError(f"{name}: key_env phải là tên biến kết thúc bằng _KEY (để khóa được che khi ghi nhật ký)")
        base = p.get("base_url") or env.get(p.get("base_url_env", ""), "")
        if p.get("enabled", True) is False or not base or not env.get(p["key_env"]):
            continue  # tắt, hoặc chưa có khóa: bỏ qua, không báo lỗi
        out.append(Provider(name, base, p["key_env"], p.get("models"),
                            {m: tuple(v) for m, v in (p.get("prices") or {}).items()}, bool(p.get("trusted", False))))
    strategy = spec.get("strategy", "failover")
    if strategy not in ("failover", "round_robin"):
        raise LLMError(f"strategy {strategy!r} không hợp lệ; dùng failover hoặc round_robin")
    return out, strategy


# Tình trạng nhà cung cấp, dùng chung cho mọi client trong tiến trình (các lượt chạy song song học được từ nhau)
COOLDOWN_S = {"transient": 120, "auth": 900, "no_model": 900}
_health: dict[tuple[str, str], dict] = {}  # (nhà cung cấp, model hoặc "*") -> {"until", "kind", "reason"}
_health_lock = threading.Lock()
_rotation = itertools.count()


def _mark(provider: str, model: str, kind: str, reason: str) -> None:
    with _health_lock:
        _health[(provider, model)] = {"until": time.time() + COOLDOWN_S[kind], "kind": kind, "reason": reason}


def _clear(provider: str, model: str) -> None:
    with _health_lock:
        _health.pop((provider, "*"), None)
        _health.pop((provider, model), None)


def _state(provider: str, model: str) -> dict | None:
    with _health_lock:
        now = time.time()
        for key in ((provider, "*"), (provider, model)):
            h = _health.get(key)
            if h and h["until"] > now:
                return h
    return None


def provider_health() -> dict[str, dict]:
    """Nhà cung cấp đang bị tạm ngắt và lý do (để hiển thị, kiểm tra)."""
    with _health_lock:
        now = time.time()
        return {f"{p}/{m}": {**h, "con_giay": round(h["until"] - now)} for (p, m), h in _health.items() if h["until"] > now}


def reset_health() -> None:
    with _health_lock:
        _health.clear()


class GatewayClient:
    """Gọi model qua các nhà cung cấp trong providers.json. Với mỗi model, thử lần lượt các nhà có model đó; tác tử điều phối
    còn chuyển sang model dự phòng khi mọi nhà đều lỗi. trusted_only: chỉ dùng nhà có trusted (khi nối dữ liệu thật)."""

    def __init__(self, models: ModelConfig = ModelConfig(), env: dict[str, str] | None = None, timeout: float = 240,
                 providers: list[Provider] | None = None, strategy: str | None = None, trusted_only: bool = False):
        env = env if env is not None else load_env()
        missing = sorted({models.master, models.master_fallback, models.worker, models.domain_worker} - PRICES.keys())
        if missing:
            raise LLMError(f"Chưa có giá cho model {', '.join(missing)} trong config.PRICES")
        loaded, default_strategy = load_providers(env) if providers is None else (providers, "failover")
        self.providers = [p for p in loaded if p.trusted or not trusted_only]
        if not self.providers:
            raise LLMError("Không có nhà cung cấp nào dùng được" + (" có trusted" if trusted_only else "")
                           + ": kiểm tra ~/.credere/providers.json và khóa trong ~/.credere/.env")
        for role, names in (("master", [models.master, models.master_fallback]), ("worker", [models.worker]),
                            ("domain_worker", [models.domain_worker])):
            if not any(p.model_id(m) for m in names for p in self.providers):
                raise LLMError(f"Không nhà cung cấp nào có model cho vai trò {role}: {', '.join(names)}")
        self.strategy = strategy or default_strategy
        self._keys = {p.name: env[p.key_env] for p in self.providers}
        self._env = env
        self.models = models
        self.timeout = timeout
        self.ledger = Ledger()

    def _safe(self, text: str) -> str:
        for key in self._keys.values():
            text = text.replace(key, "***")
        return redact(text, self._env)[:300]  # che trước rồi mới cắt, để không lộ một phần khóa

    def _order(self, model: str) -> list[Provider]:
        cands = [p for p in self.providers if p.model_id(model)]
        if self.strategy == "round_robin" and cands:
            k = next(_rotation) % len(cands)
            cands = cands[k:] + cands[:k]
        ok, cooling = [], []
        for p in cands:
            h = _state(p.name, model)
            if h is None:
                ok.append(p)
            elif h["kind"] == "transient":
                cooling.append(p)  # vừa lỗi tạm thời: vẫn thử, nhưng sau cùng
        return ok + cooling  # nhà lỗi khóa hoặc không có model thì bỏ qua đến khi hết hạn ngắt

    def complete(self, role: Role, messages: list[dict], max_tokens: int = 2000, label: str = "") -> str:
        candidates = {"master": [self.models.master, self.models.master_fallback],
                      "domain_worker": [self.models.domain_worker]}.get(role, [self.models.worker])
        errors = []
        for model in candidates:  # cùng model ở nhà khác trước, rồi mới hạ xuống model dự phòng
            order = self._order(model)
            for p in order:
                tries = 3 if len(order) == 1 else 2
                last, gave_up = "", False
                for attempt in range(tries):
                    if attempt:
                        time.sleep(3 * attempt)
                    t0 = time.time()
                    try:
                        r = httpx.post(p.url(), timeout=self.timeout, headers={"Authorization": f"Bearer {self._keys[p.name]}"},
                                       json={"model": p.model_id(model), "messages": messages, "max_tokens": max_tokens})
                    except httpx.HTTPError as e:
                        last = f"{p.name}/{model}: {type(e).__name__}"
                        continue
                    if r.status_code in (429, 500, 502, 503, 504):
                        last = f"{p.name}/{model}: HTTP {r.status_code}: {self._safe(r.text)}"
                        continue
                    if r.status_code in (400, 404, 422):  # nhà này không có hoặc không nhận model: thử nhà khác
                        last, gave_up = f"{p.name}/{model}: HTTP {r.status_code}: {self._safe(r.text)}", True
                        if r.status_code == 404:
                            _mark(p.name, model, "no_model", last)
                        break
                    if r.status_code != 200:  # 401, 403: lỗi khóa; thử lại không có ích, ngắt nhà này
                        last, gave_up = f"{p.name}/{model}: HTTP {r.status_code}: {self._safe(r.text)}", True
                        _mark(p.name, "*", "auth", last)
                        break
                    try:
                        body = r.json()
                        content = body["choices"][0]["message"].get("content") or ""
                        text = content if isinstance(content, str) else "".join(x.get("text", "") for x in content)
                        usage = body.get("usage") or {}
                        tin, tout = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
                    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
                        last = f"{p.name}/{model}: phản hồi không đúng định dạng"
                        continue
                    _clear(p.name, model)
                    price_in, price_out = p.prices.get(model) or PRICES[model]
                    self.ledger.calls.append(LLMCall(role, model, tin, tout, (tin * price_in + tout * price_out) / 1_000_000,
                                                     round(time.time() - t0, 2), label, provider=p.name))
                    return text
                if not gave_up:
                    _mark(p.name, "*", "transient", last)
                errors.append(last)
        raise LLMError("Gọi model thất bại ở mọi nhà cung cấp: " + (" | ".join(errors[-4:]) or "không nhà nào sẵn sàng"))


class FakeClient:
    """Model giả lập cho kiểm thử: handler(role, messages, label) trả về văn bản."""

    def __init__(self, handler: Callable[[Role, list[dict], str], str]):
        self.handler = handler
        self.ledger = Ledger()
        self.transcript: list[tuple[Role, str, list[dict]]] = []

    def complete(self, role: Role, messages: list[dict], max_tokens: int = 2000, label: str = "") -> str:
        self.transcript.append((role, label, list(messages)))  # bản sao: người gọi có thể nối thêm tin nhắn sau đó
        text = self.handler(role, messages, label)
        self.ledger.calls.append(LLMCall(role, f"fake-{role}", 100, 20, 0.0, 0.0, label))
        return text


def parse_json(text: str) -> dict:
    """Đọc đối tượng JSON từ câu trả lời: thử nguyên văn trước, sau đó lấy đối tượng đầu tiên đọc được (kể cả trong khối ```json)."""
    t = (text or "").strip()
    try:
        obj = json.loads(t)
    except ValueError:
        obj = None
        decoder = json.JSONDecoder()
        for i, ch in enumerate(t):
            if ch == "{":
                try:
                    obj = decoder.raw_decode(t, i)[0]
                    break
                except ValueError:
                    continue
    if not isinstance(obj, dict):
        raise ValueError("Câu trả lời không chứa đối tượng JSON.")
    return obj
