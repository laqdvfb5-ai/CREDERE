"""Mô hình chủ – tớ: AI Tổng hợp giao việc cho AI Tuyển sinh và AI Đào tạo, nhận báo cáo, ghép số liệu (model giả lập)."""
import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.apps import AppRuntime, SubAgent
from app.config import Limits
from app.contracts import Source
from app.domains import dao_tao, tuyen_sinh
from app.llm import FakeClient, LLMError
from app.web import create_app

ACCEPT = json.dumps({"accepted": True, "issues": [], "required_changes": []})
SCRIPTS = Path(__file__).parents[1] / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def stores(tmp_path_factory):
    d = tmp_path_factory.mktemp("hai_linh_vuc")
    ts_path, dt_path = d / "ts.sqlite", d / "dt.sqlite"
    load("make_gia_lap").build(ts_path, scale=0.15)
    gen = load("make_gia_lap_dao_tao")
    gen.TS_DB = ts_path  # sĩ số khóa K11, K12 lấy từ dữ liệu tuyển sinh của chính bài kiểm thử
    gen.build(dt_path, scale=0.1)
    return tuyen_sinh.open_store(ts_path), dao_tao.open_store(dt_path)


def test_academic_totals_match_the_overview(stores):
    dt = stores[1]
    for q in dt.queries:
        if q.tong:
            assert set(q.tong) <= set(dt.run(q.name).columns), q.name
    r = dt.run("tong_quan_hoc_vu")
    overview = dict(zip(r.columns, r.rows[0]))
    si_so = dt.run("si_so_theo_nganh_khoa").for_model()["tong_cac_dong"]
    assert (si_so["dang_hoc"], si_so["bao_luu"], si_so["thoi_hoc"] + si_so["buoc_thoi_hoc"]) == (
        overview["dang_hoc"], overview["bao_luu"], overview["roi_truong"])
    canh_bao = dt.run("canh_bao_hoc_vu_theo_nganh").for_model()["tong_cac_dong"]
    assert canh_bao["canh_bao_muc_1"] + canh_bao["canh_bao_muc_2"] == overview["canh_bao_hk2"]
    assert dt.run("lop_hoc_phan_tong_hop").for_model()["tong_cac_dong"]["so_lop"] == overview["so_lop_hoc_phan_hk2"]


def child(kind: str, query: str, report: str):
    """Model giả lập của một AI con: một nhiệm vụ du_lieu, một truy vấn, nghiệm thu đạt, báo cáo có mã nhiệm vụ nội bộ [T1]."""
    plan = {"tasks": [{"task_id": "T1", "worker_type": "du_lieu", "task_type": "truy_van_du_lieu", "goal": f"Lấy số liệu {kind}"}]}

    def h(role, messages, label):
        k = label.split(":")[0]
        if k in ("plan", "plan_repair"):
            return json.dumps(plan)
        if k == "worker":
            return json.dumps({"queries": [{"name": query, "params": {}}]})
        if k.startswith("review"):
            return ACCEPT
        if k.startswith("synthesize"):
            return report
        raise AssertionError(label)
    return h


PRINCIPAL_PLAN = {"tasks": [
    {"task_id": "T1", "worker_type": "ai_tuyen_sinh", "task_type": "giao_viec", "goal": "Số đã xác nhận nhập học và chỉ tiêu còn lại theo ngành"},
    {"task_id": "T2", "worker_type": "ai_dao_tao", "task_type": "giao_viec", "goal": "Tỷ lệ cảnh báo, rời trường theo ngành các khóa trước"},
    {"task_id": "T3", "worker_type": "analysis", "task_type": "so_sanh", "goal": "Ghép hai bảng theo ngành", "depends_on": ["T1", "T2"]}]}


def principal(plan=PRINCIPAL_PLAN, synth="Kế toán thiếu nhiều nhất [CSDL-TS]; tỷ lệ rời trường [CSDL-DT]; ghép [T3]; báo cáo [T1]."):
    seen = []

    def h(role, messages, label):
        seen.append((label, messages[-1]["content"]))
        k = label.split(":")[0]
        if k in ("plan", "plan_repair"):
            return json.dumps(plan)
        if k.startswith("review"):
            return ACCEPT
        if k == "worker":
            return json.dumps({"calculations": [{"name": "chenh", "expression": "265 - 100", "unit": "chỉ tiêu"}]})
        if k.startswith("synthesize"):
            return synth
        raise AssertionError(label)
    h.seen = seen
    return h


def apps_for(stores, principal_handler, ts_handler=None, dt_handler=None, principal_limits=Limits(max_llm_calls=90)):
    ts, dt = stores
    w_ts, s_ts, p_ts = tuyen_sinh.app_config(ts)
    w_dt, s_dt, p_dt = dao_tao.app_config(dt)
    apps = {"tuyen_sinh": AppRuntime("tuyen_sinh", "AI Tuyển sinh", "TT Tuyển sinh", "cán bộ", "tuyển sinh", [], ts, w_ts, s_ts, p_ts),
            "dao_tao": AppRuntime("dao_tao", "AI Đào tạo", "Phòng Quản lý đào tạo", "cán bộ", "đào tạo", [], dt, w_dt, s_dt, p_dt),
            "hieu_truong": AppRuntime("hieu_truong", "AI Tổng hợp", "Ban Giám hiệu", "Hiệu trưởng", "điều phối", [], None, {"analysis"},
                                      "", "", [], principal_limits, delegates=["tuyen_sinh", "dao_tao"])}
    handlers = {"tuyen_sinh": ts_handler or child("tuyển sinh", "xac_nhan_theo_nganh", "Kế toán còn 265 chỉ tiêu [CSDL-TS] [T1]."),
                "dao_tao": dt_handler or child("học vụ", "si_so_theo_nganh_khoa", "Kế toán rời trường 5,1% [CSDL-DT; T1].")}
    subs = {f"ai_{k}": SubAgent(apps[k], lambda k=k: FakeClient(handlers[k])) for k in ("tuyen_sinh", "dao_tao")}
    return apps, subs


def test_principal_delegates_to_two_sub_ais_then_joins(stores):
    h = principal()
    apps, subs = apps_for(stores, h)
    llm, events = FakeClient(h), []
    state = apps["hieu_truong"].run("Ngành nào thiếu chỉ tiêu và học tập ra sao?", llm, events.append, subs)
    assert state["status"] == {"T1": "accepted", "T2": "accepted", "T3": "accepted"}
    t1, t2 = state["results"]["T1"], state["results"]["T2"]
    assert t1["data"]["ai_con"] == "AI Tuyển sinh" and "[T1]" not in t1["data"]["bao_cao"] and "[CSDL-TS]" in t1["data"]["bao_cao"]
    # AI con gửi thẳng kết quả đã nghiệm thu (code ghép, kèm nguồn), không gọi model viết báo cáo văn
    assert t2["data"]["bao_cao"].startswith("Các kết quả đã nghiệm thu") and "[CSDL-DT]" in t2["data"]["bao_cao"]
    assert {c["source_id"] for c in t1["claims"]} == {"CSDL-TS"} and {c["source_id"] for c in t2["claims"]} == {"CSDL-DT"}
    # lời gọi của AI con được chép vào sổ của AI Tổng hợp, tính vào nhiệm vụ đã giao
    sub_calls = [c for c in llm.ledger.calls if c.label.startswith("sub:")]
    assert {c.label.split("/")[1] for c in sub_calls} == {"tuyen_sinh", "dao_tao"} and state["usage"]["calls"] == len(llm.ledger.calls)
    assert not [c for c in sub_calls if "/synthesize" in c.label]
    # AI con đã nghiệm thu đủ mọi nhiệm vụ: AI Tổng hợp kiểm bằng code, không gọi model nghiệm thu lại
    assert not [c for c in llm.ledger.calls if c.label.startswith(("review:T1", "review:T2"))]
    assert t1["usage"]["calls"] == sum(1 for c in sub_calls if c.label.startswith("sub:T1#")) + 0
    # tiến độ bên trong AI con đi ra ngoài ngay (sub_event), có kế hoạch riêng của AI con
    inner = [e for e in events if e["event_type"] == "sub_event"]
    assert {e["detail"]["app"] for e in inner} == {"tuyen_sinh", "dao_tao"}
    assert any(e["detail"]["event"]["event_type"] == "plan_saved" for e in inner)
    assert next(e for e in state["events"] if e["event_type"] == "report_checked")["detail"]["ok"]
    # AI Tổng hợp được giới thiệu các AI con khi lập kế hoạch; phân tích nhận báo cáo của cả hai
    plan_prompt = next(m for label, m in h.seen if label == "plan")
    worker_prompt = next(m for label, m in h.seen if label.startswith("worker:T3"))
    assert "CSDL-TS" in worker_prompt and "CSDL-DT" in worker_prompt
    assert plan_prompt  # nội dung yêu cầu; phần mô tả AI con nằm ở system prompt


def test_sub_ai_description_reaches_the_principal_planner(stores):
    h = principal()
    apps, subs = apps_for(stores, h)
    llm = FakeClient(h)
    apps["hieu_truong"].run("Câu hỏi", llm, None, subs)
    system = next(m for _, label, m in llm.transcript if label == "plan")[0]["content"]
    assert "ai_tuyen_sinh: giao_viec" in system and "AI Đào tạo (Phòng Quản lý đào tạo" in system and "Cơ sở dữ liệu học vụ" in system


def test_budget_check_counts_a_whole_sub_ai_run(stores):
    h = principal()
    apps, subs = apps_for(stores, h, principal_limits=Limits(max_llm_calls=20))  # một AI con có thể dùng 24 lời gọi: không đủ chỗ
    state = apps["hieu_truong"].run("Câu hỏi", FakeClient(h), None, subs)
    assert state["status"]["T1"] == "budget_exceeded" and not [c for c in state.get("history", [])]


def test_failing_sub_ai_only_fails_its_task(stores):
    def broken(role, messages, label):
        raise LLMError("cổng lỗi")
    plan = {"tasks": PRINCIPAL_PLAN["tasks"][:2]}
    h = principal(plan=plan, synth="Chỉ có số tuyển sinh [CSDL-TS].")
    apps, subs = apps_for(stores, h, dt_handler=broken, principal_limits=Limits(max_llm_calls=90, max_revisions=0))
    state = apps["hieu_truong"].run("Câu hỏi", FakeClient(h), None, subs)
    assert state["status"]["T1"] == "accepted" and state["status"]["T2"] == "failed"
    assert state["report"].startswith("Chỉ có số tuyển sinh")


def test_web_lists_apps_and_streams_sub_events(stores, tmp_path):
    h = principal()
    apps, _ = apps_for(stores, h)
    shared = Source(source_id="CHUNG", title="Văn bản chung", text="Nội dung chung")
    for key, source_id in (("tuyen_sinh", "TS-VB"), ("dao_tao", "DT-VB")):
        apps[key].sources = [shared, Source(source_id=source_id, title="Văn bản", text="Nội dung"),
                             Source(source_id=f"{source_id}-NOI-BO", title="Nội bộ", text="Nội bộ", access_scope="internal")]
    handlers = {"hieu_truong": h, "tuyen_sinh": child("tuyển sinh", "xac_nhan_theo_nganh", "Kế toán còn 265 [CSDL-TS]."),
                "dao_tao": child("học vụ", "si_so_theo_nganh_khoa", "Rời trường [CSDL-DT].")}
    order = ["hieu_truong", "tuyen_sinh", "dao_tao"]  # client tạo theo thứ tự: AI Tổng hợp trước, rồi từng AI con khi được giao việc
    client = TestClient(create_app(apps=apps, client_factory=lambda: FakeClient(handlers[order.pop(0)]), record_dir=tmp_path))
    listed = client.get("/api/apps").json()
    assert [a["key"] for a in listed] == ["tuyen_sinh", "dao_tao", "hieu_truong"]
    assert listed[2]["delegates"] == [{"key": "tuyen_sinh", "ten": "AI Tuyển sinh"}, {"key": "dao_tao", "ten": "AI Đào tạo"}]
    assert listed[2]["synthetic"] and {"CSDL-TS", "CSDL-DT"} <= set(client.get("/api/sources").json())
    assert [a["source_count"] for a in listed] == [2, 2, 3]  # nguồn chung chỉ đếm một lần; không đếm nguồn nội bộ
    assert [a["query_count"] for a in listed] == [len(stores[0].catalog), len(stores[1].catalog),
                                                 sum(len(store.catalog) for store in stores)]
    assert listed[0]["snapshot"] == stores[0].snapshot
    assert listed[2]["snapshot"] == " · ".join(dict.fromkeys(store.snapshot for store in stores if store.snapshot))
    assert client.get("/api/info", params={"app": "hieu_truong"}).json() == listed[2]
    assert client.get("/api/info", params={"app": "khong-co"}).status_code == 404
    body = client.get("/api/ask", params={"q": "Ngành nào thiếu chỉ tiêu?", "app": "hieu_truong"}).text
    assert '"event_type": "sub_event"' in body and "event: done" in body
    assert len(list(tmp_path.glob("hieu_truong--*--nganh-nao-thieu-chi-tieu.json"))) == 1  # hồ sơ lượt chạy
