"""Cấu hình model, giới hạn lượt chạy và bảng giá. Cấu hình A được chốt ngày 26/09/2026 (xem PLAN.md)."""
import os
import re
from dataclasses import dataclass
from pathlib import Path

CREDERE_HOME = Path(os.environ.get("CREDERE_HOME", Path.home() / ".credere"))  # ngoài OneDrive
ENV_FILE = CREDERE_HOME / ".env"
PROVIDERS_FILE = CREDERE_HOME / "providers.json"  # danh sách nhà cung cấp; khóa vẫn nằm trong .env
RUNS_DIR = CREDERE_HOME / "runs"
DATA_ROOT = Path(os.environ.get("CREDERE_DATA", Path.home() / "credere-data"))  # kho tài liệu theo DATA_PLAN.md, ngoài OneDrive


@dataclass(frozen=True)
class ModelConfig:
    master: str = "gpt-6-sol"
    master_fallback: str = "gpt-5.6-sol"
    worker: str = "gpt-6-luna"         # tìm kiếm, phân tích
    domain_worker: str = "gpt-6-luna"  # tác tử chuyên môn bám nguồn; M-1 không đạt thì đổi sang gpt-6-sol


CONFIGS = {
    "A": ModelConfig(),
    "C": ModelConfig(worker="gpt-6-sol", domain_worker="gpt-6-sol"),  # đối chứng NFR2: mọi vai trò dùng gpt-6-sol
}


@dataclass(frozen=True)
class Limits:
    max_tasks: int = 8
    max_parallel: int = 3
    max_llm_calls: int = 40
    max_cost_usd: float = 2.0  # kiểm tra giữa các đợt; một đợt đang chạy không bị cắt ngang
    max_revisions: int = 2  # tối đa 2 lượt sửa, tức 3 lần thực thi mỗi nhiệm vụ

    @property
    def recursion_limit(self) -> int:
        # mỗi lần thực thi tốn 2 bước graph (execute, join); chuỗi dài nhất là max_tasks nhiệm vụ nối tiếp, mỗi nhiệm vụ chạy hết số lần
        return 2 * self.max_tasks * (self.max_revisions + 1) + 10


# Giá niêm yết OpenRouter, USD cho mỗi 1 triệu token (vào, ra)
PRICE_DATE = "2026-09-26"
PRICES = {
    "gpt-6-sol": (2.0, 10.0),
    "gpt-5.6-sol": (2.0, 10.0),
    "gpt-6-luna": (0.10, 0.50),
}


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    """Đọc .env: bỏ BOM, dòng trống, chú thích, tiền tố export và dấu nháy bao quanh giá trị."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, value = s.removeprefix("export ").split("=", 1)
        env[key.strip()] = value.strip().strip("\"'")
    return env


def redact(text: str, env: dict[str, str] | None = None) -> str:
    """Che khóa bí mật (giá trị *_KEY trong .env, Bearer token, tham số api_key) trước khi ghi ra đĩa hoặc gửi cho model."""
    env = load_env() if env is None else env
    for key, value in env.items():
        if key.endswith("_KEY") and len(value) >= 8:
            text = text.replace(value, "***")
    text = re.sub(r"(?i)bearer\s+[^\s\"']+", "Bearer ***", text)
    return re.sub(r"(?i)(api_key=)[^&\s\"']+", r"\1***", text)
