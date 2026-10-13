"""Kiểm tra kế hoạch của tác tử điều phối trước khi thực thi (FR1)."""
from .config import Limits
from .contracts import Plan

# Loại nhiệm vụ mỗi tác tử thực thi được nhận. Tổng hợp báo cáo cuối do tác tử điều phối làm, không nằm trong kế hoạch.
ROLES = {
    "nckh": {"tra_cuu_noi_bo", "trich_bang_chung", "soan_thao"},
    "dao_tao": {"tra_cuu_noi_bo", "trich_bang_chung", "soan_thao"},
    "htqt": {"tra_cuu_noi_bo", "trich_bang_chung", "soan_thao"},
    "tuyen_sinh": {"tra_cuu_noi_bo", "trich_bang_chung", "soan_thao"},
    "search": {"tim_nguon", "trich_bang_chung"},
    "analysis": {"tinh_toan", "so_sanh"},
    "du_lieu": {"truy_van_du_lieu"},  # chỉ có khi lượt chạy được nối cơ sở dữ liệu
}
DOMAIN = {"nckh", "dao_tao", "htqt", "tuyen_sinh"}
# Tác tử không phải dẫn nguồn vì chỉ tính trên kết quả đã nghiệm thu. Tác tử thêm sau mặc định phải dẫn nguồn.
UNGROUNDED = {"analysis"}


def validate_plan(plan: Plan, limits: Limits, available: set[str] | None = None, source_ids: set[str] | None = None,
                  roles: dict[str, set[str]] | None = None) -> list[str]:
    """available: tác tử chạy được trong lượt này; source_ids: mã nguồn người dùng được phép dùng. None nghĩa là không kiểm tra.
    roles: tác tử và loại nhiệm vụ của lượt chạy (thêm AI con); mặc định ROLES."""
    roles = roles or ROLES
    errors = []
    tasks = plan.tasks
    if not tasks:
        return ["Kế hoạch không có nhiệm vụ nào."]
    if len(tasks) > limits.max_tasks:
        errors.append(f"Kế hoạch có {len(tasks)} nhiệm vụ, vượt giới hạn {limits.max_tasks}.")
    ids = [t.task_id for t in tasks]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"Trùng mã nhiệm vụ: {', '.join(duplicates)}.")
    known = set(ids)
    for t in tasks:
        if available is not None and t.worker_type not in available:
            errors.append(f"{t.task_id}: tác tử {t.worker_type} không có trong lượt chạy này.")
        elif t.worker_type not in roles:
            errors.append(f"{t.task_id}: không có tác tử {t.worker_type}.")
        elif t.task_type not in roles[t.worker_type]:
            errors.append(f"{t.task_id}: tác tử {t.worker_type} không được nhận loại nhiệm vụ {t.task_type}.")
        for d in t.depends_on:
            if d not in known:
                errors.append(f"{t.task_id}: phụ thuộc vào nhiệm vụ không tồn tại {d}.")
            elif d == t.task_id:
                errors.append(f"{t.task_id}: tự phụ thuộc vào chính nó.")
        if t.max_helper_calls < 0 or (t.max_helper_calls and not t.allowed_helpers):
            errors.append(f"{t.task_id}: max_helper_calls không khớp với allowed_helpers.")
        if t.worker_type in UNGROUNDED and not t.depends_on:  # tác tử phân tích không đọc tài liệu, chỉ tính trên kết quả nhiệm vụ trước
            errors.append(f"{t.task_id}: tác tử {t.worker_type} không đọc tài liệu nên phải phụ thuộc nhiệm vụ lấy số liệu; "
                          "việc tra cứu, đối chiếu văn bản giao cho tác tử chuyên môn.")
        if source_ids is not None:
            bad = [r for r in t.context.refs if r not in source_ids]
            if bad:
                errors.append(f"{t.task_id}: context.refs có mã nguồn không tồn tại hoặc không được phép dùng: {', '.join(bad)}.")
            if t.worker_type in DOMAIN and not t.context.refs and not source_ids and not t.depends_on:
                errors.append(f"{t.task_id}: tác tử chuyên môn không có nguồn nào để dẫn và không dựa vào nhiệm vụ nào.")
    if not errors and has_cycle(plan):
        errors.append("Kế hoạch có vòng phụ thuộc.")
    return errors


def has_cycle(plan: Plan) -> bool:
    indegree = {t.task_id: len(set(t.depends_on)) for t in plan.tasks}
    children = {t.task_id: [] for t in plan.tasks}
    for t in plan.tasks:
        for d in set(t.depends_on):
            children.setdefault(d, []).append(t.task_id)
    queue = [i for i, n in indegree.items() if n == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for c in children.get(node, []):
            indegree[c] -= 1
            if indegree[c] == 0:
                queue.append(c)
    return visited != len(indegree)
