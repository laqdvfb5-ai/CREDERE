"""Quản lý nhà cung cấp cho trang Cài đặt: đọc, kiểm tra và ghi providers.json; ghi khóa vào .env; gọi thử từng nhà.

Khóa chỉ đi một chiều: từ trang Cài đặt vào .env. Không hàm nào ở đây trả khóa ra ngoài (chỉ báo có hay chưa có).
"""
import json
import re
import shutil
import time
from pathlib import Path

import httpx

from .config import PRICES, load_env, redact
from .llm import DEFAULT_PROVIDERS, LLMError, Provider, load_providers

NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
ENV_VAR = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


def read_spec(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else json.loads(json.dumps(DEFAULT_PROVIDERS))


def key_env_for(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_") + "_API_KEY"


def view(path: Path, env_path: Path) -> dict:
    """Cấu hình để hiển thị: không có khóa, chỉ has_key; base_url lấy từ .env nếu nhà đó khai báo base_url_env."""
    spec, env = read_spec(path), load_env(env_path)
    active = {p.name for p in load_providers(env, path)[0]} if path.exists() else {"aigw"} if env.get("AIGW_OPENAI_KEY") else set()
    rows = []
    for p in spec.get("providers", []):
        rows.append({"name": p.get("name", ""), "base_url": p.get("base_url") or env.get(p.get("base_url_env", ""), ""),
                     "base_url_env": p.get("base_url_env", ""), "key_env": p.get("key_env", ""), "has_key": bool(env.get(p.get("key_env", ""))),
                     "models": p.get("models"), "prices": p.get("prices") or {}, "trusted": bool(p.get("trusted", False)),
                     "enabled": p.get("enabled", True) is not False, "active": p.get("name") in active})
    return {"strategy": spec.get("strategy", "failover"), "providers": rows, "system_models": list(PRICES), "file": str(path)}


def set_env(env_path: Path, updates: dict[str, str]) -> None:
    """Sửa hoặc thêm biến trong .env, giữ nguyên các dòng khác (kể cả chú thích)."""
    lines = env_path.read_text(encoding="utf-8-sig").splitlines() if env_path.exists() else []
    done = set()
    for i, line in enumerate(lines):
        s = line.strip().removeprefix("export ").strip()
        name = s.split("=", 1)[0].strip() if "=" in s and not s.startswith("#") else None
        if name in updates:
            lines[i] = f"{name}={updates[name]}"
            done.add(name)
    lines += [f"{k}={v}" for k, v in updates.items() if k not in done]
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save(body: dict, path: Path, env_path: Path) -> dict:
    """Ghi cấu hình từ trang Cài đặt. body: {strategy, providers: [{name, base_url, key (tùy chọn), models, prices, trusted, enabled}]}.
    Kiểm tra hết trước khi ghi; ghi xong mà đọc lại lỗi thì khôi phục bản cũ."""
    strategy = body.get("strategy", "failover")
    if strategy not in ("failover", "round_robin"):
        raise LLMError("Cách chọn phải là failover hoặc round_robin.")
    old = {p.get("name"): p for p in read_spec(path).get("providers", [])}
    providers, env_updates, seen = [], {}, set()
    for row in body.get("providers") or []:
        name = str(row.get("name", "")).strip()
        if not NAME.match(name):
            raise LLMError(f"Tên {name!r} không hợp lệ: chỉ chữ thường, số, gạch ngang, tối đa 32 ký tự.")
        if name in seen:
            raise LLMError(f"Trùng tên nhà cung cấp {name}.")
        seen.add(name)
        prev = old.get(name, {})
        key_env = prev.get("key_env") or key_env_for(name)
        entry = {"name": name, "key_env": key_env}
        base = str(row.get("base_url", "")).strip()
        if base and not re.match(r"^https?://[^\s]+$", base):
            raise LLMError(f"{name}: địa chỉ API phải bắt đầu bằng http:// hoặc https://")
        if prev.get("base_url_env"):  # nhà khai báo địa chỉ trong .env (như aigw): sửa địa chỉ thì ghi vào .env
            entry["base_url_env"] = prev["base_url_env"]
            if base:
                env_updates[prev["base_url_env"]] = base
        elif base:
            entry["base_url"] = base
        else:
            raise LLMError(f"{name}: thiếu địa chỉ API.")
        key = str(row.get("key") or "").strip()
        if key:
            if any(c.isspace() for c in key) or len(key) < 8:
                raise LLMError(f"{name}: khóa không hợp lệ.")
            env_updates[key_env] = key
        models = row.get("models")
        if models is not None:
            if not isinstance(models, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in models.items()):
                raise LLMError(f"{name}: phần đối chiếu model không hợp lệ.")
            entry["models"] = {k: v.strip() for k, v in models.items() if v.strip()}
        prices = {}
        for model, pair in (row.get("prices") or {}).items():
            if pair in (None, "", []) or (isinstance(pair, list) and all(str(x).strip() == "" for x in pair)):
                continue  # để trống: dùng bảng giá chung
            if model not in PRICES:
                raise LLMError(f"{name}: không có model {model} trong hệ thống.")
            try:
                p_in, p_out = (float(x) for x in pair)
            except (TypeError, ValueError):
                raise LLMError(f"{name}: giá của {model} phải là hai số (vào, ra).") from None
            if p_in < 0 or p_out < 0:
                raise LLMError(f"{name}: giá không được âm.")
            prices[model] = [p_in, p_out]
        if prices:
            entry["prices"] = prices
        if row.get("trusted"):
            entry["trusted"] = True
        if row.get("enabled") is False:
            entry["enabled"] = False
        providers.append(entry)
    spec = {"strategy": strategy, "providers": providers}
    backup_json = path.with_suffix(".json.bak")
    backup_env = env_path.with_name(env_path.name + ".bak")
    if path.exists():
        shutil.copy2(path, backup_json)
    if env_updates and env_path.exists():
        shutil.copy2(env_path, backup_env)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if env_updates:
            set_env(env_path, env_updates)
        load_providers(load_env(env_path), path)  # đọc lại được mới coi là xong
    except Exception:
        if backup_json.exists():
            shutil.copy2(backup_json, path)
        if env_updates and backup_env.exists():
            shutil.copy2(backup_env, env_path)
        raise
    return view(path, env_path)


def probe(p: Provider, env: dict[str, str], ping: bool = False) -> dict:
    """Liệt kê model của nhà cung cấp (GET /models) và, nếu ping, gọi thử mỗi model của hệ thống vài token."""
    key, base = env[p.key_env], p.url().removesuffix("/chat/completions")
    out = {"name": p.name, "models_listed": None, "listing": "", "checks": []}
    try:
        r = httpx.get(f"{base}/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
        if r.status_code == 200:
            out["models_listed"] = sorted(m.get("id", "") for m in r.json().get("data", []))
            out["listing"] = f"{len(out['models_listed'])} model"
        else:
            out["listing"] = f"HTTP {r.status_code}: {redact(r.text, env)[:160]}"
    except (httpx.HTTPError, ValueError, AttributeError) as e:
        out["listing"] = type(e).__name__
    ids = set(out["models_listed"] or [])
    for model in PRICES:
        mid = p.model_id(model)
        check = {"model": model, "provider_model": mid,
                 "listed": None if mid is None or not ids else mid in ids, "ping": None}
        if ping and mid:
            t0 = time.time()
            try:
                r = httpx.post(p.url(), headers={"Authorization": f"Bearer {key}"}, timeout=60,
                               json={"model": mid, "messages": [{"role": "user", "content": "Trả lời đúng một chữ: OK"}], "max_tokens": 5})
                check["ping"] = {"status": r.status_code, "seconds": round(time.time() - t0, 1),
                                 "detail": "" if r.status_code == 200 else redact(r.text, env)[:160]}
            except httpx.HTTPError as e:
                check["ping"] = {"status": None, "seconds": round(time.time() - t0, 1), "detail": type(e).__name__}
        out["checks"].append(check)
    out["similar"] = [i for i in sorted(ids) if any(k in i for k in ("gpt-6", "gpt-5.6", "sol", "luna"))][:15]
    return out
