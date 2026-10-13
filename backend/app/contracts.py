"""Hợp đồng dữ liệu FR2. Chỉ thị có task_id, goal, context, constraints; phản hồi có task_id, status, data, error."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field

# Tác tử cơ bản: nckh, dao_tao, htqt, tuyen_sinh, search, analysis, du_lieu; AI con được giao việc có tên ai_<lĩnh vực>.
# Không liệt kê cứng để thêm AI con không phải sửa lõi (NFR1); validate_plan kiểm tra tác tử có trong lượt chạy.
WorkerType = Annotated[str, Field(pattern=r"^[a-z][a-z_]{1,31}$")]
TaskType = Literal["tra_cuu_noi_bo", "tim_nguon", "trich_bang_chung", "tinh_toan", "so_sanh", "soan_thao", "truy_van_du_lieu", "giao_viec"]
TaskStatus = Literal["pending", "revise", "accepted", "failed", "blocked", "budget_exceeded"]


class TaskContext(BaseModel):
    refs: list[str] = Field(default_factory=list)  # mã nguồn được phép dùng, không sao chép toàn văn
    summary: str = ""


class Task(BaseModel):
    task_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,32}$")  # không chứa ':' hay '#' vì nhãn lời gọi dùng hai ký tự này
    worker_type: WorkerType
    task_type: TaskType
    goal: str
    context: TaskContext = Field(default_factory=TaskContext)
    constraints: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    allowed_helpers: list[Literal["search", "analysis"]] = Field(default_factory=list)  # chưa dùng: Worker hỗ trợ làm ở M2
    max_helper_calls: int = 0
    acceptance_criteria: list[str] = Field(default_factory=list)


class Plan(BaseModel):
    tasks: list[Task]


class Source(BaseModel):
    source_id: str
    title: str
    text: str
    url_or_document_id: str = ""
    access_scope: Literal["public", "internal", "restricted"] = "public"


class Claim(BaseModel):
    text: str
    source_id: str | None = None


class Usage(BaseModel):
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class WorkerResult(BaseModel):
    task_id: str
    status: Literal["ok", "error"]
    data: dict = Field(default_factory=dict)
    claims: list[Claim] = Field(default_factory=list)
    error: str | None = None
    usage: Usage = Field(default_factory=Usage)
    assumptions: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)  # nguồn do công cụ tạo ra; chỉ code điền, không lấy từ câu trả lời của model
    # danh sách từng thí sinh của tác tử Dữ liệu: chỉ đưa lên màn hình cán bộ; exclude để không lọt vào state, lịch sử hay prompt
    tables: list[dict] = Field(default_factory=list, exclude=True)


class Review(BaseModel):
    task_id: str
    accepted: bool
    checks: dict[str, bool] = Field(default_factory=dict)
    feedback: str = ""
    required_changes: list[str] = Field(default_factory=list)
    reviewer_error: str | None = None  # bước nghiệm thu không chạy được (lỗi cổng, câu trả lời hỏng); không phải lỗi của Worker
