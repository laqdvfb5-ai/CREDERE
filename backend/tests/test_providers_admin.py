"""Trang Cài đặt: đăng nhập, phiên quản trị và lưu nhà cung cấp mà không lộ khóa."""
import json
from http.cookies import SimpleCookie

import pytest
from fastapi.testclient import TestClient

from app import llm as llm_mod
from app.contracts import Source
from app.llm import FakeClient, load_providers, reset_health
from app.providers import set_env
from app.settings_auth import hash_password
from app.web import create_app

SOURCES = [Source(source_id="TS-100", title="Điểm chuẩn", text="Kế toán 16.")]
ADMIN = {"X-Credere-Admin": "1"}
SECRET = "sk-proxy-SECRET-0123456789"
TEST_PASSWORD = "test-only-settings-password-2026"


@pytest.fixture(scope="module")
def password_record():
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def setup(tmp_path, monkeypatch, password_record):
    monkeypatch.setattr(llm_mod, "PROVIDERS_FILE", tmp_path / "khong-dung.json")
    reset_health()
    env_file = tmp_path / ".env"
    env_file.write_text("# khóa của nhóm\nAIGW_BASE_URL=https://gw.example\nAIGW_OPENAI_KEY=sk-gateway-0123456789\n", encoding="utf-8")
    prov = tmp_path / "providers.json"
    prov.write_text(json.dumps({"providers": [{"name": "aigw", "base_url_env": "AIGW_BASE_URL", "key_env": "AIGW_OPENAI_KEY"}]}), encoding="utf-8")
    env_file.with_name("settings-auth.json").write_text(json.dumps(password_record), encoding="utf-8")
    app = create_app(SOURCES, client_factory=lambda: FakeClient(lambda *a: ""), replay_dir=tmp_path / "r",
                     providers_file=prov, env_file=env_file)
    client = TestClient(app)
    assert client.post("/api/settings/login", json={"password": TEST_PASSWORD}, headers=ADMIN).status_code == 200
    return client, prov, env_file


def body_with_proxy(**extra):
    return {"strategy": "round_robin", "providers": [
        {"name": "aigw", "base_url": "https://gw.example", "enabled": True},
        {"name": "proxyllm", "base_url": "https://api.proxyllm.example/v1", "key": SECRET, "trusted": False, "enabled": True,
         "models": {"gpt-6-sol": "openai/gpt-6-sol", "gpt-5.6-sol": "", "gpt-6-luna": "gpt-6-luna"},
         "prices": {"gpt-6-luna": ["0.08", "0.4"], "gpt-6-sol": ["", ""]}, **extra}]}


def test_save_writes_config_and_key_but_never_returns_the_key(setup):
    client, prov, env_file = setup
    r = client.put("/api/providers", json=body_with_proxy(), headers=ADMIN)
    assert r.status_code == 200 and SECRET not in r.text
    row = next(p for p in r.json()["providers"] if p["name"] == "proxyllm")
    assert row["has_key"] and row["active"] and row["key_env"] == "PROXYLLM_API_KEY"
    spec = json.loads(prov.read_text(encoding="utf-8"))
    assert spec["strategy"] == "round_robin" and SECRET not in prov.read_text(encoding="utf-8")
    saved = spec["providers"][1]
    assert saved["models"] == {"gpt-6-sol": "openai/gpt-6-sol", "gpt-6-luna": "gpt-6-luna"}  # để trống: không dùng
    assert saved["prices"] == {"gpt-6-luna": [0.08, 0.4]}
    env_text = env_file.read_text(encoding="utf-8")
    assert f"PROXYLLM_API_KEY={SECRET}" in env_text and env_text.startswith("# khóa của nhóm")  # giữ dòng cũ
    assert SECRET not in client.get("/api/providers").text
    providers, strategy = load_providers({"AIGW_BASE_URL": "https://gw.example", "AIGW_OPENAI_KEY": "sk-gateway-0123456789",
                                          "PROXYLLM_API_KEY": SECRET}, prov)
    assert [p.name for p in providers] == ["aigw", "proxyllm"] and strategy == "round_robin"


def test_second_save_without_key_keeps_existing_key(setup):
    client, _, env_file = setup
    client.put("/api/providers", json=body_with_proxy(), headers=ADMIN)
    b = body_with_proxy()
    del b["providers"][1]["key"]
    b["providers"].reverse()  # đổi thứ tự ưu tiên
    r = client.put("/api/providers", json=b, headers=ADMIN)
    assert [p["name"] for p in r.json()["providers"]] == ["proxyllm", "aigw"]
    assert env_file.read_text(encoding="utf-8").count("PROXYLLM_API_KEY=") == 1


def test_changing_base_url_of_env_backed_provider_updates_env(setup):
    client, prov, env_file = setup
    b = body_with_proxy()
    b["providers"][0]["base_url"] = "https://gw2.example"
    client.put("/api/providers", json=b, headers=ADMIN)
    assert "AIGW_BASE_URL=https://gw2.example" in env_file.read_text(encoding="utf-8")
    assert "base_url" not in json.loads(prov.read_text(encoding="utf-8"))["providers"][0]


@pytest.mark.parametrize("bad, message", [
    ({"name": "Proxy LLM"}, "Tên"), ({"base_url": "ftp://x"}, "http"), ({"key": "ngan"}, "khóa"),
    ({"prices": {"gpt-6-luna": ["a", "1"]}}, "giá"), ({"prices": {"gpt-9": ["1", "1"]}}, "model"),
])
def test_invalid_input_is_rejected_and_nothing_is_written(setup, bad, message):
    client, prov, env_file = setup
    before = (prov.read_text(encoding="utf-8"), env_file.read_text(encoding="utf-8"))
    r = client.put("/api/providers", json=body_with_proxy(**bad), headers=ADMIN)
    assert r.status_code == 400 and message.lower() in r.json()["detail"].lower()
    assert (prov.read_text(encoding="utf-8"), env_file.read_text(encoding="utf-8")) == before


def test_duplicate_names_and_bad_strategy_are_rejected(setup):
    client, _, _ = setup
    b = body_with_proxy()
    b["providers"][1]["name"] = "aigw"
    assert client.put("/api/providers", json=b, headers=ADMIN).status_code == 400
    assert client.put("/api/providers", json={**body_with_proxy(), "strategy": "ngau_nhien"}, headers=ADMIN).status_code == 400


def test_writes_need_the_admin_header(setup):
    client, prov, _ = setup
    before = prov.read_text(encoding="utf-8")
    assert client.put("/api/providers", json=body_with_proxy()).status_code == 403
    assert client.post("/api/providers/reset-health").status_code == 403
    assert client.post("/api/providers/test", json={"name": "aigw"}).status_code == 403
    assert prov.read_text(encoding="utf-8") == before
    assert client.get("/cai-dat").status_code == 200 and "Cài đặt nhà cung cấp" in client.get("/cai-dat").text


def test_settings_are_refused_from_other_machines(setup, tmp_path):
    _, prov, env_file = setup
    app = create_app(SOURCES, client_factory=lambda: FakeClient(lambda *a: ""), replay_dir=tmp_path / "r2",
                     providers_file=prov, env_file=env_file)
    remote = TestClient(app, client=("203.0.113.5", 50000))
    assert remote.get("/api/providers").status_code == 403 and remote.get("/cai-dat").status_code == 403
    assert remote.post("/api/settings/login", json={"password": TEST_PASSWORD}, headers=ADMIN).status_code == 403
    assert remote.post("/api/settings/logout", headers=ADMIN).status_code == 403
    assert remote.put("/api/providers", json=body_with_proxy(), headers=ADMIN).status_code == 403
    assert remote.post("/api/providers/test", json={"name": "aigw"}, headers=ADMIN).status_code == 403
    assert remote.post("/api/providers/reset-health", headers=ADMIN).status_code == 403
    # /static chỉ có CSS, font, icon, logo: không có đường vòng tới HTML của trang Cài đặt
    assert remote.get("/static/credere.css").status_code == 200
    assert remote.get("/static/settings.html").status_code == 404 and remote.get("/static/../pages/settings.html").status_code == 404


def test_locked_settings_return_login_page_without_configuration(setup):
    client, _, _ = setup
    client.cookies.clear()
    response = client.get("/cai-dat")
    assert response.status_code == 200 and "text/html" in response.headers["content-type"]
    assert "/api/settings/login" in response.text
    assert 'id="save"' not in response.text and "/api/providers" not in response.text
    assert TEST_PASSWORD not in response.text and "sk-gateway-0123456789" not in response.text
    # The public assistant remains accessible while provider administration is locked.
    assert client.get("/").status_code == 200
    assert client.get("/api/apps").status_code == 200


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/api/providers", None),
    ("PUT", "/api/providers", {"strategy": "failover", "providers": []}),
    ("POST", "/api/providers/test", {"name": "aigw", "ping": True}),
    ("POST", "/api/providers/reset-health", None),
])
def test_admin_header_does_not_bypass_password_session(setup, monkeypatch, method, path, body):
    client, prov, env_file = setup
    client.cookies.clear()
    before = (prov.read_bytes(), env_file.read_bytes())
    calls = []
    monkeypatch.setattr("app.web.probe", lambda *a, **k: calls.append("probe") or {})
    monkeypatch.setattr("app.web.reset_health", lambda: calls.append("reset"))
    response = client.request(method, path, json=body, headers=ADMIN)
    assert response.status_code == 401
    assert "providers" not in response.json() and "sk-gateway-0123456789" not in response.text
    assert (prov.read_bytes(), env_file.read_bytes()) == before
    assert not calls  # blocked before probing a provider or changing its state


def test_login_needs_header_and_correct_password(setup):
    client, _, _ = setup
    client.cookies.clear()
    assert client.post("/api/settings/login", json={"password": TEST_PASSWORD}).status_code == 403
    wrong = client.post("/api/settings/login", json={"password": "incorrect-test-only-password"}, headers=ADMIN)
    assert wrong.status_code == 401 and "set-cookie" not in wrong.headers
    assert not list(client.cookies.jar)
    assert client.get("/api/providers").status_code == 401
    assert client.post("/api/settings/login", json={"password": TEST_PASSWORD}, headers=ADMIN).status_code == 200
    assert client.get("/api/providers").status_code == 200


def test_successful_login_uses_protected_cookie_without_password_exposure(setup):
    client, _, env_file = setup
    client.cookies.clear()
    response = client.post("/api/settings/login", json={"password": TEST_PASSWORD}, headers=ADMIN)
    assert response.status_code == 200
    cookies = SimpleCookie()
    cookies.load(response.headers["set-cookie"])
    assert len(cookies) == 1
    cookie = next(iter(cookies.values()))
    assert cookie["httponly"] and cookie["samesite"].lower() == "strict" and cookie["path"] == "/"
    assert cookie.value and cookie.value != TEST_PASSWORD
    assert TEST_PASSWORD not in response.text + response.headers["set-cookie"]
    assert TEST_PASSWORD not in env_file.with_name("settings-auth.json").read_text(encoding="utf-8")


def test_forged_cookie_does_not_unlock_settings(setup):
    client, _, _ = setup
    cookie_name = next(iter(client.cookies.jar)).name
    client.cookies.clear()
    client.cookies.set(cookie_name, "forged-browser-cookie")
    assert client.get("/api/providers", headers=ADMIN).status_code == 401
    assert client.put("/api/providers", json=body_with_proxy(), headers=ADMIN).status_code == 401
    assert "/api/settings/login" in client.get("/cai-dat").text


def test_logout_requires_header_and_invalidates_copied_session(setup):
    client, _, _ = setup
    cookie = next(iter(client.cookies.jar))
    copied_header = {"Cookie": f"{cookie.name}={cookie.value}"}
    assert client.post("/api/settings/logout").status_code == 403
    assert client.get("/api/providers").status_code == 200
    response = client.post("/api/settings/logout", headers=ADMIN)
    assert response.status_code == 200
    assert cookie.name not in client.cookies
    assert client.get("/api/providers").status_code == 401
    assert client.get("/api/providers", headers=copied_header).status_code == 401
    assert "/api/settings/login" in client.get("/cai-dat").text


@pytest.mark.parametrize("path", ["/pages/settings.html", "/static/settings.html", "/static/../pages/settings.html",
                                  "/static/%2e%2e/pages/settings.html", "/static/%2e%2e/settings-auth.json"])
def test_settings_page_and_credentials_have_no_public_file_bypass(setup, path):
    client, _, _ = setup
    client.cookies.clear()
    response = client.get(path)
    assert response.status_code == 404
    assert 'id="save"' not in response.text and TEST_PASSWORD not in response.text


def test_login_fails_closed_when_credentials_have_not_been_configured(tmp_path):
    app = create_app(SOURCES, client_factory=lambda: FakeClient(lambda *a: ""), replay_dir=tmp_path / "r",
                     providers_file=tmp_path / "providers.json", env_file=tmp_path / ".env")
    client = TestClient(app)
    response = client.post("/api/settings/login", json={"password": TEST_PASSWORD}, headers=ADMIN)
    assert response.status_code == 503 and "set-cookie" not in response.headers
    assert client.get("/api/providers", headers=ADMIN).status_code == 401
    assert "/api/settings/login" in client.get("/cai-dat").text


def test_set_env_updates_in_place_and_handles_export(tmp_path):
    f = tmp_path / ".env"
    f.write_text("export A_KEY=old\n# ghi chú\nB=1\n", encoding="utf-8")
    set_env(f, {"A_KEY": "new", "C_KEY": "c"})
    assert f.read_text(encoding="utf-8") == "A_KEY=new\n# ghi chú\nB=1\nC_KEY=c\n"
