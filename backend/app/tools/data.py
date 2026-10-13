"""Công cụ của tác tử Dữ liệu: đọc cơ sở dữ liệu của một lĩnh vực (tuyển sinh, học vụ…) bằng truy vấn đã duyệt, không để model tự viết SQL.

Mỗi lĩnh vực có danh mục truy vấn riêng (app/domains/*_queries.py) và mã nguồn riêng (CSDL-TS, CSDL-DT…).

Nguyên tắc (NGHIEN_CUU_NGUOI_DUNG_TUYEN_SINH.md, mục 6):
- Chỉ đọc: mở SQLite ở chế độ read-only; SQL cố định trong mã, model chỉ chọn tên truy vấn và tham số đã kiểm tra.
- Phép đếm, phép tính do cơ sở dữ liệu làm; kết quả ghi thời điểm dữ liệu.
- Truy vấn trả danh sách từng người (ca_nhan=True): model chỉ nhận số lượng và bảng tổng hợp; danh sách chi tiết
  đi thẳng tới màn hình của cán bộ (sự kiện data_table), không vào lời gọi model nào.
"""
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..retrieval import fold

MAX_ROWS_TO_MODEL = 120
MAX_ROWS_TO_SCREEN = 1000
GAP_COLUMNS = ("sdt", "email", "ma_can_bo_tu_van", "ma_co_van")  # cột mà danh sách cần có để liên hệ, phân công
PERSON_IDS = ("ma_sv", "ma_ts")  # cột định danh một người trong danh sách
METHODS = {"100", "200", "301", "402", "405"}


class DataError(ValueError):
    """Tên truy vấn hoặc tham số không hợp lệ; thông báo đủ rõ để model sửa ở lần sau."""


@dataclass(frozen=True)
class Param:
    name: str
    kind: str  # "nganh" | "phuong_thuc" | "float" | "int" | "choice"
    mo_ta: str
    required: bool = False
    lo: float | None = None
    hi: float | None = None
    default: object = None             # giá trị khi model bỏ trống
    choices: tuple[str, ...] = ()      # với kind "choice": các giá trị hợp lệ


@dataclass(frozen=True)
class Query:
    name: str
    mo_ta: str
    sql: str = ""
    params: tuple[Param, ...] = ()
    ca_nhan: bool = False              # trả danh sách từng người: chỉ hiện cho cán bộ
    group_by: tuple[str, ...] = ()     # với truy vấn cá nhân: các cột dùng để đếm, gửi cho model thay cho danh sách
    compute: Callable | None = None    # truy vấn cần xử lý bằng Python (kịch bản điểm chuẩn)
    ghi_chu: str = ""
    tong: tuple[str, ...] = ()         # cột cộng được giữa các dòng: kết quả từ 2 dòng thì máy cộng sẵn, model không tự cộng


@dataclass
class QueryResult:
    query: Query
    params: dict
    columns: list[str]
    rows: list[list]
    summary: list[dict] = field(default_factory=list)
    total: dict = field(default_factory=dict)

    def for_model(self) -> dict:
        """Phần được gửi cho model: bảng tổng hợp; truy vấn cá nhân chỉ có số dòng và bảng đếm."""
        out = {"truy_van": self.query.name, "mo_ta": self.query.mo_ta, "tham_so": self.params}
        if self.query.ghi_chu:
            out["ghi_chu"] = self.query.ghi_chu
        if self.query.ca_nhan:
            out.update(so_dong=len(self.rows), tong_hop=self.summary,
                       danh_sach="Danh sách chi tiết hiển thị trực tiếp cho cán bộ trên màn hình, không gửi cho dịch vụ AI.")
            key = next((c for c in PERSON_IDS if c in self.columns), None)
            if key:  # một người có thể xuất hiện ở nhiều dòng (nhiều lớp, nhiều lỗi): đếm sẵn số người khác nhau
                out["so_nguoi_khac_nhau"] = len({r[self.columns.index(key)] for r in self.rows})
            gaps = {f"so_dong_thieu_{c}": sum(1 for r in self.rows if not r[self.columns.index(c)])
                    for c in GAP_COLUMNS if c in self.columns}  # để phân công liên hệ: ai thiếu số điện thoại, chưa có người phụ trách
            if gaps:
                out["kiem_tra_danh_sach"] = gaps
        else:
            out.update(cot=self.columns, dong=self.rows[:MAX_ROWS_TO_MODEL])
            if len(self.rows) > MAX_ROWS_TO_MODEL:
                out["bi_cat"] = f"chỉ gửi {MAX_ROWS_TO_MODEL}/{len(self.rows)} dòng"
            if self.total:  # tính trên mọi dòng, kể cả dòng bị cắt
                out["tong_cac_dong"] = self.total
        return out

    def for_screen(self) -> dict:
        label = ", ".join(f"{k} = {v}" for k, v in self.params.items() if v is not None)
        return {"title": self.query.mo_ta + (f" ({label})" if label else ""), "columns": self.columns,
                "rows": self.rows[:MAX_ROWS_TO_SCREEN], "total": len(self.rows)}




class DataStore:
    """Một cơ sở dữ liệu chỉ đọc cùng danh mục truy vấn của nó.
    source_id: mã dẫn nguồn trong câu trả lời; label: tên hiển thị ("tuyển sinh 2026"); person: người trong danh sách ("thí sinh").
    majors_sql: câu lấy (mã, tên) ngành, để model ghi ngành bằng tên cũng được."""

    def __init__(self, path: str | Path, queries: list[Query], source_id: str, label: str, person: str = "người",
                 majors_sql: str = "SELECT ma_xet_tuyen, ten_nganh FROM nganh ORDER BY 1", methods: set[str] = frozenset(METHODS)):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self.queries = list(queries)
        self.catalog = {q.name: q for q in self.queries}
        self.source_id, self.label, self.person, self.methods = source_id, label, person, set(methods)
        self.count_key = "so_" + fold(person).replace(" ", "_")  # "so_thi_sinh", "so_sinh_vien"
        with self._connect() as conn:
            self.meta = dict(conn.execute("SELECT khoa, gia_tri FROM meta"))
            self.majors = dict(conn.execute(majors_sql))

    def _connect(self) -> sqlite3.Connection:
        # mỗi truy vấn một kết nối chỉ đọc: các nhiệm vụ chạy song song trên nhiều luồng
        return sqlite3.connect(f"file:{self.path.as_posix()}?mode=ro", uri=True)

    @property
    def snapshot(self) -> str:
        return self.meta.get("thoi_diem_du_lieu", "")

    @property
    def synthetic(self) -> bool:
        return "GIẢ LẬP" in self.meta.get("ghi_chu", "")

    def title(self) -> str:
        return f"Cơ sở dữ liệu {self.label}{' (GIẢ LẬP)' if self.synthetic else ''}, dữ liệu lúc {self.snapshot}"

    def catalog_text(self) -> str:
        lines = []
        for q in self.queries:
            ps = ", ".join(f"{p.name}{'' if p.required else '?'}: {p.mo_ta}" for p in q.params)
            lines.append(f"- {q.name}({ps}): {q.mo_ta}" + (f" [danh sách từng {self.person}: bạn chỉ nhận số lượng]" if q.ca_nhan else ""))
        majors = "; ".join(f"{k} {v}" for k, v in self.majors.items())
        return "\n".join(lines) + f"\n\nNGÀNH (mã, tên): {majors}"

    def _check(self, q: Query, params: dict) -> dict:
        params = dict(params or {})
        unknown = sorted(set(params) - {p.name for p in q.params})
        if unknown:
            raise DataError(f"Truy vấn {q.name} không có tham số {', '.join(unknown)}.")
        out = {}
        for p in q.params:
            v = params.get(p.name)
            if v in (None, ""):
                if p.required:
                    raise DataError(f"Truy vấn {q.name} cần tham số {p.name} ({p.mo_ta}).")
                out[p.name] = p.default
                continue
            if p.kind == "nganh":
                out[p.name] = self._major(str(v))
            elif p.kind == "phuong_thuc":
                code = "".join(ch for ch in str(v) if ch.isdigit())
                if code not in self.methods:
                    raise DataError(f"Phương thức {v!r} không hợp lệ; dùng một trong {', '.join(sorted(self.methods))}.")
                out[p.name] = code
            elif p.kind == "text":  # mã ngắn (mã giảng viên, mã lớp…): chỉ chữ, số, gạch
                value = str(v).strip().upper()
                if not value or len(value) > 24 or not all(ch.isalnum() or ch in "-_" for ch in value):
                    raise DataError(f"Tham số {p.name} = {v!r} không hợp lệ ({p.mo_ta}).")
                out[p.name] = value
            elif p.kind == "choice":
                value = str(v).strip()
                hit = next((c for c in p.choices if fold(c) == fold(value)), None)
                if hit is None:
                    raise DataError(f"Tham số {p.name} = {v!r} không hợp lệ; dùng một trong {', '.join(p.choices)}.")
                out[p.name] = hit
            else:
                try:
                    num = float(str(v).replace(",", ".")) if p.kind == "float" else int(v)
                except (TypeError, ValueError):
                    raise DataError(f"Tham số {p.name} phải là số, nhận {v!r}.") from None
                if (p.lo is not None and num < p.lo) or (p.hi is not None and num > p.hi):
                    raise DataError(f"Tham số {p.name} = {num} nằm ngoài khoảng {p.lo}–{p.hi}.")
                out[p.name] = num
        return out

    def _major(self, value: str) -> str:
        if value in self.majors:
            return value
        key = fold(value)
        hits = [ma for ma, ten in self.majors.items() if key and (key == fold(ten) or key in fold(ten))]
        if len(hits) == 1:
            return hits[0]
        raise DataError(f"Không có ngành {value!r}. Dùng mã ngành: " + "; ".join(f"{k} {v}" for k, v in self.majors.items()))

    def run(self, name: str, params: dict | None = None) -> QueryResult:
        q = self.catalog.get(name)
        if q is None:
            raise DataError(f"Không có truy vấn {name!r}. Chỉ dùng: {', '.join(self.catalog)}.")
        checked = self._check(q, params or {})
        with self._connect() as conn:
            if q.compute:
                columns, rows = q.compute(conn, checked)
            else:
                cur = conn.execute(q.sql, checked)
                columns = [d[0] for d in cur.description]
                rows = [list(r) for r in cur.fetchall()]
        summary = []
        if q.ca_nhan:
            idx = [columns.index(c) for c in q.group_by]
            counts = Counter(tuple(r[i] for i in idx) for r in rows)
            summary = [{**dict(zip(q.group_by, k)), self.count_key: n} for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))]
        total = {}
        if q.tong and len(rows) >= 2:
            total = {"so_dong": len(rows), **{c: sum(r[columns.index(c)] or 0 for r in rows) for c in q.tong}}
        return QueryResult(q, {k: v for k, v in checked.items() if v is not None}, columns, rows, summary, total)
