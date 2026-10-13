"""Kiểm tra các nhà cung cấp trong ~/.credere/providers.json: có khóa chưa, có những model nào, (tùy chọn) gọi thử một câu ngắn.

    python scripts/check_providers.py            # chỉ liệt kê model (GET /v1/models, không tốn tiền)
    python scripts/check_providers.py --ping     # gọi thử mỗi model của hệ thống ở mỗi nhà, vài token

Không in khóa. Dùng để điền phần "models" trong providers.json khi nhà cung cấp đặt tên model khác.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import PRICES, PROVIDERS_FILE, load_env, redact  # noqa: E402
from app.llm import load_providers  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true", help="gọi thử mỗi model một câu ngắn (tốn vài token)")
    args = ap.parse_args()
    env = load_env()
    spec = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8-sig")) if PROVIDERS_FILE.exists() else None
    print(f"Tệp cấu hình: {PROVIDERS_FILE if spec else 'chưa có, chỉ dùng cổng AIGW trong .env'}")
    if spec:
        for p in spec.get("providers", []):
            if not env.get(p.get("key_env", "")):
                print(f"- {p.get('name')}: CHƯA CÓ KHÓA ({p.get('key_env')} trong ~/.credere/.env), bỏ qua")
    providers, strategy = load_providers(env)
    print(f"Cách chọn: {strategy}; nhà dùng được theo thứ tự: {', '.join(p.name for p in providers) or '(không có)'}")
    for p in providers:
        key = env[p.key_env]
        base = p.url().removesuffix("/chat/completions")
        try:
            r = httpx.get(f"{base}/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
            ids = sorted(m.get("id", "") for m in r.json().get("data", [])) if r.status_code == 200 else []
            listing = f"{len(ids)} model" if r.status_code == 200 else f"HTTP {r.status_code}: {redact(r.text, env)[:120]}"
        except (httpx.HTTPError, ValueError, AttributeError) as e:
            ids, listing = [], type(e).__name__
        print(f"\n== {p.name}{' (trusted)' if p.trusted else ''}: /models → {listing}")
        for model in PRICES:
            mid = p.model_id(model)
            status = "không khai báo" if mid is None else ("có trong danh sách" if mid in ids else "không thấy trong danh sách" if ids else "?")
            line = f"   {model} → {mid or '-'}: {status}"
            if args.ping and mid:
                t0 = time.time()
                try:
                    r = httpx.post(p.url(), headers={"Authorization": f"Bearer {key}"}, timeout=60,
                                   json={"model": mid, "messages": [{"role": "user", "content": "Trả lời đúng một chữ: OK"}], "max_tokens": 5})
                    line += f"; gọi thử HTTP {r.status_code} ({time.time() - t0:.1f} s)" + ("" if r.status_code == 200 else f": {redact(r.text, env)[:100]}")
                except httpx.HTTPError as e:
                    line += f"; gọi thử lỗi {type(e).__name__}"
            print(line)
        similar = [i for i in ids if any(k in i for k in ("gpt-6", "gpt-5.6", "sol", "luna"))]
        if similar:
            print(f"   model có tên gần giống: {', '.join(similar[:12])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
