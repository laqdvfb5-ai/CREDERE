"""AI Tuyển sinh: chọn nguồn theo mức liên quan, giới hạn tác tử, nạp kho nguồn và trang demo (model giả lập, không gọi mạng)."""
import json

import pytest
from fastapi.testclient import TestClient

from app import workers
from app.contracts import Source, Task
from app.graph import run
from app.llm import FakeClient, LLMError
from app.retrieval import fold, rank, within_budget
from app.sources import load_sources
from app.web import create_app, question_key

DC_2026 = Source(source_id="TS-101", title="Điểm chuẩn đại học chính quy năm 2026",
                 text="Ngành Kế toán | Mã 7340301 | Điểm chuẩn 2026 (thi THPT): 18,50. Ngành Thú y | Mã 7640101 | 17,00.")
DC_2025 = Source(source_id="TS-100", title="Điểm chuẩn đại học chính quy năm 2025",
                 text="Ngành Kế toán | Mã 7340301 | Điểm chuẩn 2025 (thi THPT): 17,00.")
HOC_PHI = Source(source_id="TS-201", title="Học phí năm học 2026-2027", text="Nhóm ngành kinh tế: 450.000 đồng/tín chỉ.")
TS_SOURCES = [DC_2025, DC_2026, HOC_PHI]

PLAN = {"tasks": [
    {"task_id": "T1", "worker_type": "tuyen_sinh", "task_type": "tra_cuu_noi_bo", "goal": "Tra điểm chuẩn ngành Kế toán 2025 và 2026",
     "context": {"refs": ["TS-100", "TS-101"]}},
    {"task_id": "T2", "worker_type": "analysis", "task_type": "so_sanh", "goal": "Tính chênh lệch điểm chuẩn", "depends_on": ["T1"]},
]}
T1 = json.dumps({"data": {"2025": "17,00", "2026": "18,50"}, "claims": [
    {"text": "Điểm chuẩn Kế toán 2025 là 17,00", "source_id": "TS-100"}, {"text": "Điểm chuẩn Kế toán 2026 là 18,50", "source_id": "TS-101"}]})
ACCEPT = json.dumps({"accepted": True, "issues": [], "required_changes": []})


def handler(overrides=None):
    overrides = overrides or {}

    def h(role, messages, label):
        base = label.split("#")[0]
        if base in overrides:
            o = overrides[base]
            return o() if callable(o) else o
        return {"plan": json.dumps(PLAN, ensure_ascii=False), "worker:T1": T1,
                "worker:T2": json.dumps({"calculations": [{"name": "chenh_lech", "expression": "18.50 - 17.00", "unit": "điểm"}]}),
                "synthesize": "Điểm chuẩn Kế toán tăng từ 17,00 [TS-100] lên 18,50 [TS-101], tăng 1,5 điểm [T2]."}.get(base) or ACCEPT
    return h


def test_fold_and_rank_are_diacritic_insensitive():
    assert fold("Điểm chuẩn Học phí") == "diem chuan hoc phi"
    assert rank("học phí ngành kinh tế", TS_SOURCES)[0].source_id == "TS-201"
    assert rank("diem chuan 2026", TS_SOURCES)[0].source_id == "TS-101"


def test_budget_keeps_most_relevant_sources():
    kept = within_budget("học phí", TS_SOURCES, max_chars=len(HOC_PHI.text) + 5)
    assert [s.source_id for s in kept] == ["TS-201"]
    assert within_budget("x", TS_SOURCES, max_chars=10**6) == TS_SOURCES


def test_sources_for_applies_budget_to_large_corpora(monkeypatch):
    monkeypatch.setattr(workers, "SOURCE_BUDGET_CHARS", len(HOC_PHI.text) + 5)
    task = Task(task_id="T1", worker_type="tuyen_sinh", task_type="tra_cuu_noi_bo", goal="Học phí nhóm ngành kinh tế")
    assert [s.source_id for s in workers.sources_for(task, TS_SOURCES)] == ["TS-201"]


def test_admissions_run_uses_only_admissions_and_analysis_workers():
    llm = FakeClient(handler())
    state = run("Điểm chuẩn Kế toán 2026 tăng bao nhiêu so với 2025?", llm, TS_SOURCES, workers={"tuyen_sinh", "analysis"})
    plan_prompt = llm.transcript[0][2][0]["content"]
    assert "- tuyen_sinh:" in plan_prompt and "- nckh:" not in plan_prompt and "- dao_tao:" not in plan_prompt
    assert state["status"] == {"T1": "accepted", "T2": "accepted"}
    assert state["results"]["T2"]["data"]["calculations"][0]["value"] == "1.50"
    worker_system = next(m for _, lb, m in llm.transcript if lb.startswith("worker:T1"))[0]["content"]
    assert "Tuyển sinh" in worker_system and "năm, đợt và phương thức" in worker_system


def test_load_sources_maps_url_and_year_scope(tmp_path):
    p = tmp_path / "sources.json"
    p.write_text(json.dumps([{"source_id": "TS-001", "title": "Đề án tuyển sinh", "year_scope": "2026", "url": "https://nau.edu.vn/x",
                              "text": "Phương thức 1: xét điểm thi THPT."}], ensure_ascii=False), encoding="utf-8")
    [s] = load_sources(p)
    assert s.title == "Đề án tuyển sinh (2026)" and s.url_or_document_id == "https://nau.edu.vn/x" and s.access_scope == "public"
    p.write_text(json.dumps([{"source_id": "A", "title": "a", "text": "a"}] * 2), encoding="utf-8")
    with pytest.raises(ValueError, match="Trùng mã"):
        load_sources(p)


def sse_events(body: str) -> list[tuple[str, dict]]:
    out = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines() if not line.startswith(":"))
        if "event" in lines:
            out.append((lines["event"], json.loads(lines["data"])))
    return out


def test_web_streams_plan_progress_and_cited_answer(tmp_path):
    app = create_app(TS_SOURCES, client_factory=lambda: FakeClient(handler()), record_dir=tmp_path, samples=["Câu mẫu"])
    client = TestClient(app)
    assert client.get("/api/samples").json() == [{"kind": "", "q": "Câu mẫu"}]  # tệp cũ chỉ có câu hỏi: nhãn trống
    info = client.get("/api/info").json()
    assert info["data"] is False
    assert info["source_count"] == len({s.source_id for s in TS_SOURCES if s.access_scope == "public"})
    assert info["query_count"] == 0 and info["snapshot"] == ""
    assert client.get("/api/sources").json()["TS-101"]["title"].startswith("Điểm chuẩn")
    assert "AI Tuyển sinh" in client.get("/").text
    events = sse_events(client.get("/api/ask", params={"q": "Điểm chuẩn Kế toán tăng bao nhiêu?"}).text)
    kinds = [e["event_type"] for k, e in events if k == "event"]
    assert kinds[0] == "plan_saved" and "task_reviewed" in kinds
    done = events[-1]
    assert done[0] == "done" and "[TS-101]" in done[1]["report"] and "replayed" not in done[1]
    key = question_key("Điểm chuẩn Kế toán tăng bao nhiêu?")
    assert (tmp_path / done[1]["record"]).exists() and done[1]["record"].endswith(f"--{key}.json")
    second = sse_events(client.get("/api/ask", params={"q": "Điểm chuẩn Kế toán tăng bao nhiêu?"}).text)[-1][1]
    assert second["record"] != done[1]["record"] and len(list(tmp_path.glob(f"*--{key}.json"))) == 2  # không ghi đè lượt trước
    assert client.get("/api/replays").status_code == 404  # không còn chế độ phát lại


def test_gateway_failure_is_never_covered_by_an_old_record(tmp_path):
    q = "Điểm chuẩn Kế toán tăng bao nhiêu?"
    TestClient(create_app(TS_SOURCES, client_factory=lambda: FakeClient(handler()), record_dir=tmp_path)).get("/api/ask", params={"q": q})

    def down():
        raise LLMError("gpt-6-sol: HTTP 502")
    broken = create_app(TS_SOURCES, client_factory=lambda: FakeClient(handler({"plan": down})), record_dir=tmp_path)
    events = sse_events(TestClient(broken).get("/api/ask", params={"q": q, "mode": "replay"}).text)
    assert not [k for k, _ in events if k == "replay"]
    assert events[-1][0] == "done" and "Không lập được kế hoạch" in events[-1][1]["report"]
    assert "[TS-101]" not in events[-1][1]["report"] and len(list(tmp_path.iterdir())) == 1  # lượt lỗi không thành hồ sơ


def test_web_reports_failure_honestly_without_recording(tmp_path):
    def down():
        raise LLMError("gpt-6-sol: HTTP 502")
    app = create_app(TS_SOURCES, client_factory=lambda: FakeClient(handler({"plan": down})), record_dir=tmp_path)
    events = sse_events(TestClient(app).get("/api/ask", params={"q": "Câu chưa có bản ghi"}).text)
    assert events[-1][0] == "done" and "record" not in events[-1][1]
    assert "Không lập được kế hoạch" in events[-1][1]["report"]
    assert not list(tmp_path.iterdir())


def test_multi_id_brackets_and_hint_ids_are_accepted_by_report_check():
    from app.graph import cited_ids
    assert cited_ids("x [TS-100, TS-101] y [T2; TS-312]") == {"TS-100", "TS-101", "T2", "TS-312"}
    llm = FakeClient(handler({"synthesize": "Tăng 1,5 điểm [TS-100, TS-101] [T2]. Liên hệ 0975 313 755 [TS-312]."}))
    state = run("Điểm chuẩn Kế toán?", llm, TS_SOURCES, workers={"tuyen_sinh", "analysis"},
                synth_hint="Thiếu thông tin thì mời gọi 0975 313 755 [TS-312].")
    check = next(e for e in state["events"] if e["event_type"] == "report_checked")
    assert check["detail"] == {"ok": True, "unknown_ids": []}
    assert "0975 313 755 [TS-312]" in next(m for _, lb, m in llm.transcript if lb == "synthesize")[0]["content"]


def test_plan_hint_reaches_the_planner():
    llm = FakeClient(handler())
    run("Điểm chuẩn 2027?", llm, TS_SOURCES, workers={"tuyen_sinh", "analysis"}, plan_hint="CHI_KIEM_TRA_NAM_DUOC_HOI")
    assert llm.transcript[0][2][0]["content"].endswith("CHI_KIEM_TRA_NAM_DUOC_HOI")


def test_worker_fields_outside_data_are_regrouped_not_rejected():
    from app.workers import _split_result
    top = {"diem_trung_tuyen": [{"nganh": "Kế toán", "diem": 16}], "claims": [{"text": "16", "source_id": "TS-101"}]}
    assert _split_result(top) == ({"diem_trung_tuyen": [{"nganh": "Kế toán", "diem": 16}]}, top["claims"], [])
    inside = {"data": {"diem": 16, "claims": [{"text": "16", "source_id": "TS-101"}], "assumptions": ["x"]}}
    assert _split_result(inside) == ({"diem": 16}, [{"text": "16", "source_id": "TS-101"}], ["x"])
    assert _split_result({"data": 7})[0] == {}  # kiểu sai vẫn bị kiểm tra tự động từ chối như trước
    llm = FakeClient(handler({"worker:T1": json.dumps({"diem_2025": "17,00", "diem_2026": "18,50", "claims": json.loads(T1)["claims"]})}))
    state = run("Điểm chuẩn Kế toán 2026 tăng bao nhiêu?", llm, TS_SOURCES, workers={"tuyen_sinh", "analysis"})
    assert state["attempts"]["T1"] == 1 and state["status"]["T1"] == "accepted"


def test_version_note_marks_updated_documents(tmp_path):
    p = tmp_path / "sources.json"
    p.write_text(json.dumps([
        {"source_id": "TS-202", "title": "Chỉ tiêu 2026", "year_scope": "2026", "text": "Kế toán 450.", "updated_by": ["TS-306"],
         "version_note": "Thông báo 679/TB-ĐHNA ngày 04/6/2026 (TS-306) cập nhật chỉ tiêu."},
        {"source_id": "TS-306", "title": "Thông báo 679/TB-ĐHNA", "text": "Tổng 2.356."}], ensure_ascii=False), encoding="utf-8")
    old, new = load_sources(p)
    assert "[đã có văn bản cập nhật: TS-306]" in old.title and old.text.startswith("LƯU Ý PHIÊN BẢN: Thông báo 679/TB-ĐHNA")
    assert new.title == "Thông báo 679/TB-ĐHNA" and new.text == "Tổng 2.356."
    llm = FakeClient(handler())
    run("Chỉ tiêu 2026?", llm, [old, new], workers={"tuyen_sinh", "analysis"})
    assert "đưa cả mã văn bản cập nhật vào context.refs" in llm.transcript[0][2][0]["content"]
