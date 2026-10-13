"""Settings authentication uses local test credentials and never calls a provider."""
import hashlib
import json

import pytest

from app import settings_auth as auth_module
from app.settings_auth import AuthError, SettingsAuth, hash_password, verify_password

PASSWORD = "fixture-only-lighthouse"


@pytest.fixture(scope="module")
def credential():
    return hash_password(PASSWORD)


@pytest.fixture
def configured(tmp_path, credential):
    path = tmp_path / "settings-auth.json"
    path.write_text(json.dumps(credential), encoding="utf-8")
    now = [100.0]
    return SettingsAuth(path, clock=lambda: now[0]), now


def test_hashes_are_salted_and_password_verification_is_exact(credential):
    other = hash_password(PASSWORD)
    assert credential["algorithm"] == "pbkdf2_sha256" and credential["iterations"] >= 600_000
    assert len(bytes.fromhex(credential["salt"])) >= 16
    assert credential["salt"] != other["salt"] and credential["digest"] != other["digest"]
    assert PASSWORD not in json.dumps(credential)
    assert verify_password(PASSWORD, credential)
    assert not verify_password(PASSWORD.upper(), credential)


def test_session_expires_absolutely_and_only_token_hash_is_stored(configured):
    auth, now = configured
    token = auth.login(PASSWORD, "client")
    assert token not in auth._sessions
    assert hashlib.sha256(token.encode("ascii")).hexdigest() in auth._sessions
    now[0] += 1799
    assert auth.authenticated(token)
    now[0] += 1
    assert not auth.authenticated(token)  # using the session does not extend its lifetime


def test_token_tampering_logout_and_new_process_reject_old_session(configured):
    auth, _ = configured
    token = auth.login(PASSWORD, "client")
    tampered = ("A" if token[0] != "A" else "B") + token[1:]
    assert not auth.authenticated(tampered)
    assert not auth.authenticated(None)
    assert not auth.authenticated("not-a-session")
    assert not SettingsAuth(auth.path).authenticated(token)
    assert auth.authenticated(token)
    auth.logout(token)
    auth.logout(None)
    assert not auth.authenticated(token)


def test_failed_logins_are_limited_per_client_and_window_expires(configured):
    auth, now = configured
    for _ in range(5):
        with pytest.raises(AuthError) as error:
            auth.login("incorrect-fixture", "client-one")
        assert error.value.status_code == 401
    with pytest.raises(AuthError) as error:
        auth.login(PASSWORD, "client-one")
    assert error.value.status_code == 429
    assert auth.authenticated(auth.login(PASSWORD, "client-two"))
    now[0] += 300
    assert auth.authenticated(auth.login(PASSWORD, "client-one"))


def test_success_resets_failed_attempts(configured):
    auth, _ = configured
    for _ in range(4):
        with pytest.raises(AuthError):
            auth.login("incorrect-fixture", "client")
    auth.login(PASSWORD, "client")
    with pytest.raises(AuthError) as error:
        auth.login("incorrect-fixture", "client")
    assert error.value.status_code == 401
    assert auth.authenticated(auth.login(PASSWORD, "client"))


@pytest.mark.parametrize("contents", [None, "{", "[]", "{}", '{"algorithm":"plaintext","password":"fixture"}'])
def test_absent_or_malformed_configuration_fails_closed(tmp_path, contents):
    path = tmp_path / "auth.json"
    if contents is not None:
        path.write_text(contents, encoding="utf-8")
    auth = SettingsAuth(path)
    assert not auth.configured and not auth.authenticated("anything")
    with pytest.raises(AuthError) as error:
        auth.login(PASSWORD, "client")
    assert error.value.status_code == 503


def test_rotation_and_removal_revoke_existing_sessions(configured, credential):
    auth, _ = configured
    old_token = auth.login(PASSWORD, "client")
    replacement = "fixture-only-rotated-password"
    auth.path.write_text(json.dumps(hash_password(replacement)), encoding="utf-8")
    assert auth.configured and not auth.authenticated(old_token)
    with pytest.raises(AuthError) as error:
        auth.login(PASSWORD, "client")
    assert error.value.status_code == 401
    token = auth.login(replacement, "client")
    assert auth.authenticated(token)
    auth.path.unlink()
    assert not auth.authenticated(token)
    auth.path.write_text(json.dumps(credential), encoding="utf-8")
    assert auth.configured and not auth.authenticated(old_token)


def test_oversized_password_and_weak_or_malformed_hash_skip_pbkdf(configured, credential, monkeypatch):
    auth, _ = configured

    def unexpected(*args, **kwargs):
        pytest.fail("PBKDF must not run for oversized passwords or invalid credential records")

    monkeypatch.setattr(auth_module.hashlib, "pbkdf2_hmac", unexpected)
    with pytest.raises(AuthError) as error:
        auth.login("x" * 1025, "client")
    assert error.value.status_code == 400
    with pytest.raises(ValueError):
        hash_password("x" * 1025)
    assert not verify_password("x" * 1025, credential)
    for record in ({**credential, "iterations": 1}, {**credential, "salt": "invalid"},
                   {**credential, "digest": "00"}, {**credential, "iterations": True}):
        assert not verify_password(PASSWORD, record)
        auth.path.write_text(json.dumps(record), encoding="utf-8")
        assert not auth.configured
