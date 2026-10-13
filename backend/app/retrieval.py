"""Xếp hạng nguồn theo mức liên quan bằng BM25 đơn giản: bỏ dấu, tách âm tiết và cặp âm tiết, không cần thư viện ngoài.

Dùng để giới hạn lượng văn bản gửi cho model khi kho nguồn lớn (ví dụ toàn bộ tài liệu tuyển sinh).
"""
import math
import re
import unicodedata
from collections import Counter

from .contracts import Source


def fold(text: str) -> str:
    """Chữ thường, bỏ dấu tiếng Việt: 'Điểm chuẩn' -> 'diem chuan'."""
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", fold(text))
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]  # cặp âm tiết giữ được từ ghép: "ke_toan", "hoc_phi"


def rank(query: str, sources: list[Source], k1: float = 1.5, b: float = 0.75) -> list[Source]:
    """Nguồn xếp từ liên quan nhất; tiêu đề được tính gấp đôi. Thứ tự gốc giữ nguyên khi điểm bằng nhau."""
    if not sources:
        return []
    docs = [Counter(tokens(s.title) * 2 + tokens(s.text)) for s in sources]
    lengths = [sum(d.values()) for d in docs]
    avg = sum(lengths) / len(lengths) or 1
    df = Counter(t for d in docs for t in d)
    q = set(tokens(query))
    n = len(docs)

    def score(i: int) -> float:
        d, total = docs[i], 0.0
        for t in q & d.keys():
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            total += idf * d[t] * (k1 + 1) / (d[t] + k1 * (1 - b + b * lengths[i] / avg))
        return total
    order = sorted(range(n), key=lambda i: -score(i))
    return [sources[i] for i in order]


def within_budget(query: str, sources: list[Source], max_chars: int) -> list[Source]:
    """Giữ các nguồn liên quan nhất cho tới khi hết ngân sách ký tự; luôn giữ ít nhất một nguồn."""
    if sum(len(s.text) for s in sources) <= max_chars:
        return sources
    kept, used = [], 0
    for s in rank(query, sources):
        if kept and used + len(s.text) > max_chars:
            continue
        kept.append(s)
        used += len(s.text)
    return kept
