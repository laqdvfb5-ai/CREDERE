"""Tác tử Dữ liệu (giai đoạn 2) trên cơ sở dữ liệu giả lập nhỏ: truy vấn đã duyệt, chỉ đọc, danh sách cá nhân không tới model."""
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Limits
from app.contracts import Source
from app.graph import run
from app.llm import FakeClient
from app.domains.tuyen_sinh import open_store
from app.domains.tuyen_sinh_queries import QUERIES
from app.tools.data import DataError, DataStore
from app.web import create_app

SOURCES = [Source(source_id="TS-100", title="Điểm trúng tuyển 2026", text="Kế toán: 16 điểm (PT 100).")]
ACCEPT = json.dumps({"accepted": True, "issues": [], "required_changes": []})
REQUIRED = {"mo_phong_diem_chuan": {"ma_xet_tuyen": "7340301", "phuong_thuc": "100", "diem_chuan": 15}}


@pytest.fixture(scope="module")
def db_path(tmp_path_factory) -> Path:
    spec = importlib.util.spec_from_file_location("make_gia_lap", Path(__file__).parents[1] / "scripts" / "make_gia_lap.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    path = tmp_path_factory.mktemp("gia_lap") / "ts.sqlite"
    gen.build(path, scale=0.15)
    return path


@pytest.fixture(scope="module")
def store(db_path) -> DataStore:
    return open_store(db_path)


def personal_values(store: DataStore) -> set[str]:
    with sqlite3.connect(store.path) as conn:
        return {v for row in conn.execute("SELECT ho_ten, sdt, cccd FROM thi_sinh") for v in row}


# ---------- Công cụ ----------

def test_every_approved_query_runs(store):
    for q in QUERIES:
        r = store.run(q.name, REQUIRED.get(q.name, {}))
        assert r.columns and isinstance(r.rows, list), q.name
        assert set(q.tong) <= set(r.columns), q.name


def test_totals_are_added_by_the_machine_and_match_the_overview(store):
    """Model không tự cộng: truy vấn theo ngành gửi kèm tong_cac_dong, khớp với truy vấn tổng quan do SQL đếm riêng."""
    r = store.run("tong_quan")
    overview = dict(zip(r.columns, r.rows[0]))
    total = store.run("nhap_hoc_tong_hop").for_model()["tong_cac_dong"]
    assert total["da_lam_thu_tuc"] == overview["da_lam_thu_tuc_nhap_hoc"]
    assert total["so_dong"] == len(store.run("nhap_hoc_tong_hop").rows)
    xn = store.run("xac_nhan_theo_nganh").for_model()["tong_cac_dong"]
    assert (xn["trung_tuyen"], xn["da_xac_nhan"], xn["chi_tieu_chua_co_nguoi_xac_nhan"]) == (
        overview["trung_tuyen_dot_1"], overview["da_xac_nhan_nhap_hoc"], overview["chi_tieu_chua_co_nguoi_xac_nhan"])
    assert "tong_cac_dong" not in store.run("nhap_hoc_tong_hop", {"ma_xet_tuyen": "7340301"}).for_model()  # một dòng: không cần tổng


def test_personal_list_reaches_screen_but_not_model(store):
    r = store.run("danh_sach_chua_xac_nhan", {"ma_xet_tuyen": "7340301"})
    model = json.dumps(r.for_model(), ensure_ascii=False)
    assert r.rows and r.for_model()["so_dong"] == len(r.rows)
    assert sum(g["so_thi_sinh"] for g in r.for_model()["tong_hop"]) == len(r.rows)
    assert not any(v in model for v in personal_values(store))  # không họ tên, số điện thoại, CCCD nào
    assert "sdt" in r.for_screen()["columns"] and r.for_screen()["total"] == len(r.rows)
    assert r.for_model()["kiem_tra_danh_sach"] == {"so_dong_thieu_sdt": 0, "so_dong_thieu_ma_can_bo_tu_van": 0}
    assert r.for_model()["so_nguoi_khac_nhau"] == len({row[r.columns.index("ma_ts")] for row in r.rows})


def test_parameters_are_checked_and_majors_resolve_by_name(store):
    assert store.run("xac_nhan_theo_nganh", {"ma_xet_tuyen": "Kế toán"}).params == {"ma_xet_tuyen": "7340301"}
    assert store.run("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301", "phuong_thuc": "PT 100", "diem_chuan": "15,5"}).params["diem_chuan"] == 15.5
    for name, params in [("xoa_du_lieu", {}), ("xac_nhan_theo_nganh", {"nam": 2026}), ("xac_nhan_theo_nganh", {"ma_xet_tuyen": "Luật"}),
                         ("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301", "phuong_thuc": "999", "diem_chuan": 15}),
                         ("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301", "phuong_thuc": "100", "diem_chuan": 45}),
                         ("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301"})]:
        with pytest.raises(DataError):
            store.run(name, params)


def test_database_is_opened_read_only(store):
    with pytest.raises(sqlite3.OperationalError):
        store._connect().execute("DELETE FROM thi_sinh")


def test_cross_check_finds_every_planted_error(store):
    with sqlite3.connect(store.path) as conn:
        planted = {ts for ts, in conn.execute("SELECT ma_ts FROM _loi_cai_san")}
    found = {row[0] for row in store.run("doi_soat_trung_tuyen").rows}
    assert planted and planted <= found


def test_cutoff_scenario_is_consistent(store):
    same = store.run("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301", "phuong_thuc": "100", "diem_chuan": 16}).rows[0]
    lower = store.run("mo_phong_diem_chuan", {"ma_xet_tuyen": "7340301", "phuong_thuc": "100", "diem_chuan": 14}).rows[0]
    assert same[-2] == 0 and same[5] == same[6]  # điểm chuẩn hiện tại: không đổi
    assert lower[6] >= lower[5] and lower[-2] >= 0


# ---------- Trong graph ----------

PLAN = {"tasks": [{"task_id": "T1", "worker_type": "du_lieu", "task_type": "truy_van_du_lieu",
                   "goal": "Số thí sinh Kế toán chưa xác nhận nhập học và danh sách để gọi nhắc"}]}


def handler(worker_replies=None, synth="Còn thí sinh chưa xác nhận [CSDL-TS]; danh sách hiển thị bên dưới."):
    replies = worker_replies or [json.dumps({"queries": [{"name": "danh_sach_chua_xac_nhan", "params": {"ma_xet_tuyen": "7340301"}},
                                                         {"name": "xac_nhan_theo_nganh", "params": {"ma_xet_tuyen": "7340301"}}]})]
    count = {"worker": 0}

    def h(role, messages, label):
        kind = label.split(":")[0]
        if kind in ("plan", "plan_repair"):
            return json.dumps(PLAN, ensure_ascii=False)
        if kind == "worker":
            count["worker"] += 1
            return replies[min(count["worker"], len(replies)) - 1]
        if kind == "review":
            return ACCEPT
        if kind == "synthesize":
            return synth
        raise AssertionError(label)
    return h


def test_data_task_runs_and_personal_rows_never_enter_a_prompt(store):
    llm = FakeClient(handler())
    state = run("Ai trúng tuyển Kế toán mà chưa xác nhận?", llm, SOURCES, None, Limits(), None, {"tuyen_sinh", "analysis", "du_lieu"}, data=store)
    assert state["status"] == {"T1": "accepted"}
    tables = [e for e in state["events"] if e["event_type"] == "data_table"]
    assert len(tables) == 1 and tables[0]["detail"]["rows"] and tables[0]["actor"] == "du_lieu"
    prompts = json.dumps([m for _, _, m in llm.transcript], ensure_ascii=False)
    assert not any(v in prompts for v in personal_values(store))
    assert "tables" not in state["results"]["T1"] and "tables" not in json.dumps(state["history"], ensure_ascii=False)
    assert state["results"]["T1"]["claims"][0]["source_id"] == "CSDL-TS"
    review = [m for _, label, m in llm.transcript if label == "review:T1#1"][0][-1]["content"]
    assert "DANH MỤC TRUY VẤN CỦA HỆ THỐNG" in review  # người nghiệm thu biết hệ thống lưu gì, không đòi thứ không có
    assert next(e for e in state["events"] if e["event_type"] == "report_checked")["detail"]["ok"]  # [CSDL-TS] được phép dẫn


def test_unknown_query_is_sent_back_with_the_valid_names(store):
    bad = json.dumps({"queries": [{"name": "so_thi_sinh", "params": {}}]})
    good = json.dumps({"queries": [{"name": "tong_quan", "params": {}}]})
    llm = FakeClient(handler([bad, good]))
    state = run("Tổng quan", llm, SOURCES, None, Limits(), None, {"du_lieu"}, data=store)
    assert state["status"]["T1"] == "accepted" and state["attempts"]["T1"] == 2
    second = [m for _, label, m in llm.transcript if label == "worker:T1#2"][0][-1]["content"]
    assert "Không có truy vấn 'so_thi_sinh'" in second and "tong_quan" in second
    assert not [e for e in state["events"] if e["event_type"] == "data_table"]


def test_data_worker_is_not_offered_without_a_database():
    state = run("Tổng quan", FakeClient(handler()), SOURCES, None, Limits(), None, {"tuyen_sinh", "analysis", "du_lieu"})
    assert state["plan_errors"] and "du_lieu" in state["plan_errors"][0]


def test_replay_on_disk_keeps_no_rows_for_real_data(db_path, tmp_path):
    real = tmp_path / "that.sqlite"
    real.write_bytes(db_path.read_bytes())
    with sqlite3.connect(real) as conn:  # giả như dữ liệu thật: bỏ nhãn GIẢ LẬP
        conn.execute("UPDATE meta SET gia_tri = 'Dữ liệu tuyển sinh' WHERE khoa = 'ghi_chu'")
    store = open_store(real)
    assert not store.synthetic
    replays = tmp_path / "replays"
    body = TestClient(create_app(SOURCES, client_factory=lambda: FakeClient(handler()), replay_dir=replays, data=store)).get(
        "/api/ask", params={"q": "Ai chưa xác nhận?"}).text
    assert '"rows": [["TS' in body  # màn hình cán bộ vẫn có danh sách
    saved = json.loads(next(replays.glob("*.json")).read_text(encoding="utf-8"))
    tables = [r["event"]["detail"] for r in saved["events"] if r["event"]["event_type"] == "data_table"]
    assert tables and all(t["rows"] == [] and t["total"] > 0 for t in tables)


def test_web_data_mode_streams_the_table_to_the_screen(store, tmp_path):
    app = create_app(SOURCES, client_factory=lambda: FakeClient(handler()), replay_dir=tmp_path, data=store,
                     samples=[{"kind": "Số liệu", "q": "Ai chưa xác nhận?"}])
    client = TestClient(app)
    info = client.get("/api/info").json()
    assert info["data"] and info["synthetic"] and "GIẢ LẬP" in info["title"]
    assert "CSDL-TS" in client.get("/api/sources").json()
    assert client.get("/api/samples").json() == [{"kind": "Số liệu", "q": "Ai chưa xác nhận?"}]
    body = client.get("/api/ask", params={"q": "Ai trúng tuyển Kế toán mà chưa xác nhận?"}).text
    assert "event: done" in body and '"event_type": "data_table"' in body
