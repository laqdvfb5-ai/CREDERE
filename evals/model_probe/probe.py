"""Đo nhanh các model qua cổng API cho Credere (mốc M-1).

Chạy:  py -3 probe.py                 # liệt kê model, gọi thử, chấm điểm
       py -3 probe.py --only claude   # chỉ model có chữ "claude" trong tên
       py -3 probe.py --max-models 20 # giới hạn số model được chấm

Key đọc từ %USERPROFILE%\\.credere\\.env (AIGW_BASE_URL, AIGW_OPENAI_KEY, AIGW_CLAUDE_KEY).
Không in key ra màn hình hay file kết quả. Kết quả ghi vào results/.
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)

ENV = dict(line.strip().split("=", 1) for line in open(os.path.expanduser(r"~\.credere\.env"), encoding="utf-8")
           if "=" in line and not line.startswith("#"))
BASE = ENV["AIGW_BASE_URL"].rstrip("/")
KEYS = {"openai-key": ENV["AIGW_OPENAI_KEY"], "claude-key": ENV["AIGW_CLAUDE_KEY"]}
SECRETS = list(KEYS.values())

SKIP = re.compile(r"embed|tts|whisper|dall-e|image|audio|moderation|realtime|transcri|rerank|sora|veo|flux|midjourney|"
                  r"mj[_-]|suno|kling|speech|video|music|ocr", re.I)


def redact(text):
    text = str(text)
    for s in SECRETS:
        text = text.replace(s, "***")
    return text


def http(method, path, key, payload=None, style="bearer", timeout=180):
    headers = {"Content-Type": "application/json", "User-Agent": "credere-probe/0.1"}
    if style == "bearer":
        headers["Authorization"] = f"Bearer {key}"
    else:
        headers.update({"x-api-key": key, "anthropic-version": "2023-06-01", "Authorization": f"Bearer {key}"})
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    for attempt in range(3):
        t0 = time.time()
        req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return {"ok": True, "status": r.status, "body": json.loads(r.read().decode("utf-8")), "latency": time.time() - t0}
        except urllib.error.HTTPError as e:
            err = redact(e.read()[:600].decode("utf-8", errors="replace"))
            if e.code in (429, 502, 503, 504) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return {"ok": False, "status": e.code, "error": err, "latency": time.time() - t0}
        except Exception as e:  # mạng, timeout
            if attempt < 2:
                time.sleep(3)
                continue
            return {"ok": False, "status": None, "error": redact(f"{type(e).__name__}: {e}"), "latency": time.time() - t0}


# ---------- Gọi model: định dạng OpenAI, dự phòng định dạng Anthropic cho Claude ----------

def call_openai(key, model, messages, max_tokens, tools=None):
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if tools:
        payload["tools"] = [{"type": "function", "function": t} for t in tools]
    r = http("POST", "/v1/chat/completions", key, payload)
    if not r["ok"] and r["status"] == 400 and "max_tokens" in r.get("error", ""):
        payload.pop("max_tokens")
        payload["max_completion_tokens"] = max_tokens
        r = http("POST", "/v1/chat/completions", key, payload)
    if not r["ok"]:
        return {"ok": False, "error": f"HTTP {r['status']}: {r['error']}", "latency": r["latency"]}
    b = r["body"]
    try:
        msg = b["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return {"ok": False, "error": "phản hồi không có choices: " + redact(json.dumps(b)[:300]), "latency": r["latency"]}
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    calls = [{"name": c["function"]["name"], "arguments": c["function"].get("arguments", "")}
             for c in (msg.get("tool_calls") or []) if c.get("function")]
    u = b.get("usage") or {}
    return {"ok": True, "text": content, "tool_calls": calls, "latency": r["latency"], "reported_model": b.get("model"),
            "in_tokens": u.get("prompt_tokens"), "out_tokens": u.get("completion_tokens"), "format": "openai"}


def call_anthropic(key, model, messages, max_tokens, tools=None):
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    payload = {"model": model, "max_tokens": max_tokens, "messages": [m for m in messages if m["role"] != "system"]}
    if system:
        payload["system"] = system
    if tools:
        payload["tools"] = [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in tools]
    r = http("POST", "/v1/messages", key, payload, style="anthropic")
    if not r["ok"]:
        return {"ok": False, "error": f"HTTP {r['status']}: {r['error']}", "latency": r["latency"]}
    b = r["body"]
    blocks = b.get("content") or []
    text = "".join(x.get("text", "") for x in blocks if x.get("type") == "text")
    calls = [{"name": x["name"], "arguments": json.dumps(x.get("input", {}), ensure_ascii=False)} for x in blocks if x.get("type") == "tool_use"]
    u = b.get("usage") or {}
    return {"ok": True, "text": text, "tool_calls": calls, "latency": r["latency"], "reported_model": b.get("model"),
            "in_tokens": u.get("input_tokens"), "out_tokens": u.get("output_tokens"), "format": "anthropic"}


def call(key, model, messages, max_tokens, tools=None, fmt=None):
    if fmt == "anthropic":
        return call_anthropic(key, model, messages, max_tokens, tools)
    r = call_openai(key, model, messages, max_tokens, tools)
    if not r["ok"] and fmt is None and "claude" in model.lower():
        r2 = call_anthropic(key, model, messages, max_tokens, tools)
        if r2["ok"]:
            return r2
    return r


# ---------- Bài kiểm tra ----------

PLAN_SYS = ("Bạn là tác tử điều phối của hệ thống đa tác tử cho trường đại học. Hãy lập kế hoạch dạng đồ thị nhiệm vụ. "
            "Chỉ trả về JSON, không giải thích, theo đúng dạng: "
            '{"tasks":[{"id":"T0","worker_type":"...","task_type":"...","goal":"...","depends_on":[]}]}. '
            "worker_type chỉ được chọn trong: dieu_phoi, nckh, dao_tao, htqt, search, analysis. "
            "task_type chỉ được chọn trong: tra_cuu_noi_bo, tim_nguon, trich_bang_chung, tinh_toan, so_sanh, soan_thao. "
            "Tối đa 8 nhiệm vụ. Các việc độc lập phải không phụ thuộc nhau để chạy song song. Nhiệm vụ cuối là soạn báo cáo.")
PLAN_USER = ("Hãy phân tích tác động của việc ứng dụng AI vào kết quả nghiên cứu khoa học trong 3 năm qua, lập bảng so sánh "
             "3 case study tiêu biểu và đề xuất lộ trình triển khai kèm chi phí ước tính cho kế hoạch nghiên cứu khoa học năm tới.")
WORKERS = {"dieu_phoi", "nckh", "dao_tao", "htqt", "search", "analysis"}
TTYPES = {"tra_cuu_noi_bo", "tim_nguon", "trich_bang_chung", "tinh_toan", "so_sanh", "soan_thao"}

TOOLS = [
    {"name": "search_openalex", "description": "Tìm và đếm công bố khoa học trên OpenAlex theo từ khóa và khoảng năm.",
     "parameters": {"type": "object", "properties": {
         "query": {"type": "string", "description": "Từ khóa tìm kiếm, tiếng Anh"},
         "from_year": {"type": "integer"}, "to_year": {"type": "integer"}},
         "required": ["query", "from_year", "to_year"]}},
    {"name": "calculate", "description": "Tính một biểu thức số học.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
]
TOOL_USER = ("Hãy dùng công cụ để đếm số công bố về 'artificial intelligence in scientific research' "
             "trong giai đoạn 2023 đến 2025. Gọi công cụ ngay, chưa cần trả lời.")

SOURCE = ("[QĐ-01, Điều 5] Sinh viên được đăng ký tối đa 25 tín chỉ mỗi học kỳ chính. Sinh viên có điểm trung bình học kỳ "
          "trước dưới 1,0 chỉ được đăng ký tối đa 14 tín chỉ.\n"
          "[QĐ-01, Điều 9] Lệ phí phúc khảo là 20.000 đồng mỗi học phần. Đơn phúc khảo nộp tại Phòng Quản lý đào tạo trong "
          "7 ngày kể từ ngày công bố điểm.\n"
          "[Trang Dịch vụ số] Trang này liệt kê liên kết tới cổng thông tin sinh viên và hệ thống học trực tuyến. Trang KHÔNG "
          "cho biết cổng nào hiển thị lịch học cá nhân và KHÔNG mô tả cách khôi phục mật khẩu.")
GROUND_SYS = ("Bạn là trợ lý của trường đại học. Chỉ trả lời dựa trên các nguồn được cấp dưới đây. Mỗi nhận định phải ghi mã "
              "nguồn trong ngoặc vuông, ví dụ [QĐ-01, Điều 5]. Nếu nguồn không đủ để trả lời, nói rõ là chưa đủ căn cứ và "
              "không suy đoán.\n\nNGUỒN:\n" + SOURCE)
GROUND_Q = {
    "co_nguon": "Sinh viên có điểm trung bình học kỳ trước là 0,8 được đăng ký tối đa bao nhiêu tín chỉ, và phúc khảo mất bao nhiêu tiền mỗi học phần?",
    "thieu_nguon": "Học phí mỗi tín chỉ năm 2026 là bao nhiêu?",
    "bay": "Em xem lịch học cá nhân ở đâu? Nếu quên mật khẩu thì làm thế nào?",
}
REFUSE = re.compile(r"chưa đủ|không đủ|không có thông tin|không tìm thấy|không đề cập|không nêu|không cho biết|không mô tả|"
                    r"chưa có thông tin|không có căn cứ|không được nêu|không có dữ liệu", re.I)

CALC_USER = ("Kế hoạch năm tới gồm 3 đề tài, mỗi đề tài 12.500.000 đồng, và 2 hội thảo, mỗi hội thảo 8.750.000 đồng. "
             "Cộng thêm 10% dự phòng trên tổng. Tổng chi phí là bao nhiêu đồng? Ghi con số cuối cùng ở dòng cuối.")
VN_USER = ("Viết đúng 3 gạch đầu dòng, mỗi dòng bắt đầu bằng '- ', mỗi dòng không quá 20 từ, bằng tiếng Việt có dấu, "
           "nêu lợi ích của việc dẫn nguồn trong báo cáo khoa học. Không viết gì khác.")


def parse_json(text):
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1)
    s, e = t.find("{"), t.rfind("}")
    if s < 0 or e < 0:
        return None
    try:
        return json.loads(t[s:e + 1])
    except json.JSONDecodeError:
        return None


def score_plan(r):
    checks = {}
    obj = parse_json(r.get("text", "")) if r["ok"] else None
    tasks = obj.get("tasks") if isinstance(obj, dict) else None
    checks["json_hop_le"] = isinstance(tasks, list)
    tasks = tasks if isinstance(tasks, list) else []
    checks["so_nhiem_vu_3_8"] = 3 <= len(tasks) <= 8
    fields = {"id", "worker_type", "task_type", "goal", "depends_on"}
    checks["du_truong"] = bool(tasks) and all(isinstance(t, dict) and fields <= set(t) for t in tasks)
    checks["dung_danh_muc"] = bool(tasks) and all(isinstance(t, dict) and t.get("worker_type") in WORKERS and t.get("task_type") in TTYPES for t in tasks)
    ids = {t.get("id") for t in tasks if isinstance(t, dict)}
    deps = {t.get("id"): [d for d in (t.get("depends_on") or []) if isinstance(d, str)] for t in tasks if isinstance(t, dict)}
    checks["phu_thuoc_ton_tai"] = bool(tasks) and all(d in ids for ds in deps.values() for d in ds)

    def ancestors(x, seen=None):
        seen = set() if seen is None else seen
        for d in deps.get(x, []):
            if d not in seen:
                seen.add(d)
                ancestors(d, seen)
        return seen
    anc = {x: ancestors(x) for x in deps}
    checks["khong_chu_trinh"] = bool(tasks) and all(x not in a for x, a in anc.items())
    # Hai nhiệm vụ bất kỳ (kể cả nhiệm vụ gốc) không phụ thuộc nhau là chạy song song được.
    checks["co_nhanh_song_song"] = any(a != b and a not in anc[b] and b not in anc[a] for a in deps for b in deps)
    finals = [t.get("id") for t in tasks if isinstance(t, dict) and t.get("task_type") == "soan_thao"]
    checks["tong_hop_cuoi"] = any(len(anc.get(f, set())) >= max(1, int(0.8 * (len(tasks) - 1))) for f in finals)
    return sum(checks.values()) / len(checks), checks


def score_tool(r):
    checks = {"goi_cong_cu": False, "dung_ten": False, "tham_so_json": False, "dung_nam": False}
    calls = r.get("tool_calls") or [] if r["ok"] else []
    if calls:
        checks["goi_cong_cu"] = True
        c = calls[0]
        checks["dung_ten"] = c["name"] == "search_openalex"
        try:
            a = json.loads(c["arguments"]) if isinstance(c["arguments"], str) else c["arguments"]
            checks["tham_so_json"] = isinstance(a, dict) and "query" in a
            checks["dung_nam"] = int(a.get("from_year", 0)) == 2023 and int(a.get("to_year", 0)) == 2025
        except (ValueError, TypeError):
            pass
    return sum(checks.values()) / len(checks), checks


def score_ground(results):
    a, b, c = (results[k].get("text", "") if results[k]["ok"] else "" for k in ("co_nguon", "thieu_nguon", "bay"))
    checks = {
        "co_nguon_14": bool(re.search(r"\b14\b", a)),
        "co_nguon_20000": bool(re.search(r"20[.,\s]?000|20 nghìn|20k", a, re.I)),
        "co_nguon_trich_dan": "[" in a and "QĐ-01" in a,
        "thieu_nguon_tu_choi": bool(REFUSE.search(b)),
        "thieu_nguon_khong_bia_so": not re.search(r"\d[\d.,\s]*\s*(đồng|vnđ|vnd|nghìn|triệu)", re.sub(r"20[.,]?000\s*đồng", "", b), re.I),
        "bay_neu_gioi_han": bool(REFUSE.search(c)),
        "bay_khong_bia": not re.search(r"(nhấn|bấm|chọn|click)[^.\n]{0,40}quên mật khẩu|quên mật khẩu[^.\n]{0,40}(nhấn|bấm|chọn|click)|"
                                       r"đăng nhập[^.\n]{0,60}(để|sẽ|là) (xem|thấy)[^.\n]{0,20}lịch", c, re.I),
    }
    return sum(checks.values()) / len(checks), checks


def score_calc(r):
    t = r.get("text", "") if r["ok"] else ""
    ok = bool(re.search(r"60[.,\s]?500[.,\s]?000|60,5 triệu|60\.5 triệu", t))
    return float(ok), {"dung_60_500_000": ok}


def score_vn(r):
    t = (r.get("text", "") if r["ok"] else "").strip()
    lines = [x.strip() for x in t.splitlines() if x.strip()]
    checks = {
        "dung_3_dong": len(lines) == 3 and all(x.startswith("- ") for x in lines),
        "moi_dong_toi_da_20_tu": bool(lines) and all(len(x[2:].split()) <= 20 for x in lines),
        "co_dau_tieng_viet": bool(re.search(r"[ăâđêôơưàáạảãèéẹẻẽìíịỉĩòóọỏõùúụủũỳýỵỷỹ]", t.lower())),
    }
    return sum(checks.values()) / len(checks), checks


WEIGHTS = {"bam_nguon": 0.35, "lap_ke_hoach": 0.25, "goi_cong_cu": 0.15, "tieng_viet": 0.15, "tinh_toan": 0.10}


def bench(key_name, model, fmt, log):
    key = KEYS[key_name]
    rec = {"key": key_name, "model": model, "format": fmt, "calls": []}

    def run(label, messages, max_tokens, tools=None):
        r = call(key, model, messages, max_tokens, tools, fmt)
        rec["calls"].append({"task": label, **{k: v for k, v in r.items() if k != "tool_calls"}, "tool_calls": r.get("tool_calls")})
        return r

    s = {}
    s["lap_ke_hoach"] = score_plan(run("plan", [{"role": "system", "content": PLAN_SYS}, {"role": "user", "content": PLAN_USER}], 2500))
    s["goi_cong_cu"] = score_tool(run("tool", [{"role": "user", "content": TOOL_USER}], 1500, TOOLS))
    g = {k: run("ground_" + k, [{"role": "system", "content": GROUND_SYS}, {"role": "user", "content": q}], 1500) for k, q in GROUND_Q.items()}
    s["bam_nguon"] = score_ground(g)
    s["tinh_toan"] = score_calc(run("calc", [{"role": "user", "content": CALC_USER}], 1500))
    s["tieng_viet"] = score_vn(run("vn", [{"role": "user", "content": VN_USER}], 1000))
    rec["scores"] = {k: round(v[0], 3) for k, v in s.items()}
    rec["checks"] = {k: v[1] for k, v in s.items()}
    rec["total"] = round(sum(WEIGHTS[k] * s[k][0] for k in WEIGHTS), 3)
    ok_calls = [c for c in rec["calls"] if c.get("ok")]
    rec["errors"] = sum(1 for c in rec["calls"] if not c.get("ok"))
    rec["latency_median"] = round(statistics.median([c["latency"] for c in ok_calls]), 2) if ok_calls else None
    rec["tokens_in"] = sum(c.get("in_tokens") or 0 for c in ok_calls)
    rec["tokens_out"] = sum(c.get("out_tokens") or 0 for c in ok_calls)
    rec["reported_models"] = sorted({str(c.get("reported_model")) for c in ok_calls})
    log(f"  chấm xong {model} [{key_name}]: {rec['total']:.2f} (lỗi gọi: {rec['errors']})")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="chỉ model có chuỗi này trong tên")
    ap.add_argument("--max-models", type=int, default=60)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    log = lambda m: print(m, flush=True)

    # 1. Liệt kê model của từng key
    models = {}
    for kn, key in KEYS.items():
        r = http("GET", "/v1/models", key)
        if not r["ok"]:
            r = http("GET", "/v1/models", key, style="anthropic")
        ids = sorted({m.get("id") for m in (r.get("body") or {}).get("data", []) if m.get("id")}) if r["ok"] else []
        models[kn] = ids
        log(f"[1] {kn}: {'HTTP ' + str(r['status']) if not r['ok'] else ''} {len(ids)} model" + (f" — lỗi: {r.get('error', '')[:200]}" if not r["ok"] else ""))
    json.dump(models, open(os.path.join(RES, "models.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for kn, ids in models.items():
        log(f"    {kn}: " + ", ".join(ids))

    pairs = [(kn, m) for kn, ids in models.items() for m in ids if not SKIP.search(m) and re.search(args.only, m)]
    skipped = [(kn, m) for kn, ids in models.items() for m in ids if SKIP.search(m)]
    if skipped:
        log(f"    bỏ qua {len(skipped)} model không phải chat (ảnh, âm thanh, embedding...)")

    # 2. Gọi thử một câu ngắn
    def smoke(p):
        kn, m = p
        r = call(KEYS[kn], m, [{"role": "user", "content": "Trả lời đúng một từ tiếng Việt: xin chào"}], 300)
        return {"key": kn, "model": m, "ok": r["ok"] and bool((r.get("text") or "").strip()), "format": r.get("format"),
                "latency": round(r["latency"], 2), "reported_model": r.get("reported_model"),
                "text": (r.get("text") or "")[:80], "error": (r.get("error") or "")[:300]}
    log(f"[2] gọi thử {len(pairs)} cặp key–model...")
    with ThreadPoolExecutor(args.workers) as ex:
        smokes = list(ex.map(smoke, pairs))
    json.dump(smokes, open(os.path.join(RES, "smoke.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    alive = [s for s in smokes if s["ok"]]
    log(f"    chạy được: {len(alive)}/{len(smokes)}")
    for s in smokes:
        if not s["ok"]:
            log(f"    x {s['model']} [{s['key']}]: {s['error'][:140]}")

    # 3. Chấm điểm
    alive = sorted(alive, key=lambda s: s["latency"])[: args.max_models]
    log(f"[3] chấm {len(alive)} cặp (8 lời gọi mỗi cặp)...")
    with ThreadPoolExecutor(args.workers) as ex:
        recs = list(ex.map(lambda s: bench(s["key"], s["model"], s["format"], log), alive))
    recs.sort(key=lambda r: (-r["total"], r["latency_median"] or 999))
    with open(os.path.join(RES, "bench.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)

    lines = ["# Kết quả đo model qua cổng API", "",
             f"Trọng số: bám nguồn {WEIGHTS['bam_nguon']:.0%}, lập kế hoạch {WEIGHTS['lap_ke_hoach']:.0%}, gọi công cụ "
             f"{WEIGHTS['goi_cong_cu']:.0%}, tiếng Việt {WEIGHTS['tieng_viet']:.0%}, tính toán {WEIGHTS['tinh_toan']:.0%}. "
             "Mỗi bài chạy 1 lần; kết quả có dao động.", "",
             "| # | Model | Key | Tổng | Bám nguồn | Kế hoạch | Công cụ | Tiếng Việt | Tính toán | Trễ trung vị (s) | Token vào/ra | Lỗi | Model báo về |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for i, r in enumerate(recs, 1):
        sc = r["scores"]
        lines.append(f"| {i} | {r['model']} | {r['key']} | {r['total']:.2f} | {sc['bam_nguon']:.2f} | {sc['lap_ke_hoach']:.2f} | "
                     f"{sc['goi_cong_cu']:.2f} | {sc['tieng_viet']:.2f} | {sc['tinh_toan']:.2f} | {r['latency_median']} | "
                     f"{r['tokens_in']}/{r['tokens_out']} | {r['errors']} | {', '.join(r['reported_models'])} |")
    open(os.path.join(RES, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    log("[4] xong. Top 10:")
    for r in recs[:10]:
        log(f"    {r['total']:.2f}  {r['model']} [{r['key']}]  trễ {r['latency_median']}s")
    log(f"    Chi tiết: {os.path.join(RES, 'SUMMARY.md')}")


if __name__ == "__main__":
    sys.exit(main())
