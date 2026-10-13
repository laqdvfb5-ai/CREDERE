from app.config import Limits
from app.contracts import Plan
from app.planning import validate_plan


def plan(*tasks):
    return Plan.model_validate({"tasks": [
        {"task_id": i, "worker_type": w, "task_type": t, "goal": "g", "depends_on": d, **extra}
        for i, w, t, d, *rest in tasks for extra in [rest[0] if rest else {}]]})


def test_valid_plan_has_no_errors():
    p = plan(("T1", "nckh", "tra_cuu_noi_bo", []), ("T2", "search", "tim_nguon", []), ("T3", "analysis", "tinh_toan", ["T1", "T2"]))
    assert validate_plan(p, Limits()) == []


def test_detects_cycle():
    p = plan(("T1", "nckh", "tra_cuu_noi_bo", ["T2"]), ("T2", "analysis", "so_sanh", ["T1"]))
    assert any("vòng" in e for e in validate_plan(p, Limits()))


def test_detects_unknown_self_and_duplicate_dependencies():
    p = plan(("T1", "nckh", "tra_cuu_noi_bo", ["T9"]), ("T1", "htqt", "tra_cuu_noi_bo", []), ("T2", "search", "tim_nguon", ["T2"]))
    errors = " ".join(validate_plan(p, Limits()))
    assert "T9" in errors and "Trùng mã" in errors and "tự phụ thuộc" in errors


def test_role_matrix_is_enforced():
    p = plan(("T1", "search", "tinh_toan", []))
    assert any("không được nhận" in e for e in validate_plan(p, Limits()))


def test_task_limit_and_helper_consistency():
    many = plan(*[(f"T{i}", "nckh", "tra_cuu_noi_bo", []) for i in range(9)])
    assert any("vượt giới hạn" in e for e in validate_plan(many, Limits(max_tasks=8)))
    helper = plan(("T1", "nckh", "tra_cuu_noi_bo", [], {"max_helper_calls": 2}))
    assert any("allowed_helpers" in e for e in validate_plan(helper, Limits()))


def test_unavailable_worker_is_rejected():
    p = plan(("T1", "search", "tim_nguon", []))
    assert any("không có trong lượt chạy" in e for e in validate_plan(p, Limits(), available={"nckh", "analysis"}))
    assert validate_plan(p, Limits(), available={"search"}) == []


def test_refs_must_be_known_public_sources():
    p = plan(("T1", "nckh", "tra_cuu_noi_bo", [], {"context": {"refs": ["QĐ-620", "NB-1"]}}))
    errors = validate_plan(p, Limits(), source_ids={"QĐ-620"})
    assert len(errors) == 1 and "NB-1" in errors[0]


def test_domain_task_needs_something_to_cite():
    lonely = plan(("T1", "dao_tao", "tra_cuu_noi_bo", []))
    assert any("không có nguồn" in e for e in validate_plan(lonely, Limits(), source_ids=set()))
    assert validate_plan(lonely, Limits(), source_ids={"QĐ-620"}) == []


def test_task_id_format_is_enforced():
    import pytest
    from pydantic import ValidationError
    for bad in ("T:1", "T#1", "", "x" * 33):
        with pytest.raises(ValidationError):
            plan((bad, "nckh", "tra_cuu_noi_bo", []))


def test_analysis_task_must_depend_on_a_lookup_task():
    alone = plan(("T1", "analysis", "so_sanh", []))
    assert any("không đọc tài liệu" in e for e in validate_plan(alone, Limits()))
    chained = plan(("T1", "tuyen_sinh", "tra_cuu_noi_bo", []), ("T2", "analysis", "so_sanh", ["T1"]))
    assert validate_plan(chained, Limits()) == []
