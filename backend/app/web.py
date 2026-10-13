"""Trang demo Credere: hỏi đáp trên trình duyệt với từng AI (AI Tuyển sinh, AI Đào tạo, AI Tổng hợp của Hiệu trưởng),
hiện kế hoạch và tiến độ các tác tử theo thời gian thực (SSE), kể cả các bước bên trong AI con khi AI Tổng hợp giao việc.

    python -m app.web [--port 8000] [--no-data]

Mỗi câu hỏi chạy với một client riêng (sổ ghi lời gọi nằm trên client). Lượt chạy thành công được lưu làm bản ghi;
nếu cổng API lỗi, trang phát lại bản ghi của đúng câu hỏi đó và ghi rõ là bản ghi, không giả làm chạy thật.
"""
import argparse
import json
import mimetypes
import queue
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import CONFIGS, DATA_ROOT, ENV_FILE, PROVIDERS_FILE, RUNS_DIR, Limits, load_env, redact
from .contracts import Source
from .llm import GatewayClient, LLMClient, LLMError, load_providers, provider_health, reset_health
from .providers import probe, save as save_providers, view as providers_view
from .retrieval import fold
from .sources import load_sources
from .apps import AppRuntime, SubAgent, build_apps, read_samples
from .domains import tuyen_sinh
from .domains.tuyen_sinh import (DEFAULT_DATA, DEFAULT_SOURCES, PLAN_HINT, SYNTH_HINT, WORKERS,  # noqa: F401  (dùng lại ở scripts)
                                 app_config, open_store)
from .tools.data import DataStore
from .settings_auth import SESSION_TTL, AuthError, SettingsAuth

REPLAY_DIR = RUNS_DIR / "demo-tuyen-sinh"
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}  # testclient: TestClient của FastAPI khi kiểm thử
STATIC = Path(__file__).parent / "static"  # công khai: CSS, font, icon, logo
PAGES = Path(__file__).parent / "pages"    # HTML của trang, chỉ qua route (trang Cài đặt phải qua admin_only)
SETTINGS_COOKIE = "credere_settings_session"
# Windows lấy kiểu MIME từ registry, có máy thiếu .woff2 hoặc ghi sai .css: khai báo rõ cho tệp tĩnh
for _ext, _type in {".css": "text/css", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".png": "image/png"}.items():
    mimetypes.add_type(_type, _ext)


def question_key(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(question)).strip("-")[:120] or "cau-hoi"


def sse(kind: str, data: dict) -> str:
    return f"event: {kind}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def samples_of(items: list) -> list[dict]:
    """Câu hỏi mẫu: {"kind": nhãn, "q": câu hỏi}; tệp cũ chỉ có danh sách câu hỏi thì nhãn trống."""
    return [i if isinstance(i, dict) else {"kind": "", "q": i} for i in items or []]


def create_app(sources: list[Source] | None = None, client_factory: Callable[[], LLMClient] | None = None,
               replay_dir: Path = REPLAY_DIR, limits: Limits = Limits(max_llm_calls=24), replay_pace_s: float = 1.2,
               samples: list | None = None, data: DataStore | None = None,
               providers_file: Path = PROVIDERS_FILE, env_file: Path = ENV_FILE, apps: dict[str, AppRuntime] | None = None,
               settings_auth_file: Path | None = None) -> FastAPI:
    """apps: các AI hiện trên trang (build_apps()); không truyền thì chỉ có AI Tuyển sinh dựng từ sources, data, samples (kiểm thử, bộ thử).
    providers_file, env_file: cấu hình nhà cung cấp và khóa; trang Cài đặt sửa hai tệp này, lượt hỏi sau dùng ngay."""
    if apps is None:
        workers, synth, plan = app_config(data)
        apps = {tuyen_sinh.KEY: AppRuntime(tuyen_sinh.KEY, tuyen_sinh.TEN, tuyen_sinh.DON_VI, tuyen_sinh.NGUOI_DUNG, tuyen_sinh.LINH_VUC,
                                           sources or [], data, workers, synth, plan, samples_of(samples), limits)}
    default = next(iter(apps))
    app = FastAPI(title="Credere")
    # tệp tĩnh công khai (CSS, font, icon, logo) nằm cục bộ, trang chạy không cần mạng; HTML vẫn đọc lại ở mỗi lần tải trang
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    env = load_env(env_file)  # đọc lại sau mỗi lần lưu ở trang Cài đặt (sửa tại chỗ để redact() che được khóa mới)
    settings_auth = SettingsAuth(settings_auth_file or env_file.with_name("settings-auth.json"))

    @app.middleware("http")
    async def private_settings_responses(request: Request, call_next):
        response = await call_next(request)
        if request.url.path == "/cai-dat" or request.url.path.startswith(("/api/providers", "/api/settings/")):
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Frame-Options"] = "DENY"
        return response

    def real_data(a: AppRuntime) -> bool:
        stores = [a.data] + [apps[k].data for k in a.delegates]
        return any(d is not None and not d.synthetic for d in stores)

    def client_for(a: AppRuntime) -> LLMClient:
        if client_factory:
            return client_factory()
        providers, strategy = load_providers(env, providers_file)
        # dữ liệu thật của Trường: chỉ gửi qua tài khoản chính thức (trusted), không qua cổng trung gian
        return GatewayClient(CONFIGS["A"], env, providers=providers, strategy=strategy, trusted_only=real_data(a))

    catalog = {}
    for a in apps.values():
        catalog.update({s.source_id: {"title": s.title, "url": s.url_or_document_id} for s in a.sources if s.access_scope == "public"})
        if a.data:
            catalog[a.data.source_id] = {"title": a.data.title(), "url": ""}

    def pick(key: str | None) -> AppRuntime:
        if key and key not in apps:
            raise HTTPException(404, f"Không có AI {key}.")
        return apps[key or default]

    def describe(a: AppRuntime) -> dict:
        members = [a] + [apps[k] for k in a.delegates]
        stores = [member.data for member in members if member.data is not None]
        return {"key": a.key, "ten": a.ten, "don_vi": a.don_vi, "nguoi_dung": a.nguoi_dung, "linh_vuc": a.linh_vuc,
                "data": bool(a.data), "title": a.data.title() if a.data else "",
                "source_count": len({s.source_id for member in members for s in member.sources if s.access_scope == "public"}),
                "query_count": sum(len(store.catalog) for store in stores),
                "snapshot": " · ".join(dict.fromkeys(store.snapshot for store in stores if store.snapshot)),
                "synthetic": bool(a.data and a.data.synthetic) or any(apps[k].data is not None and apps[k].data.synthetic for k in a.delegates),
                "delegates": [{"key": k, "ten": apps[k].ten} for k in a.delegates]}

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (PAGES / "index.html").read_text(encoding="utf-8")

    @app.get("/api/apps")
    def list_apps() -> list[dict]:
        return [describe(a) for a in apps.values()]

    @app.get("/api/sources")
    def list_sources() -> dict:
        return catalog

    @app.get("/api/samples")
    def list_samples(app_key: str | None = Query(None, alias="app")) -> list[dict]:
        return pick(app_key).samples

    @app.get("/api/replays")
    def list_replays(app_key: str | None = Query(None, alias="app")) -> list[str]:
        """Câu mẫu nào đã có bản ghi: trang đánh dấu để người trình bày biết câu nào phát lại được."""
        a = pick(app_key)
        return [s["q"] for s in a.samples if replay_path(a, s["q"]).exists()]

    @app.get("/api/info")
    def info(app_key: str | None = Query(None, alias="app")) -> dict:
        return describe(pick(app_key))

    # ---------- Cài đặt: chỉ trên máy này, xác thực bằng mật khẩu và phiên phía máy chủ ----------
    def settings_origin(request: Request, write: bool = False) -> None:
        if request.client is None or request.client.host not in LOCAL_HOSTS:
            raise HTTPException(403, "Trang Cài đặt chỉ mở được trên chính máy chạy hệ thống.")
        if write and request.headers.get("x-credere-admin") != "1":  # trang lạ không gửi được header này mà không bị trình duyệt chặn
            raise HTTPException(403, "Thiếu xác nhận từ trang Cài đặt.")

    def admin_only(request: Request, write: bool = False) -> None:
        settings_origin(request, write)
        if not settings_auth.authenticated(request.cookies.get(SETTINGS_COOKIE)):
            raise HTTPException(401, "Vui lòng nhập mật khẩu để mở khóa cài đặt.")

    @app.get("/cai-dat", response_class=HTMLResponse)
    def settings_page(request: Request) -> str:
        settings_origin(request)
        page = "settings.html" if settings_auth.authenticated(request.cookies.get(SETTINGS_COOKIE)) else "settings_login.html"
        return (PAGES / page).read_text(encoding="utf-8")

    @app.post("/api/settings/login")
    def unlock_settings(request: Request, body: dict = Body(...)) -> JSONResponse:
        settings_origin(request, write=True)
        password = body.get("password")
        if not isinstance(password, str):
            raise HTTPException(400, "Vui lòng nhập mật khẩu.")
        try:
            token = settings_auth.login(password, request.client.host)
        except AuthError as e:
            raise HTTPException(e.status_code, e.detail) from None
        settings_auth.logout(request.cookies.get(SETTINGS_COOKIE))
        response = JSONResponse({"ok": True})
        response.set_cookie(SETTINGS_COOKIE, token, max_age=SESSION_TTL, httponly=True, samesite="strict",
                            secure=request.url.scheme == "https", path="/")
        return response

    @app.post("/api/settings/logout")
    def lock_settings(request: Request) -> JSONResponse:
        settings_origin(request, write=True)
        settings_auth.logout(request.cookies.get(SETTINGS_COOKIE))
        response = JSONResponse({"ok": True})
        response.delete_cookie(SETTINGS_COOKIE, path="/", httponly=True, samesite="strict",
                               secure=request.url.scheme == "https")
        return response

    @app.get("/api/providers")
    def get_providers(request: Request) -> dict:
        admin_only(request)
        return {**providers_view(providers_file, env_file), "health": provider_health()}

    @app.put("/api/providers")
    def put_providers(request: Request, body: dict = Body(...)) -> dict:
        admin_only(request, write=True)
        try:
            out = save_providers(body, providers_file, env_file)
        except (LLMError, ValueError) as e:
            raise HTTPException(400, redact(str(e), env)[:300]) from None
        env.clear()
        env.update(load_env(env_file))
        reset_health()  # cấu hình mới: bỏ các lần tạm ngắt cũ
        return {**out, "health": provider_health()}

    @app.post("/api/providers/test")
    def test_provider(request: Request, body: dict = Body(...)) -> dict:
        admin_only(request, write=True)
        found = [p for p in load_providers(env, providers_file)[0] if p.name == body.get("name")]
        if not found:
            raise HTTPException(400, "Nhà cung cấp chưa được lưu, bị tắt hoặc chưa có khóa.")
        return probe(found[0], env, ping=bool(body.get("ping")))

    @app.post("/api/providers/reset-health")
    def clear_health(request: Request) -> dict:
        admin_only(request, write=True)
        reset_health()
        return {"health": provider_health()}

    @app.get("/api/ask")
    def ask(q: str = Query(..., min_length=3, max_length=500), mode: str = "live",
            app_key: str | None = Query(None, alias="app")) -> StreamingResponse:
        a = pick(app_key)
        gen = replay(a, q, "Người trình bày chọn phát lại bản ghi.") if mode == "replay" else live(a, q)
        return StreamingResponse(gen, media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    def replay_path(a: AppRuntime, q: str) -> Path:
        return replay_dir / f"{'' if a.key == tuyen_sinh.KEY else a.key + '--'}{question_key(q)}.json"

    def live(a: AppRuntime, q: str):
        events: queue.Queue = queue.Queue()
        box: dict = {}

        def work() -> None:
            try:
                llm = client_for(a)
                box["llm"] = llm
                subagents = {f"ai_{k}": SubAgent(apps[k], lambda k=k: client_for(apps[k])) for k in a.delegates}
                box["state"] = a.run(q, llm, events.put, subagents)
            except Exception as e:
                box["error"] = redact(f"{type(e).__name__}: {e}", env)[:300]
            finally:
                events.put(None)

        t0 = time.time()
        threading.Thread(target=work, daemon=True).start()
        recorded = []
        while True:
            try:
                e = events.get(timeout=15)
            except queue.Empty:
                yield ": keepalive\n\n"  # giữ kết nối khi model đang chạy lâu
                continue
            if e is None:
                break
            recorded.append({"t": round(time.time() - t0, 2), "event": e})
            yield sse("event", e)
        state = box.get("state") or {}
        gateway_down = bool(box.get("error")) or any("Lỗi gọi model" in x for x in state.get("plan_errors") or [])
        if gateway_down and replay_path(a, q).exists():
            yield from replay(a, q, f"Cổng API đang lỗi ({box.get('error') or state['plan_errors'][0]}).")
            return
        done = {"report": redact(state.get("report") or f"Không chạy được: {box.get('error')}", env),
                "usage": state.get("usage"), "status": state.get("status"), "elapsed_s": round(time.time() - t0, 1), "replayed": False}
        if state.get("report") and not gateway_down:
            save(a, q, recorded, done, box.get("llm"), state)
        yield sse("done", done)

    def strip_rows(e: dict) -> dict:
        """Bản ghi trên đĩa của dữ liệu thật: bỏ danh sách từng người trong bảng (kể cả bảng bên trong AI con), chỉ giữ số dòng."""
        if e["event_type"] == "data_table":
            return {**e, "detail": {**e["detail"], "rows": []}}
        if e["event_type"] == "sub_event":
            return {**e, "detail": {**e["detail"], "event": strip_rows(e["detail"]["event"])}}
        return e

    def save(a: AppRuntime, q: str, recorded: list, done: dict, llm, state: dict) -> None:
        if real_data(a):
            recorded = [{**r, "event": strip_rows(r["event"])} for r in recorded]
        replay_dir.mkdir(parents=True, exist_ok=True)
        record = {"app": a.key, "question": q, "recorded_at": datetime.now().isoformat(timespec="seconds"), "events": recorded, "done": done,
                  "history": state.get("history"), "ledger": [c.__dict__ for c in llm.ledger.calls] if llm else []}
        replay_path(a, q).write_text(redact(json.dumps(record, ensure_ascii=False, indent=1), env), encoding="utf-8")

    def replay(a: AppRuntime, q: str, reason: str):
        path = replay_path(a, q)
        if not path.exists():
            yield sse("done", {"report": "Chưa có bản ghi cho câu hỏi này.", "usage": None, "status": None, "replayed": True})
            return
        rec = json.loads(path.read_text(encoding="utf-8"))
        yield sse("replay", {"recorded_at": rec["recorded_at"], "reason": reason})
        last = 0.0
        for item in rec["events"]:
            time.sleep(min(max(item["t"] - last, 0), replay_pace_s))  # giữ nhịp như lúc chạy thật nhưng không chờ quá lâu
            last = item["t"]
            yield sse("event", {**item["event"], "_t": item["t"]})  # thời điểm lúc chạy thật
        yield sse("done", {**rec["done"], "replayed": True, "recorded_at": rec["recorded_at"]})

    return app


def main() -> None:
    import uvicorn
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # cửa sổ lệnh Windows mặc định không in được tiếng Việt
    ap = argparse.ArgumentParser(description="Trang demo Credere")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-data", action="store_true", help="chỉ dùng văn bản công khai (giai đoạn 1)")
    args = ap.parse_args()
    apps = build_apps(with_data=not args.no_data)
    for a in apps.values():
        extra = f", dữ liệu: {a.data.title()}" if a.data else (f", giao việc cho: {', '.join(a.delegates)}" if a.delegates else ", chưa nối dữ liệu")
        print(f"- {a.ten}: {len(a.sources)} văn bản{extra}")
    print(f"Mở http://{args.host}:{args.port}")
    uvicorn.run(create_app(apps=apps), host=args.host, port=args.port, log_level="warning")


def load_samples(sources_path: Path, data: DataStore | None) -> list[dict]:
    """Câu hỏi mẫu của một AI: demo_questions.json cạnh kho văn bản, thêm câu hỏi số liệu cạnh cơ sở dữ liệu nếu có."""
    return read_samples(sources_path.with_name("demo_questions.json"), data.path.with_name("demo_questions.json") if data else None,
                        data_mode=bool(data))


if __name__ == "__main__":
    main()
