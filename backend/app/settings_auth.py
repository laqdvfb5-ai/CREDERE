"""Password verification and short-lived, server-side sessions for settings."""
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from pathlib import Path
from typing import Callable

ITERATIONS = 600_000
SESSION_TTL = 1800
FAILURE_WINDOW = 300
MAX_FAILURES = 5
MAX_PASSWORD_LENGTH = 1024


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _valid_record(record: object) -> bool:
    if not isinstance(record, dict) or record.get("algorithm") != "pbkdf2_sha256":
        return False
    iterations, salt, digest = record.get("iterations"), record.get("salt"), record.get("digest")
    return (type(iterations) is int and ITERATIONS <= iterations <= 5_000_000
            and isinstance(salt, str) and len(salt) % 2 == 0
            and re.fullmatch(r"[0-9a-fA-F]{32,128}", salt) is not None
            and isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest) is not None)


def hash_password(password: str) -> dict:
    if not isinstance(password, str) or not 1 <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError("Mật khẩu phải có từ 1 đến 1024 ký tự.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return {"algorithm": "pbkdf2_sha256", "iterations": ITERATIONS, "salt": salt.hex(), "digest": digest.hex()}


def verify_password(password: str, record: dict) -> bool:
    if not isinstance(password, str) or not 1 <= len(password) <= MAX_PASSWORD_LENGTH or not _valid_record(record):
        return False
    try:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(record["salt"]), record["iterations"])
    except (ValueError, OverflowError):
        return False
    return hmac.compare_digest(digest, bytes.fromhex(record["digest"]))


class SettingsAuth:
    def __init__(self, path: Path, *, clock: Callable[[], float] = time.monotonic):
        self.path = Path(path)
        self._clock = clock
        self._lock = threading.Lock()
        self._fingerprint: str | None = None
        self._sessions: dict[str, float] = {}
        self._failures: dict[str, list[float]] = {}

    def _credentials(self) -> dict | None:
        """Called under the lock; changing/removing credentials revokes all sessions."""
        record = fingerprint = None
        try:
            raw = self.path.read_bytes()
            if len(raw) <= 4096:
                candidate = json.loads(raw.decode("utf-8-sig"))
                if _valid_record(candidate):
                    record = candidate
                    fingerprint = hashlib.sha256(raw).hexdigest()
        except (OSError, ValueError):
            pass
        if fingerprint != self._fingerprint:
            self._sessions.clear()
            self._failures.clear()
            self._fingerprint = fingerprint
        return record

    def _prune(self, now: float) -> None:
        self._sessions = {key: expiry for key, expiry in self._sessions.items() if expiry > now}
        self._failures = {client: recent for client, attempts in self._failures.items()
                          if (recent := [t for t in attempts if t > now - FAILURE_WINDOW])}

    @property
    def configured(self) -> bool:
        with self._lock:
            return self._credentials() is not None

    def login(self, password: str, client_id: str) -> str:
        with self._lock:
            record = self._credentials()
            if record is None:
                raise AuthError(503, "Chưa cấu hình mật khẩu Cài đặt hợp lệ trên máy chủ.")
            if not isinstance(password, str) or len(password) > MAX_PASSWORD_LENGTH:
                raise AuthError(400, "Mật khẩu không hợp lệ hoặc vượt quá 1024 ký tự.")
            now = self._clock()
            self._prune(now)
            if len(self._failures.get(client_id, [])) >= MAX_FAILURES:
                raise AuthError(429, "Đã nhập sai quá nhiều lần. Vui lòng thử lại sau 5 phút.")
            if not verify_password(password, record):
                self._failures.setdefault(client_id, []).append(now)
                raise AuthError(401, "Mật khẩu không đúng.")
            self._failures.pop(client_id, None)
            token = secrets.token_urlsafe(32)
            self._sessions[hashlib.sha256(token.encode("ascii")).hexdigest()] = self._clock() + SESSION_TTL
            return token

    def authenticated(self, token: str | None) -> bool:
        with self._lock:
            if self._credentials() is None:
                return False
            now = self._clock()
            self._prune(now)
            if not isinstance(token, str) or re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is None:
                return False
            return self._sessions.get(hashlib.sha256(token.encode("ascii")).hexdigest(), 0) > now

    def logout(self, token: str | None) -> None:
        if isinstance(token, str) and re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is not None:
            with self._lock:
                self._sessions.pop(hashlib.sha256(token.encode("ascii")).hexdigest(), None)
