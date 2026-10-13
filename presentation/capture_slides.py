"""Capture the real Credere UI for presentation slides without calling any models.

Run with the project's existing Python environment, from any directory:
    python presentation/capture_slides.py --base-url http://127.0.0.1:8001

Welcome pages use the current normal UI. Answer pages explicitly replay existing
successful recordings and retain their replay/date labels. All writes, provider
endpoints, external requests, and non-replay /api/ask requests are blocked.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parent
DEFAULT_RECORDINGS = Path.home() / ".credere" / "runs" / "demo-tuyen-sinh"
VIEWPORT = {"width": 1440, "height": 900}
RECORDING_PATTERNS = {
    "tuyen_sinh": "den-gio-co-bao-nhieu-thi-sinh-da-xac-nhan-nhap-hoc-*.json",
    "dao_tao": "dao_tao--hoc-ky-2-nam-hoc-2025-2026-co-bao-nhieu-sinh-vien-*.json",
    "hieu_truong": "hieu_truong--nganh-nao-dang-thieu-nhieu-chi-tieu-tuyen-sinh-*.json",
}
SLUGS = {"tuyen_sinh": "admissions", "dao_tao": "academic", "hieu_truong": "principal"}


def walk_events(event: dict):
    yield event
    if event.get("event_type") == "sub_event":
        yield from walk_events(event["detail"]["event"])


def read_recordings(directory: Path) -> dict[str, dict]:
    recordings = {}
    for app, pattern in RECORDING_PATTERNS.items():
        candidates = sorted(directory.glob(pattern))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected exactly one recording for {app}; found {len(candidates)}.")
        path = candidates[0]
        raw = path.read_bytes()
        record = json.loads(raw.decode("utf-8"))
        if record.get("app") != app:
            raise RuntimeError(f"Wrong application in recording: {path.name}")
        statuses = record.get("done", {}).get("status", {})
        if not statuses or any(status != "accepted" for status in statuses.values()):
            raise RuntimeError(f"Recording has incomplete tasks: {path.name}")
        # Use aggregate-only examples; never include person-level data table events.
        for item in record.get("events", []):
            if any(e.get("event_type") == "data_table" for e in walk_events(item["event"])):
                raise RuntimeError(f"Recording contains a data table; choose an aggregate example: {path.name}")
        recordings[app] = {
            "question": record["question"],
            "recorded_at": record["recorded_at"],
            "recording_file": str(path),
            "recording_sha256": hashlib.sha256(raw).hexdigest(),
            "task_status": statuses,
            "event_count": len(record["events"]),
            "original_elapsed_s": record.get("done", {}).get("elapsed_s"),
            "original_run_used_synthetic_data": True,
            "delegates": sorted({
                item["event"]["detail"]["app"]
                for item in record["events"]
                if item["event"].get("event_type") == "sub_event"
            }),
        }
    return recordings


async def capture(args) -> None:
    args.output.mkdir(parents=True, exist_ok=True)
    recordings = read_recordings(args.recordings)
    base_url = args.base_url.rstrip("/")
    server = urlsplit(base_url)
    blocked = []
    browser_errors = []
    screenshots = []
    allowed_replays = {(app, record["question"]) for app, record in recordings.items()}

    async def guard(route):
        request = route.request
        target = urlsplit(request.url)
        reason = None
        if (target.scheme, target.netloc) != (server.scheme, server.netloc):
            reason = "external request"
        elif request.method not in {"GET", "HEAD"}:
            reason = "write request"
        elif target.path.startswith(("/api/providers", "/api/settings")):
            reason = "settings or provider endpoint"
        elif target.path == "/api/ask":
            params = parse_qs(target.query)
            app = params.get("app", [""])[0]
            question = params.get("q", [""])[0]
            if params.get("mode") != ["replay"] or (app, question) not in allowed_replays:
                reason = "unapproved or live model request"
        if reason:
            blocked.append({"path": target.path, "method": request.method, "reason": reason})
            await route.abort()
        else:
            await route.continue_()

    async with async_playwright() as playwright:
        chrome = args.chrome
        if chrome is None:
            chrome = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe"
        browser = await playwright.chromium.launch(executable_path=str(chrome), headless=True)
        context = await browser.new_context(viewport=VIEWPORT, device_scale_factor=1, reduced_motion="reduce")
        await context.route("**/*", guard)

        async def new_page():
            page = await context.new_page()
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            return page

        async def shot(page, filename, kind, app=None, record=None, detail=None):
            await page.evaluate("document.activeElement?.blur()")
            await page.evaluate("document.fonts.ready")
            await page.screenshot(path=str(args.output / filename), full_page=False, animations="disabled")
            entry = {
                "file": filename,
                "kind": kind,
                "app": app,
                "dimensions": dict(VIEWPORT),
                "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "page_url": page.url,
                "provenance": "current local application rendered by Chromium; no DOM content replaced",
                "replay": record is not None,
            }
            if record:
                entry.update(record)
                entry["replay_label"] = await page.locator("#run-state").inner_text()
                entry["recorded_time_banner"] = await page.locator(".cr-tags").last.inner_text()
            if detail:
                entry["view_detail"] = detail
            screenshots.append(entry)
            print(f"Captured {filename}", flush=True)

        # Each page uses a new tab and an explicit app parameter. There is no live
        # question in the URL and nothing is submitted on these welcome pages.
        for app, slug in SLUGS.items():
            page = await new_page()
            await page.goto(f"{base_url}/?{urlencode({'app': app})}", wait_until="networkidle")
            await page.locator("#welcome").wait_for(state="visible")
            if await page.locator("[data-mode], #mode").count():
                raise RuntimeError("Welcome page still contains the removed mode selector.")
            await shot(page, f"welcome-{slug}.png", "welcome", app=app)
            await page.close()

        for app, slug in SLUGS.items():
            record = recordings[app]
            page = await new_page()
            query = urlencode({"app": app, "mode": "replay", "q": record["question"]})
            await page.goto(f"{base_url}/?{query}", wait_until="domcontentloaded")
            await page.wait_for_function(
                "document.getElementById('run-state')?.textContent.trim() === 'Phát lại xong'",
                timeout=120_000,
            )
            if await page.locator(".cr-dt").count():
                raise RuntimeError("A person-level table appeared in an aggregate screenshot.")
            await page.locator("#messages").evaluate("el => { el.scrollTop = 0; }")
            await page.locator("#panel").evaluate("el => { el.scrollTop = 0; }")
            await shot(page, f"answer-{slug}.png", "recorded_answer", app=app, record=record,
                       detail="Top of the original recorded answer; viewport excerpt, with replay banner and synthetic-data label.")

            if app == "hieu_truong":
                await page.locator("#tab-steps").click()
                for delegate in record["delegates"]:
                    lane = page.locator(f".cr-lane.cr-agent--ai_{delegate}").first
                    await lane.wait_for(state="visible")
                    await lane.evaluate("""lane => {
                        const panel = document.getElementById('panel');
                        panel.scrollTop += lane.getBoundingClientRect().top - panel.getBoundingClientRect().top - 8;
                    }""")
                    filename = "process-principal.png" if delegate == "dao_tao" else f"process-principal-{SLUGS[delegate]}.png"
                    await shot(page, filename, "nested_agent_process",
                               app=app, record=record,
                               detail=f"Activity panel scrolled naturally to the {delegate} child-agent lane; recorded events unchanged.")
            await page.close()

        # New browser context has no authentication cookie. Never attempt login.
        page = await new_page()
        await page.goto(f"{base_url}/cai-dat", wait_until="networkidle")
        await page.locator("#settings-password").wait_for(state="visible")
        if await page.locator("[data-k=key], #list .cr-prov").count():
            raise RuntimeError("Settings capture unexpectedly contains provider configuration.")
        await shot(page, "settings-locked.png", "password_gate",
                   detail="Locked settings page in a fresh unauthenticated browser context; no passwords entered.")
        await browser.close()

    metadata = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "base_url": base_url,
        "dimensions": VIEWPORT,
        "capture_policy": {
            "live_model_requests_allowed": False,
            "writes_allowed": False,
            "settings_api_allowed": False,
            "external_requests_allowed": False,
            "answer_source": "existing local recordings, replayed through the real server and labeled by the real UI",
            "personal_data_tables_included": False,
            "synthetic_data_notice_preserved": True,
        },
        "blocked_requests": blocked,
        "browser_errors": browser_errors,
        "screenshots": screenshots,
    }
    (args.output / "screenshots.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if browser_errors:
        raise RuntimeError(f"Browser reported {len(browser_errors)} JavaScript error(s); see screenshots.json.")
    print(f"Saved {len(screenshots)} screenshots and screenshots.json", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8001")
    parser.add_argument("--output", type=Path, default=ROOT / "shots" / "current")
    parser.add_argument("--recordings", type=Path, default=DEFAULT_RECORDINGS)
    parser.add_argument("--chrome", type=Path)
    asyncio.run(capture(parser.parse_args()))


if __name__ == "__main__":
    main()
