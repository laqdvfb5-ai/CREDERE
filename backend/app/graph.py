"""Graph của tác tử điều phối: lập kế hoạch → kiểm tra → chạy theo đợt (song song) → nghiệm thu, sửa có giới hạn → tổng hợp."""
import json
import operator
import re
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Annotated, Callable, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .config import Limits, redact
from .contracts import Plan, Review, Source, Task, WorkerResult
from .llm import LLMClient, parse_json
from .planning import ROLES, validate_plan
from .tools.data import DataStore
from .tools.search import SearchTool
from .workers import review_task, run_task, task_calls

CALLS_PER_ATTEMPT = 3  # Worker 1 + nghiệm thu 1 + hỏi lại nghiệm thu 1
SYNTH_CALLS = 2        # tổng hợp 1 + viết lại khi dẫn sai nguồn 1
CITATION = re.compile(r"\[([^\[\]\n]{1,120})\]")


def cited_ids(text: str) -> set[str]:
    """Mã trong ngoặc vuông; một ngoặc có thể ghi nhiều mã: [TS-100, TS-202] hoặc [TS-100; T3]."""
    return {part.strip() for inner in CITATION.findall(text) for part in re.split(r"[,;]", inner) if part.strip()}


MAX_REPLY_CHARS = 800


def plain_report(accepted: dict, kinds: dict[str, str], not_done_text: str) -> str:
    """Báo cáo do code ghép từ kết quả đã nghiệm thu: mỗi nhận định kèm nguồn, mỗi phép tính kèm mã nhiệm vụ."""
    lines = [f"- {c['text']} [{c['source_id']}]" for v in accepted.values() for c in v["claims"] if c.get("source_id")]
    lines += [f"- {r['name']} = {r['value']} {r['unit']} [{k}]" for k, v in accepted.items() if kinds[k] == "analysis"
              for r in v["data"]["calculations"]]  # hàng do code tạo, luôn đủ trường
    return ("Các kết quả đã nghiệm thu:\n" + "\n".join(lines)
            + (f"\n\nChưa hoàn thành:\n{not_done_text}" if not_done_text else ""))


def merge(a: dict | None, b: dict | None) -> dict:
    return {**(a or {}), **(b or {})}


def event(event_type: str, task_id: str | None = None, actor: str = "master", **detail) -> dict:
    return {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "event_type": event_type,
            "task_id": task_id, "actor": actor, "detail": detail}


class RunState(TypedDict, total=False):
    request: str
    plan: list[dict]
    plan_errors: list[str]
    status: Annotated[dict, merge]
    results: Annotated[dict, merge]  # lần thực thi mới nhất của mỗi nhiệm vụ
    reviews: Annotated[dict, merge]
    attempts: Annotated[dict, merge]
    history: Annotated[list[dict], operator.add]  # mọi lần thực thi: chỉ thị, kết quả, nghiệm thu, lời gọi model (NFR3)
    wave: list[str]
    events: Annotated[list[dict], operator.add]
    report: str


def plan_system(roles: dict[str, set[str]], max_tasks: int, notes: list[str] | None = None) -> str:
    """notes: mô tả các AI con (lĩnh vực, người dùng, dữ liệu) để tác tử điều phối biết giao việc cho ai."""
    subs = ("\nCác AI con (worker_type ai_..., task_type giao_viec) là cả một AI lĩnh vực: tự lập kế hoạch, tra tài liệu, dữ liệu "
            "và nghiệm thu rồi báo cáo lại. Giao cho mỗi AI con một yêu cầu đầy đủ như giao cho một phòng ban: nêu rõ cần số liệu gì, "
            "theo ngành, khóa, năm nào, để ghép được với lĩnh vực khác; câu cần nhiều lĩnh vực thì giao song song cho từng AI con, "
            "việc ghép, so sánh số liệu giữa các lĩnh vực giao cho analysis phụ thuộc các nhiệm vụ đó.\n" + "\n".join(notes)) if notes else ""
    return ("Bạn là tác tử điều phối của hệ thống đa tác tử cho trường đại học. Lập kế hoạch dạng đồ thị nhiệm vụ cho yêu cầu của người dùng.\n"
            "Tác tử thực thi và loại nhiệm vụ được phép:\n"
            + "\n".join(f"- {w}: {', '.join(sorted(t))}" for w, t in roles.items()) + subs
            + f"\nQuy tắc: câu hỏi đơn chỉ cần 1 nhiệm vụ; yêu cầu tổng hợp dùng đồ thị nhỏ, tối đa {max_tasks} nhiệm vụ; nhiệm vụ độc lập "
            "không phụ thuộc nhau để chạy song song; không lập nhiệm vụ tổng hợp báo cáo cuối (tác tử điều phối tự làm); "
            + ("mọi phép tính (cộng, nhân, tỷ lệ, chênh lệch) giao cho tác tử analysis, phụ thuộc vào nhiệm vụ lấy số liệu; "
               "tác tử analysis chỉ thấy mục tiêu và kết quả trước, nên mục tiêu phải gọi đúng đại lượng như người dùng hỏi "
               "(ví dụ số thí sinh đặt nguyện vọng 1, không viết chung là số thí sinh); "
               "người dùng hỏi một con số mà nguồn không ghi sẵn nhưng suy được từ số liệu gốc (ví dụ mức một năm từ đơn giá, "
               "khối lượng và thời gian) thì nhiệm vụ lấy số liệu phải trích đủ các số đầu vào và tác tử analysis tính ước tính; "
               "tác tử analysis không đọc tài liệu nên không nhận việc tra cứu hay đối chiếu văn bản; "
               "tác tử chuyên môn chỉ trích số liệu kèm nguồn, không tự tính; " if "analysis" in roles else "") +
            "task_id chỉ gồm chữ, số, '_' hoặc '-'; context.refs chỉ chứa mã nguồn có trong danh sách nguồn; "
            "nguồn ghi 'đã có văn bản cập nhật' thì đưa cả mã văn bản cập nhật vào context.refs; "
            "context.summary là bối cảnh ngắn mà tác tử thực thi cần biết. "
            "Viết kế hoạch gọn: goal tối đa 2 câu, summary tối đa 1 câu, constraints và acceptance_criteria mỗi loại tối đa 3 ý ngắn, "
            "không chép lại nguyên văn yêu cầu. "
            "Chỉ khi yêu cầu là lời chào, câu xã giao, nằm ngoài mọi lĩnh vực trên, hoặc quá mơ hồ để giao việc thì không lập nhiệm vụ "
            "mà trả lời ngay trong reply (ngắn, không nêu số liệu hay quy định nào; mơ hồ thì hỏi lại một câu cụ thể); "
            "mọi câu hỏi về quy định, số liệu, văn bản đều phải lập nhiệm vụ.\n"
            'Chỉ trả về JSON thuần: {"tasks": [{"task_id": "T1", "worker_type": "...", "task_type": "...", "goal": "...", '
            '"context": {"refs": [], "summary": ""}, "constraints": [], "depends_on": [], "acceptance_criteria": []}], "reply": ""}')


SYNTH_SYSTEM = ("Bạn là tác tử điều phối. Viết câu trả lời cuối bằng tiếng Việt từ các kết quả đã được nghiệm thu. Mỗi nhận định "
                "ghi source_id trong ngoặc vuông; số liệu do tác tử phân tích tính thì ghi mã nhiệm vụ, ví dụ [T3]. "
                "Không thêm số liệu ngoài kết quả. Nêu rõ phần chưa làm được và lý do.")


def build_graph(llm: LLMClient, sources: list[Source], search: SearchTool | None = None, limits: Limits = Limits(),
                workers: set[str] | None = None, synth_hint: str = "", plan_hint: str = "", data: DataStore | None = None,
                subagents: dict | None = None, emit: Callable[[dict], None] | None = None, structured_report: bool = False):
    """workers: chỉ dùng các tác tử này (ví dụ {"tuyen_sinh", "analysis"} cho trợ lý tuyển sinh); None là mọi tác tử.
    synth_hint, plan_hint: chỉ dẫn thêm của từng ứng dụng cho bước tổng hợp và bước lập kế hoạch;
    mã nguồn ghi trong synth_hint được phép dẫn trong câu trả lời.
    subagents: AI con được giao việc, khóa là worker_type ("ai_dao_tao"); mỗi AI con có key, ten, mo_ta(), call_budget, run().
    emit: nhận ngay sự kiện bên trong AI con (sub_event) để trang web hiện tiến độ.
    structured_report: lượt chạy của AI con được giao việc; không gọi model viết báo cáo văn mà gửi thẳng kết quả đã nghiệm thu
    (nhận định kèm nguồn, phép tính) để AI Tổng hợp tự viết câu trả lời cuối, bớt một lượt viết dài trên đường găng."""
    subagents = subagents or {}
    start = len(llm.ledger.calls)  # sổ ghi của lượt chạy này bắt đầu từ đây
    public = [s for s in sources if s.access_scope == "public"]
    source_list = "\n".join(f"- {s.source_id}: {s.title}" for s in public) or "- (không có)"
    roles = {w: t for w, t in ROLES.items()  # chỉ giao việc cho tác tử chạy được
             if (w != "search" or search is not None) and (w != "du_lieu" or data is not None) and (workers is None or w in workers)}
    roles.update({w: {"giao_viec"} for w in subagents if workers is None or w in workers})
    notes = [f"- {w}: {s.mo_ta()}" for w, s in subagents.items() if w in roles]
    # trường hợp xấu nhất của một lần thực thi: Worker 1 + nghiệm thu 2; AI con thì cả lượt chạy của nó + nghiệm thu 2
    budget_of = {w: s.call_budget + 2 for w, s in subagents.items()}

    def spent() -> tuple[int, float]:
        calls = llm.ledger.calls[start:]
        return len(calls), sum(c.cost_usd for c in calls)

    def plan_node(state: RunState) -> dict:
        messages = [{"role": "system", "content": f"{plan_system(roles, limits.max_tasks, notes)}\n{plan_hint}".strip()},
                    {"role": "user", "content": f"YÊU CẦU: {state['request']}\n\nNGUỒN CÓ SẴN:\n{source_list}"}]
        errors, plan = [], None
        for attempt in range(2):  # một lần sửa kế hoạch nếu sai
            try:
                text = llm.complete("master", messages, label="plan" if attempt == 0 else "plan_repair")
            except Exception as e:
                errors = ["Lỗi gọi model lập kế hoạch: " + redact(f"{type(e).__name__}: {e}")[:300]]
                break
            try:
                plan = Plan.model_validate(parse_json(text))
                if not plan.tasks and plan.reply.strip():  # lời chào, ngoài phạm vi, cần hỏi lại: không chạy cả đồ thị nhiệm vụ
                    return {"plan": [], "status": {}, "report": plan.reply.strip()[:MAX_REPLY_CHARS],
                            "events": [event("direct_reply"), event("report_published", accepted_tasks=0, direct=True)]}
                errors = validate_plan(plan, limits, set(roles), {s.source_id for s in public}, roles)
            except Exception as e:
                plan, errors = None, [f"Kế hoạch không đúng định dạng: {type(e).__name__}: {e}"[:400]]
            if not errors:
                break
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": "Kế hoạch chưa hợp lệ:\n- " + "\n- ".join(errors) + "\nHãy sửa và trả lại JSON."}]
        if errors:
            return {"plan_errors": errors, "events": [event("plan_rejected", errors=errors)]}
        tasks = [t.model_dump() for t in plan.tasks]
        return {"plan": tasks, "status": {t["task_id"]: "pending" for t in tasks}, "events": [event("plan_saved", tasks=tasks)]}

    def join_node(state: RunState) -> dict:
        tasks = [Task(**t) for t in state["plan"]]
        status = dict(state.get("status", {}))
        events = []
        changed = True
        while changed:  # chặn nhiệm vụ có phụ thuộc đã thất bại hoặc bị chặn
            changed = False
            for t in tasks:
                bad = [d for d in t.depends_on if status[d] in ("failed", "blocked", "budget_exceeded")]
                if status[t.task_id] in ("pending", "revise") and bad:
                    status[t.task_id] = "blocked"
                    events.append(event("task_blocked", t.task_id, blocked_by=bad))
                    changed = True
        open_tasks = [t.task_id for t in tasks if status[t.task_id] in ("pending", "revise")]
        ready = [t.task_id for t in tasks if t.task_id in open_tasks and all(status[d] == "accepted" for d in t.depends_on)]
        calls, cost = spent()
        kinds = {t.task_id: t.worker_type for t in tasks}
        need = {t: budget_of.get(kinds[t], CALLS_PER_ATTEMPT) for t in open_tasks}
        left = limits.max_llm_calls - calls - SYNTH_CALLS  # tính trường hợp xấu nhất, giữ chỗ cho tổng hợp
        fits = any(need[t] <= left for t in ready)  # còn nhiệm vụ sẵn sàng nào vừa ngân sách lời gọi không
        if open_tasks and (not fits or cost >= limits.max_cost_usd):
            for task_id in open_tasks:
                status[task_id] = "budget_exceeded"
            events.append(event("budget_exceeded", llm_calls=calls, cost_usd=round(cost, 6), tasks=open_tasks))
            ready = []
        wave = []
        for task_id in ready:  # giao theo thứ tự kế hoạch, nhiệm vụ nào còn đủ chỗ thì giao
            if need[task_id] <= left:
                wave.append(task_id)
                left -= need[task_id]
        if len(ready) > len(wave):
            events.append(event("wave_trimmed", deferred=[t for t in ready if t not in wave], llm_calls=calls))
        if wave:
            events.append(event("wave_dispatched", tasks=wave))
        return {"status": status, "wave": wave, "events": events}

    def dispatch(state: RunState):
        if state.get("plan_errors") or not state.get("wave"):
            return "synthesize"
        by_id = {t["task_id"]: t for t in state["plan"]}
        sends = []
        for task_id in state["wave"]:
            task = by_id[task_id]
            feedback = previous = None
            if state["status"][task_id] == "revise":
                review = state["reviews"][task_id]
                feedback = "\n".join([review["feedback"]] + [f"- {c}" for c in review["required_changes"]]).strip()
                previous = {k: state["results"][task_id][k] for k in ("data", "claims", "error")}
            sends.append(Send("execute", {"task": task, "feedback": feedback, "previous": previous,
                                          "attempt": state.get("attempts", {}).get(task_id, 0) + 1,
                                          "inputs": {d: state["results"][d] for d in task["depends_on"]}}))
        return sends

    def execute_node(payload: dict) -> dict:
        task = Task(**payload["task"])
        task_id, attempt = task.task_id, payload["attempt"]
        before = len(llm.ledger.calls)
        try:
            inputs = {k: WorkerResult(**v) for k, v in payload["inputs"].items()}
            result = run_task(task, inputs, payload["feedback"], llm, sources, search, attempt, payload["previous"], data, subagents, emit)
            review: Review = review_task(task, result, inputs, llm, sources, attempt, payload["feedback"], data)
        except Exception as e:  # lưới an toàn: lỗi ngoài dự kiến chỉ làm hỏng nhiệm vụ này, không làm hỏng cả lượt chạy
            msg = redact(f"{type(e).__name__}: {e}")[:300]
            result = WorkerResult(task_id=task_id, status="error", error=msg)
            review = Review(task_id=task_id, accepted=False, checks={"khong_loi": False}, feedback=f"Lỗi hệ thống: {msg}", reviewer_error=msg)
        if review.accepted:
            status = "accepted"
        elif review.reviewer_error or attempt > limits.max_revisions:
            status = "failed"  # nghiệm thu không chạy được thì chạy lại Worker cũng không có ích
        else:
            status = "revise"
        record = {"task_id": task_id, "attempt": attempt,
                  "directive": {**payload["task"], "feedback": payload["feedback"], "inputs": sorted(payload["inputs"])},
                  "result": result.model_dump(), "review": review.model_dump(), "next": status,
                  "calls": [asdict(c) for c in task_calls(llm, before, task_id)]}
        return {"results": {task_id: result.model_dump()}, "reviews": {task_id: review.model_dump()},
                "attempts": {task_id: attempt}, "status": {task_id: status}, "history": [record],
                "events": [event("task_executed", task_id, task.worker_type, attempt=attempt, status=result.status,
                                 error=result.error, usage=result.usage.model_dump()),
                           event("task_reviewed", task_id, "master", attempt=attempt, accepted=review.accepted, checks=review.checks,
                                 feedback=review.feedback, required_changes=review.required_changes,
                                 reviewer_error=review.reviewer_error, next=status)]
                + [event("data_table", task_id, task.worker_type, **t) for t in result.tables if review.accepted]}  # chỉ tới màn hình cán bộ

    def reason(state: RunState, task_id: str, status: str) -> str:
        if status == "blocked":
            by_id = {t["task_id"]: t for t in state["plan"]}
            return "phụ thuộc nhiệm vụ chưa hoàn thành: " + ", ".join(d for d in by_id[task_id]["depends_on"] if state["status"][d] != "accepted")
        if status == "budget_exceeded":
            return "hết ngân sách lời gọi hoặc chi phí của lượt chạy"
        review = state.get("reviews", {}).get(task_id) or {}
        return "; ".join(x for x in [review.get("feedback", "")] + review.get("required_changes", []) if x)[:500] or status

    def synthesize_node(state: RunState) -> dict:
        if state.get("plan_errors"):
            report = "Không lập được kế hoạch hợp lệ nên chưa thực hiện yêu cầu:\n- " + "\n- ".join(state["plan_errors"])
            return {"report": report, "events": [event("report_published", accepted_tasks=0)]}
        status = state.get("status", {})
        goals = {t["task_id"]: t["goal"] for t in state["plan"]}
        accepted = {k: {"goal": goals[k], "data": v["data"], "claims": v["claims"]}
                    for k, v in state.get("results", {}).items() if status.get(k) == "accepted"}
        not_done = {k: {"goal": goals[k], "status": s, "reason": reason(state, k, s)} for k, s in status.items() if s != "accepted"}
        not_done_text = "\n".join(f"- {k} ({v['goal']}): {v['status']}, {v['reason']}" for k, v in not_done.items())
        if not accepted:  # không có gì để tổng hợp thì không gọi model, tránh model tự bịa nội dung
            report = "Chưa có kết quả nào được nghiệm thu nên chưa lập được báo cáo.\n" + not_done_text
            return {"report": report, "events": [event("report_published", accepted_tasks=0, not_done=not_done)]}
        if structured_report:  # AI con: AI Tổng hợp tự viết câu trả lời từ kết quả này, không cần một bài văn ở giữa
            kinds = {t["task_id"]: t["worker_type"] for t in state["plan"]}
            return {"report": plain_report(accepted, kinds, not_done_text),
                    "events": [event("report_published", accepted_tasks=len(accepted), not_done=not_done, structured=True)]}
        body = (f"YÊU CẦU: {state['request']}\n\nKẾT QUẢ ĐÃ NGHIỆM THU:\n{json.dumps(accepted, ensure_ascii=False)}\n\n"
                f"NHIỆM VỤ CHƯA HOÀN THÀNH:\n{not_done_text or 'không có'}")
        messages = [{"role": "system", "content": f"{SYNTH_SYSTEM} {synth_hint}".strip()}, {"role": "user", "content": body}]
        try:
            report = llm.complete("master", messages, label="synthesize")
        except Exception as e:  # vẫn trả về kết quả đã nghiệm thu thay vì mất cả lượt chạy
            msg = redact(f"{type(e).__name__}: {e}")[:300]
            kinds = {t["task_id"]: t["worker_type"] for t in state["plan"]}
            report = f"Không tổng hợp được báo cáo do lỗi model ({msg}). " + plain_report(accepted, kinds, not_done_text)
            return {"report": report, "events": [event("report_failed", error=msg, accepted_tasks=len(accepted), not_done=not_done)]}

        # Kiểm tra dữ kiện: báo cáo chỉ được dẫn nguồn có trong kết quả đã nghiệm thu
        allowed = ({c["source_id"] for v in accepted.values() for c in v["claims"] if c.get("source_id")} | set(accepted)
                   | cited_ids(synth_hint))
        unknown = sorted(cited_ids(report) - allowed)
        if unknown and spent()[0] < limits.max_llm_calls:
            messages += [{"role": "assistant", "content": report},
                         {"role": "user", "content": f"Báo cáo dẫn mã không có trong kết quả đã nghiệm thu: {', '.join(unknown)}. "
                                                     f"Viết lại, chỉ dẫn các mã: {', '.join(sorted(allowed))}."}]
            try:
                report = llm.complete("master", messages, label="synthesize_fix")
                unknown = sorted(cited_ids(report) - allowed)
            except Exception:
                pass  # giữ bản đầu, kèm lưu ý bên dưới
        if unknown:
            report += "\n\nLưu ý của hệ thống: báo cáo nhắc tới mã nguồn không có trong kết quả đã nghiệm thu: " + ", ".join(unknown) + "."
        return {"report": report, "events": [event("report_checked", ok=not unknown, unknown_ids=unknown),
                                             event("report_published", accepted_tasks=len(accepted), not_done=not_done)]}

    g = StateGraph(RunState)
    g.add_node("plan", plan_node)
    g.add_node("join", join_node)
    g.add_node("execute", execute_node)
    g.add_node("synthesize", synthesize_node)
    g.add_edge(START, "plan")
    g.add_conditional_edges("plan", lambda s: END if s.get("report") else "synthesize" if s.get("plan_errors") else "join",
                            ["join", "synthesize", END])
    g.add_conditional_edges("join", dispatch, ["execute", "synthesize"])
    g.add_edge("execute", "join")
    g.add_edge("synthesize", END)
    return g.compile()


def run(request: str, llm: LLMClient, sources: list[Source], search: SearchTool | None = None, limits: Limits = Limits(),
        on_event: Callable[[dict], None] | None = None, workers: set[str] | None = None, synth_hint: str = "",
        plan_hint: str = "", data: DataStore | None = None, subagents: dict | None = None, structured_report: bool = False) -> dict:
    """Chạy một yêu cầu. on_event nhận từng sự kiện ngay khi một bước graph xong, nên kế hoạch được lưu và hiển thị
    trước khi tác tử thực thi đầu tiên chạy (FR1)."""
    start = len(llm.ledger.calls)
    graph = build_graph(llm, sources, search, limits, workers, synth_hint, plan_hint, data, subagents, on_event, structured_report)
    state: dict = {}
    for mode, chunk in graph.stream({"request": request, "events": [], "history": []},
                                    config={"max_concurrency": limits.max_parallel, "recursion_limit": limits.recursion_limit},
                                    stream_mode=["updates", "values"]):
        if mode == "values":
            state = chunk
        elif on_event:
            for update in chunk.values():
                for e in (update or {}).get("events", []):
                    on_event(e)
    return {**state, "usage": llm.ledger.totals(start)}
