"""CLI: hồ sơ lượt chạy luôn được ghi (kể cả khi lỗi), không chứa khóa và không nằm trong OneDrive."""
import json

import pytest

from app import cli
from app.llm import FakeClient
from test_graph import make_handler

SECRET = "sk-SECRET-GATEWAY-KEY-123456"


@pytest.fixture
def fake_cli(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("OneDrive", str(tmp_path / "OneDrive"))
    monkeypatch.setattr(cli, "load_env", lambda: {"AIGW_OPENAI_KEY": SECRET})
    monkeypatch.setattr(cli, "GatewayClient", lambda models, env: FakeClient(make_handler(
        synthesize=f"Báo cáo [QĐ-620]. Lỗi cổng: Bearer {SECRET}", plan='{"tasks": [{"task_id": "T1", "worker_type": "nckh", '
                   '"task_type": "tra_cuu_noi_bo", "goal": "Tra quy chế", "context": {"refs": ["QĐ-620"]}}]}')))
    sources = tmp_path / "nguon.json"
    sources.write_text(json.dumps([{"source_id": "QĐ-620", "title": "Quy chế", "text": "Tối đa 25 tín chỉ."}], ensure_ascii=False), encoding="utf-8")
    return tmp_path, str(sources)


def only_run_dir(tmp_path):
    [run_dir] = (tmp_path / "runs").iterdir()
    return run_dir


def test_record_and_events_are_written_without_secrets(fake_cli, capsys):
    tmp_path, sources = fake_cli
    assert cli.main(["Tra quy chế", "--sources", sources]) == 0
    run_dir = only_run_dir(tmp_path)
    record = (run_dir / "record.json").read_text(encoding="utf-8")
    events = (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert SECRET not in record and json.loads(record)["status"] == {"T1": "accepted"}
    assert json.loads(events[0])["event_type"] == "plan_saved"
    assert "KẾ HOẠCH:" in capsys.readouterr().out


def test_record_is_written_even_when_the_run_crashes(fake_cli, monkeypatch):
    tmp_path, sources = fake_cli

    def crash(request, llm, sources, search, limits, on_event, workers):
        on_event({"event_type": "plan_saved", "task_id": None, "detail": {"tasks": []}})
        llm.complete("master", [], label="plan")
        raise RuntimeError(f"hỏng giữa chừng, khóa {SECRET}")
    monkeypatch.setattr(cli, "run", crash)
    with pytest.raises(RuntimeError):
        cli.main(["Tra quy chế", "--sources", sources])
    record = json.loads((only_run_dir(tmp_path) / "record.json").read_text(encoding="utf-8"))
    assert record["error"].startswith("RuntimeError") and SECRET not in record["error"]
    assert record["usage"]["calls"] == 1 and len(record["ledger"]) == 1


def test_refuses_to_write_records_inside_onedrive(fake_cli, monkeypatch):
    tmp_path, sources = fake_cli
    monkeypatch.setenv("OneDrive", str(tmp_path))
    assert cli.main(["Tra quy chế", "--sources", sources]) == 2
    assert not (tmp_path / "runs").exists()
