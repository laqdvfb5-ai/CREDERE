"""Các AI trong hệ thống: AI con theo lĩnh vực (Tuyển sinh, Đào tạo…) và AI Tổng hợp của Hiệu trưởng, giao việc cho các AI con.

Mô hình chủ – tớ: AI Tổng hợp không đọc tài liệu hay dữ liệu, chỉ lập kế hoạch và giao việc. Mỗi AI con nhận một yêu cầu con,
tự lập kế hoạch, giao việc cho tác tử của nó, nghiệm thu, rồi báo cáo lại. AI Tổng hợp nghiệm thu các báo cáo, ghép số liệu
(tác tử Phân tích) và trả lời Hiệu trưởng. Thêm một lĩnh vực: viết app/domains/<lĩnh vực>.py và khai báo trong build_apps().
"""
import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

from . import graph
from .config import DATA_ROOT, Limits
from .contracts import Source
from .domains import dao_tao, tuyen_sinh
from .llm import LLMClient
from .sources import load_sources
from .tools.data import DataStore

PRINCIPAL = "hieu_truong"
PRINCIPAL_PLAN = ("Người hỏi là Hiệu trưởng Trường Đại học Nghệ An. Bạn là AI Tổng hợp: không tự tra tài liệu hay dữ liệu mà giao việc cho "
                  "các AI con theo lĩnh vực. Câu thuộc một lĩnh vực thì giao một AI con. Câu cần nhiều lĩnh vực thì giao song song cho mỗi "
                  "AI con đúng phần của nó, nêu rõ đơn vị để ghép (theo ngành, mã ngành, khóa, năm); nếu cần so sánh, ghép số hay tính tỷ lệ "
                  "giữa các lĩnh vực thì thêm một nhiệm vụ analysis phụ thuộc các nhiệm vụ đó. Không giao việc ngoài lĩnh vực của các AI con; "
                  "phần chưa có AI con phụ trách thì ghi vào context.summary của nhiệm vụ gần nhất để báo cáo nói rõ. "
                  "Mục tiêu giao cho AI con viết gọn 1–2 câu: chỉ nêu số liệu cần, phạm vi (năm, học kỳ, khóa) và yêu cầu trả kèm mã ngành khi cần ghép "
                  "theo ngành; chỉ đòi mức chi tiết vừa đủ trả lời câu hỏi (toàn trường nếu câu hỏi hỏi toàn trường), không đòi chia nhỏ theo "
                  "nhiều chiều cùng lúc; dựa vào danh sách số liệu có sẵn của từng AI con; không đòi định nghĩa kỹ thuật; tiêu chí nghiệm thu tối đa 3 ý. "
                  "Khi một AI con cần số liệu của AI con khác để làm phần của mình (ví dụ AI Đào tạo cần số tân sinh viên do AI Tuyển sinh báo "
                  "để dự kiến số lớp), cho nhiệm vụ đó phụ thuộc (depends_on) nhiệm vụ lấy số liệu kia; AI con sẽ nhận kết quả đó kèm yêu cầu. "
                  "Việc mà danh sách số liệu của một AI con đã có sẵn cách làm trọn (ví dụ dự kiến số lớp cần mở của AI Đào tạo) thì giao "
                  "nguyên việc đó cho AI con, không xin đầu vào rời rạc (danh sách học phần, sĩ số) để tự tính lại bằng analysis.")
PRINCIPAL_SYNTH = ("Người đọc là Hiệu trưởng. Viết ngắn: kết luận trước (2–3 câu), rồi bảng số liệu chính theo ngành hoặc khóa, rồi rủi ro "
                   "và đề xuất nếu phù hợp. Mỗi số liệu dẫn mã nguồn có trong báo cáo của AI con (TS-…, DT-…, CSDL-TS, CSDL-DT); số do AI con "
                   "tính mà không có mã nguồn thì dẫn mã nhiệm vụ đã giao cho AI con đó, ví dụ [T1]; số do tác tử phân tích tính thì dẫn mã "
                   "nhiệm vụ đó. Nói rõ số liệu từ lĩnh vực nào; dữ liệu giả lập thì ghi rõ là giả lập. Không nêu tên, số điện thoại của "
                   "thí sinh, sinh viên. Phần AI con báo chưa có dữ liệu thì nói rõ, không tự suy.")


@dataclass
class AppRuntime:
    """Một AI dùng được trên trang: văn bản, dữ liệu, tác tử, chỉ dẫn, câu hỏi mẫu; AI Tổng hợp thêm danh sách AI con (delegates)."""
    key: str
    ten: str
    don_vi: str
    nguoi_dung: str
    linh_vuc: str
    sources: list[Source]
    data: DataStore | None = None
    workers: set[str] = field(default_factory=set)
    synth_hint: str = ""
    plan_hint: str = ""
    samples: list[dict] = field(default_factory=list)
    limits: Limits = field(default_factory=lambda: Limits(max_llm_calls=24))
    delegates: list[str] = field(default_factory=list)

    def run(self, request: str, llm: LLMClient, on_event=None, subagents: dict | None = None, extra_synth: str = "",
            limits: Limits | None = None, structured_report: bool = False) -> dict:
        subagents = subagents or {}
        return graph.run(request, llm, self.sources, None, limits or self.limits, on_event, set(self.workers) | set(subagents),
                         f"{self.synth_hint} {extra_synth}".strip(), self.plan_hint, self.data, subagents, structured_report)


@dataclass
class SubAgent:
    """AI con được AI Tổng hợp giao việc. Mỗi lần giao là một lượt chạy riêng với client riêng (sổ ghi lời gọi riêng)."""
    app: AppRuntime
    make_client: Callable[[], LLMClient]

    @property
    def key(self) -> str:
        return self.app.key

    @property
    def ten(self) -> str:
        return self.app.ten

    @property
    def call_budget(self) -> int:
        return self.app.limits.max_llm_calls

    def mo_ta(self) -> str:
        data = '; chưa nối dữ liệu, chỉ có văn bản'
        if self.app.data:
            data = (f"; dữ liệu: {self.app.data.title()}; số liệu có sẵn: "
                    + "; ".join(q.mo_ta for q in self.app.data.queries if not q.ca_nhan))
        return f"{self.app.ten} ({self.app.don_vi}, người dùng: {self.app.nguoi_dung}) phụ trách {self.app.linh_vuc}{data}."

    def run(self, request: str, emit, extra_synth: str) -> tuple[dict, list, str | None]:
        llm = None
        try:
            llm = self.make_client()
            # khi được giao việc, AI con chỉ sửa một lần: AI Tổng hợp còn nghiệm thu và có thể giao lại
            limits = replace(self.app.limits, max_revisions=min(1, self.app.limits.max_revisions))
            # báo cáo có cấu trúc: AI Tổng hợp tự viết câu trả lời cuối, AI con không viết thêm một bài văn
            state = self.app.run(request, llm, emit, extra_synth=extra_synth, limits=limits, structured_report=True)
            return state, list(llm.ledger.calls), None
        except Exception as e:  # lỗi của AI con chỉ làm hỏng nhiệm vụ được giao, không làm hỏng lượt chạy của AI Tổng hợp
            return {}, list(llm.ledger.calls) if llm else [], f"{type(e).__name__}: {e}"[:300]


def read_samples(*files: Path, data_mode: bool = False) -> list[dict]:
    """Câu hỏi mẫu: {"kind", "q"}; câu có "khi_chua_co_du_lieu" chỉ hiện khi chưa nối dữ liệu."""
    out = []
    for f in files:
        if f and f.exists():
            for s in json.loads(f.read_text(encoding="utf-8")):
                s = s if isinstance(s, dict) else {"kind": "", "q": s}
                if not (data_mode and s.get("khi_chua_co_du_lieu")):
                    out.append({"kind": s.get("kind", ""), "q": s["q"]})
    return out


def domain_app(module, sources: list[Source], data: DataStore | None, samples: list[dict]) -> AppRuntime:
    workers, synth, plan = module.app_config(data)
    return AppRuntime(module.KEY, module.TEN, module.DON_VI, module.NGUOI_DUNG, module.LINH_VUC, sources, data, workers, synth, plan, samples)


def build_apps(with_data: bool = True, root: Path = DATA_ROOT) -> dict[str, AppRuntime]:
    """Mọi AI có đủ tài liệu trên máy; AI Tổng hợp giao việc cho các AI con đó. Không có kho văn bản của lĩnh vực nào thì bỏ lĩnh vực đó."""
    apps = {}
    for module in (tuyen_sinh, dao_tao):
        if not module.DEFAULT_SOURCES.exists():
            continue
        data = module.open_store(module.DEFAULT_DATA) if with_data and module.DEFAULT_DATA.exists() else None
        samples = read_samples(module.DEFAULT_SOURCES.with_name("demo_questions.json"),
                               module.DEFAULT_DATA.with_name("demo_questions.json") if data else None, data_mode=bool(data))
        apps[module.KEY] = domain_app(module, load_sources(module.DEFAULT_SOURCES), data, samples)
    if len(apps) >= 2:
        apps[PRINCIPAL] = AppRuntime(
            PRINCIPAL, "AI Tổng hợp", "Ban Giám hiệu", "Hiệu trưởng", "điều phối các AI con", [], None, {"analysis"},
            PRINCIPAL_SYNTH, PRINCIPAL_PLAN, read_samples(root / "03_xu-ly" / "tong_hop" / "demo_questions.json"),
            Limits(max_tasks=6, max_llm_calls=90, max_cost_usd=1.5, max_revisions=1), delegates=list(apps))
    return apps
