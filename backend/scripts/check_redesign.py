"""Browser smoke review for Credere, using recordings and intercepted AI replies.

Run against an existing local server:
    python scripts/check_redesign.py --base http://127.0.0.1:8000

Saves viewport screenshots and report.json outside the repository. It blocks live
AI requests, provider writes/tests, and external network requests. A server with
replay_pace_s=0.01 makes this review faster without changing recorded content.
Without CREDERE_SETTINGS_PASSWORD it checks the locked settings page. Set that
environment variable to also inspect settings after login; it is never logged.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from playwright.sync_api import sync_playwright

SIZES = {"desktop": (1440, 1000), "laptop": (1366, 768), "mobile": (390, 844)}


def recording_path(directory: Path, app: str, question: str) -> Path:
    folded = unicodedata.normalize("NFD", question.lower().replace("đ", "d"))
    folded = "".join(c for c in folded if unicodedata.category(c) != "Mn")
    key = re.sub(r"[^a-z0-9]+", "-", folded).strip("-")[:120] or "cau-hoi"
    return directory / f"{'' if app == 'tuyen_sinh' else app + '--'}{key}.json"


def recording_features(directory: Path, app: str, question: str) -> dict:
    path = recording_path(directory, app, question)
    if not path.exists():
        return {"tables": 0, "nested": 0}
    data = json.loads(path.read_text(encoding="utf-8"))
    events = [row.get("event", {}) for row in data.get("events", [])]
    return {
        "tables": sum(e.get("event_type") == "data_table" and bool(e.get("detail", {}).get("rows")) for e in events),
        "nested": sum(e.get("event_type") == "sub_event" for e in events),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--out", type=Path, default=Path.home() / ".credere" / "ui-review" / datetime.now().strftime("%Y%m%d-%H%M%S"))
    parser.add_argument("--replay-dir", type=Path, default=Path.home() / ".credere" / "runs" / "demo-tuyen-sinh")
    parser.add_argument("--timeout", type=int, default=180000, help="Maximum milliseconds per recorded answer")
    parser.add_argument("--live-default-only", action="store_true", help="Only verify hidden replay controls and live defaults with intercepted requests")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    origin = urlparse(base)
    if origin.hostname not in {"localhost", "127.0.0.1", "::1"}:
        parser.error("Use a local server URL; this review is intended for local recorded data.")
    args.out.mkdir(parents=True, exist_ok=True)
    checks, problems, screenshots, downloads, skipped = [], [], [], [], []
    stage = {"name": "startup"}
    mock_live = {}
    mocked_requests = []
    settings_password = os.environ.get("CREDERE_SETTINGS_PASSWORD", "")

    def check(ok: bool, name: str, detail=None):
        checks.append({"ok": bool(ok), "name": name, **({"detail": detail} if detail is not None else {})})
        if not ok:
            problems.append(name)
        print(("PASS " if ok else "FAIL ") + name, flush=True)

    def shot(page, name: str):
        path = args.out / f"{name}.png"
        page.screenshot(path=str(path), animations="disabled")
        screenshots.append(str(path))

    def viewport(page, name: str):
        width, height = SIZES[name]
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_timeout(150)

    def layout(page, label: str, composer: bool = False):
        dims = page.evaluate("""() => ({width: innerWidth, scroll: document.documentElement.scrollWidth,
            body: document.body.scrollWidth})""")
        check(max(dims["scroll"], dims["body"]) <= dims["width"] + 1, f"{label}: no horizontal overflow", dims)
        if composer:
            box = page.locator("#q").bounding_box()
            height = page.viewport_size["height"]
            check(bool(box and box["y"] >= 0 and box["y"] + box["height"] <= height + 1),
                  f"{label}: composer visible in viewport", box)

    def get_json(page, path: str):
        return page.evaluate("async path => { const r = await fetch(path); if (!r.ok) throw Error(path + ': ' + r.status); return r.json(); }", path)

    def settings_checks(page, size):
        stage["name"] = f"settings-{size}"
        page.goto(base + "/cai-dat", wait_until="networkidle")
        page.locator("#settings-login-form").wait_for()
        check(page.locator("#settings-password").get_attribute("type") == "password"
              and page.locator("#settings-password").input_value() == "", f"settings {size}: locked password form")
        check(page.locator('#save, #list, input[data-k="base_url"], input[data-k="key"]').count() == 0,
              f"settings {size}: provider controls absent before authentication")
        layout(page, f"settings {size} locked")
        shot(page, stage["name"] + "-locked")
        if not settings_password:
            if not any(note.startswith("Authenticated settings") for note in skipped):
                skipped.append("Authenticated settings: set CREDERE_SETTINGS_PASSWORD to review provider controls")
            return
        status = page.evaluate("""async password => (await fetch('/api/settings/login', {
            method: 'POST', headers: {'Content-Type': 'application/json', 'X-Credere-Admin': '1'},
            body: JSON.stringify({password})
        })).status""", settings_password)
        check(status == 200, f"settings {size}: authenticated session created")
        if status != 200:
            return
        page.reload(wait_until="networkidle")
        page.locator("#save").wait_for()
        check(not any(page.locator('input[data-k="key"]').evaluate_all("els => els.map(e => e.value)")),
              f"settings {size}: stored provider keys absent from inputs")
        layout(page, f"settings {size} unlocked")
        page.evaluate("window.scrollTo(0, 0)")
        shot(page, stage["name"] + "-unlocked")
        status = page.evaluate("""async () => (await fetch('/api/settings/logout', {
            method: 'POST', headers: {'X-Credere-Admin': '1'}
        })).status""")
        check(status == 200, f"settings {size}: authenticated session closed")
        page.reload(wait_until="networkidle")
        check(page.locator("#settings-login-form").is_visible(), f"settings {size}: settings relocked after logout")

    def no_replay_ui(page, label, sample_count=None):
        check(page.locator('#mode, [data-mode="replay"], [data-mode="live"]').count() == 0,
              f"{label}: mode selector removed")
        check(not re.search(r"bản ghi|phát lại", page.locator("#welcome").inner_text(), re.I)
              and not re.search(r"bản ghi|phát lại", page.locator("#chips").text_content(), re.I)
              and page.locator(".cr-suggest .cr-has-rec, #chips .cr-pill--replay").count() == 0,
              f"{label}: welcome and suggestions have no recording labels")
        if sample_count is not None:
            stat = page.locator(".welcome-stat").nth(2)
            check(stat.locator("strong").inner_text() == str(sample_count)
                  and "Gợi ý công việc" in stat.inner_text(), f"{label}: work suggestions count includes every sample")

    def default_live_checks(page, apps):
        payload = {"report": "Phản hồi giả lập để kiểm tra mặc định giao diện; yêu cầu này không gọi dịch vụ AI.",
                   "status": {"T1": "accepted"}, "usage": None, "replayed": False}
        viewport(page, "desktop")
        for app in apps:
            key = app["key"]
            stage["name"] = f"{key}-live-default"
            page.goto(base + "/?" + urlencode({"app": key}), wait_until="networkidle")
            page.locator("#welcome").wait_for()
            samples = get_json(page, "/api/samples?" + urlencode({"app": key}))
            no_replay_ui(page, key, len(samples))
            check(page.evaluate("localStorage.getItem('credere-mode')") == "replay", f"{key}: stale replay preference present during check")
            shot(page, f"{key}-no-replay-welcome")
            for action in ("typed", "sample", "shift-sample", "popup", "shift-popup"):
                stage["name"] = f"{key}-{action}-default"
                page.goto(base + "/?" + urlencode({"app": key}), wait_until="networkidle")
                page.locator("#welcome").wait_for()
                question = f"UI QA live default {key}" if action == "typed" else samples[0]["q"]
                mock_live[question] = dict(payload)
                before = len(mocked_requests)
                if action == "typed":
                    page.locator("#q").fill(question)
                    page.locator("#send").click()
                else:
                    selector = ".cr-suggest"
                    if "popup" in action:
                        page.locator("#samples-btn").click()
                        selector = "#chips button"
                    page.locator(selector).first.click(modifiers=["Shift"] if action.startswith("shift") else [])
                page.locator("#messages .cr-foot:not([hidden])").wait_for()
                sent = mocked_requests[before:]
                check(len(sent) == 1 and sent[0]["mode"] == "live", f"{key}: {action} sends live despite stale replay preference", sent)
                mock_live.clear()

        for mode, label in (("replay", "explicit developer replay"), ("live", "server fallback")):
            question = "UI QA replay annotation " + mode
            stage["name"] = "annotation-" + mode
            mock_live[question] = {**payload, "replayed": True, "_qa_replay_event": {
                "recorded_at": "2026-09-29T12:00:00", "reason": "Recorded response simulated by browser QA"}}
            before = len(mocked_requests)
            page.goto(base + "/?" + urlencode({"app": apps[0]["key"], "q": question, "mode": mode}), wait_until="domcontentloaded")
            page.locator("#messages .cr-foot:not([hidden])").wait_for()
            check(len(mocked_requests[before:]) == 1 and mocked_requests[-1]["mode"] == mode, f"{label}: requested mode preserved")
            badge = page.locator("#messages .cr-tags .cr-pill--replay")
            check(badge.count() == 1 and "Phát lại" in badge.inner_text(), f"{label}: recorded answer honestly identified")
            mock_live.clear()

        viewport(page, "mobile")
        page.goto(base, wait_until="networkidle")
        page.locator("#welcome").wait_for()
        no_replay_ui(page, "mobile")
        layout(page, "mobile hidden-replay UI", composer=True)
        shot(page, "mobile-no-replay-welcome")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True, reduced_motion="reduce")
        context.add_init_script("localStorage.setItem('credere-mode', 'replay'); localStorage.removeItem('credere-trinh-chieu');")

        def protect(route):
            request = route.request
            parsed = urlparse(request.url)
            query = parse_qs(parsed.query)
            mock = mock_live.get(query.get("q", [""])[0])
            if parsed.path == "/api/ask" and mock is not None:
                mocked_requests.append({"app": query.get("app", [""])[0], "mode": query.get("mode", [""])[0]})
                payload = dict(mock)
                replay = payload.pop("_qa_replay_event", None)
                prefix = "event: replay\ndata: " + json.dumps(replay, ensure_ascii=False) + "\n\n" if replay else ""
                route.fulfill(status=200, content_type="text/event-stream", body=prefix + "event: done\ndata: " + json.dumps(payload, ensure_ascii=False) + "\n\n")
                return
            safe_origin = parsed.scheme in {"data", "blob"} or (parsed.hostname == origin.hostname and parsed.port == origin.port)
            is_replay = parsed.path != "/api/ask" or parse_qs(parsed.query).get("mode") == ["replay"]
            auth_post = bool(settings_password) and request.method == "POST" and parsed.path in {"/api/settings/login", "/api/settings/logout"}
            if not safe_origin or (request.method not in {"GET", "HEAD"} and not auth_post) or not is_replay:
                problems.append(f"{stage['name']}: blocked unsafe request {request.method} {parsed.path}")
                route.abort()
                return
            route.continue_()

        context.route("**/*", protect)
        page = context.new_page()
        page.set_default_timeout(15000)
        page.on("pageerror", lambda e: problems.append(f"{stage['name']}: JavaScript error: {e}"))
        page.on("console", lambda m: problems.append(f"{stage['name']}: console error: {m.text}") if m.type == "error" else None)
        page.on("response", lambda r: problems.append(f"{stage['name']}: HTTP {r.status}: {urlparse(r.url).path}") if r.status >= 400 else None)

        try:
            page.goto(base, wait_until="networkidle")
            apps = get_json(page, "/api/apps")
            check(bool(apps), "applications loaded")
            default_live_checks(page, apps)

            for size in SIZES if not args.live_default_only else ():
                viewport(page, size)
                page.goto(base, wait_until="networkidle")
                page.locator("#apps button").first.wait_for(state="attached")
                for app in apps:
                    key = app["key"]
                    stage["name"] = f"{key}-{size}-welcome"
                    if SIZES[size][0] <= 700:
                        page.locator("#menu-toggle").click()
                    buttons = page.locator("#apps button")
                    index = next(i for i, item in enumerate(apps) if item["key"] == key)
                    buttons.nth(index).click()
                    page.wait_for_function("key => localStorage.getItem('credere-app') === key", arg=key)
                    page.wait_for_function("name => document.title.includes(name)", arg=app["ten"])
                    page.locator("#q").wait_for(state="visible")
                    page.wait_for_timeout(120)
                    check(page.locator("#apps [aria-selected=true]").count() == 1, f"{key} {size}: exactly one role selected")
                    layout(page, f"{key} {size} welcome", composer=True)
                    shot(page, stage["name"])

                stage["name"] = f"suggestions-{size}"
                page.locator("#all-samples").click()
                expected_samples = get_json(page, "/api/samples?" + urlencode({"app": apps[-1]["key"]}))
                check(page.locator("#chips").is_visible() and page.locator("#chips button").count() == len(expected_samples),
                      f"suggestions {size}: all-samples button keeps full popup open")
                page.locator("#app-title").click()
                check(not page.locator("#chips").is_visible(), f"suggestions {size}: outside click closes popup")

                stage["name"] = f"library-{size}"
                if SIZES[size][0] <= 700:
                    page.locator("#menu-toggle").click()
                page.locator("#library-btn").click()
                check(page.locator("#library-dialog").is_visible(), f"library {size}: dialog opened")
                page.locator("#library-search").fill("TS-")
                ids = page.locator("#library-results .source-id").all_text_contents()
                check(bool(ids) and all(value.startswith("TS-") for value in ids), f"library {size}: source-code search filters results")
                layout(page, f"library {size}")
                shot(page, stage["name"])
                page.locator("#library-search").fill("ZZZ-unavailable-document-12345")
                check(page.locator("#library-results .library-item").count() == 0
                      and "Không tìm thấy" in page.locator("#library-results").inner_text(), f"library {size}: empty search state")
                page.locator("#library-close").click()
                check(not page.locator("#library-dialog").is_visible(), f"library {size}: dialog closed")
                no_replay_ui(page, f"welcome {size}")

                settings_checks(page, size)

            csv_checked = False
            for app in apps if not args.live_default_only else ():
                key = app["key"]
                stage["name"] = f"{key}-replay"
                page.goto(base, wait_until="networkidle")
                replays = get_json(page, "/api/replays?" + urlencode({"app": key}))
                if not replays:
                    skipped.append(f"{key}: no recordings available")
                    continue
                features = {q: recording_features(args.replay_dir, key, q) for q in replays}
                question = max(replays, key=lambda q: (features[q]["nested"] if app["delegates"] else features[q]["tables"]))
                viewport(page, "desktop")
                page.goto(base + "/?" + urlencode({"app": key, "mode": "replay", "q": question}), wait_until="domcontentloaded")
                page.wait_for_function("""() => [...document.querySelectorAll('#messages .cr-foot')].some(e => !e.hidden)
                    || /Phát lại xong/.test(document.querySelector('#run-state')?.textContent || '')""", timeout=args.timeout)
                check(page.locator("#messages").inner_text().find("Chưa có bản ghi") < 0, f"{key}: recording played")
                check(page.locator("#messages .cr-md").count() > 0 and len(page.locator("#messages .cr-md").last.inner_text()) > 80,
                      f"{key}: completed answer rendered")
                replay_badge = page.locator("#messages .cr-tags .cr-pill--replay")
                check(replay_badge.count() > 0 and bool(re.search(r"phát lại|bản ghi", replay_badge.first.inner_text(), re.I)),
                      f"{key}: recording identified")
                steps = page.locator("#panel").inner_text()
                check("Lập kế hoạch" in steps and "Nghiệm thu" in steps, f"{key}: planning and review steps rendered")
                if app["delegates"]:
                    check(page.locator("#panel .cr-lane").count() > 0, f"{key}: delegated AI steps nested")

                for size in SIZES:
                    viewport(page, size)
                    stage["name"] = f"{key}-{size}-answer"
                    if SIZES[size][0] <= 1000:
                        page.locator("#inspector-toggle").click()
                    page.locator("#tab-steps").click()
                    if SIZES[size][0] <= 1000:
                        page.locator("#inspector-close").click()
                    page.evaluate("document.querySelector('#messages').scrollTop = 0; window.scrollTo(0, 0)")
                    layout(page, f"{key} {size} answer")
                    shot(page, stage["name"])
                    if SIZES[size][0] <= 1000:
                        page.locator("#inspector-toggle").click()
                    sources_tab = page.locator("#tab-src")
                    check(sources_tab.is_enabled(), f"{key} {size}: sources tab enabled")
                    if sources_tab.is_enabled():
                        sources_tab.click()
                        check(page.locator("#sources").is_visible() and page.locator("#srclist li").count() > 0,
                              f"{key} {size}: cited sources displayed")
                        layout(page, f"{key} {size} sources")
                        shot(page, f"{key}-{size}-sources")
                    if SIZES[size][0] <= 1000:
                        page.locator("#inspector-close").click()

                csv = page.get_by_role("button", name=re.compile(r"CSV", re.I))
                if csv.count() and csv.first.is_enabled():
                    with page.expect_download() as pending:
                        csv.first.click()
                    download = pending.value
                    destination = args.out / f"{key}-sample.csv"
                    download.save_as(str(destination))
                    downloads.append(str(destination))
                    data = destination.read_bytes()
                    check(download.failure() is None and len(data) > 10 and b"\n" in data, f"{key}: CSV download contains rows")
                    csv_checked = True
                elif features[question]["tables"]:
                    check(False, f"{key}: populated recorded table has a CSV download button")

                stage["name"] = f"{key}-reset"
                page.locator("#menu-toggle").click()
                page.locator("#reset").click()
                check(page.locator("#welcome").is_visible() and page.locator("#messages .cr-answer").count() == 0,
                      f"{key}: new conversation clears answers")
                check(page.locator("#recent-requests button").count() == 0, f"{key}: new conversation clears recent requests")

            if not csv_checked and not args.live_default_only:
                skipped.append("CSV: no populated personal-table replay was available")

            # Fulfill these exact live requests inside Playwright; none reach the server.
            # This exercises finish() states that a successful saved replay cannot cover.
            viewport(page, "desktop")
            for name, status, expected in (() if args.live_default_only else (
                ("success", {"T1": "accepted"}, "Hoàn tất"),
                ("partial", {"T1": "accepted", "T2": "failed"}, "Hoàn tất một phần"),
                ("failed", {"T1": "failed"}, "Chưa có kết quả đạt"),
            )):
                stage["name"] = f"mock-live-{name}"
                question = f"UI QA mock live {name}"
                mock_live[question] = {"report": "Kết quả giả lập trong trình duyệt để kiểm tra giao diện; không gọi AI hoặc truy vấn dữ liệu.",
                                       "status": status, "usage": None, "replayed": False}
                page.goto(base + "/?" + urlencode({"app": apps[0]["key"]}), wait_until="networkidle")
                page.locator("#q").fill(question)
                page.locator("#send").click()
                page.wait_for_function("expected => document.querySelector('#run-state')?.textContent.trim() === expected", arg=expected)
                check(page.locator("#run-state").inner_text().strip() == expected, f"mock live {name}: correct completion state")
                check(page.locator("#q").is_enabled() and page.locator("#send").is_enabled(), f"mock live {name}: composer usable after completion")
                shot(page, stage["name"])
                mock_live.clear()
        except Exception as exc:
            problems.append(f"{stage['name']}: {type(exc).__name__}: {exc}")
            try:
                shot(page, "failure-" + stage["name"])
            except Exception:
                pass
        finally:
            browser.close()

    report = {"base": base, "checks": checks, "problems": list(dict.fromkeys(problems)), "skipped": skipped,
              "screenshots": screenshots, "downloads": downloads}
    (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{sum(c['ok'] for c in checks)}/{len(checks)} checks passed; {len(report['problems'])} problems. {args.out}")
    for problem in report["problems"]:
        print(" - " + problem)
    for note in skipped:
        print(" SKIP " + note)
    return int(bool(report["problems"]))


if __name__ == "__main__":
    raise SystemExit(main())
