"""Kiểm tra giao diện trước khi trình bày: mở từng AI, cho trang chạy một lượt hỏi, mở trang Cài đặt; chụp màn hình.

    python scripts/ui_check.py [--base http://127.0.0.1:8000] [--records thư_mục] [--out thư_mục]

Không gọi AI thật, không tốn phí: mọi yêu cầu /api/ask bị chặn trong trình duyệt và trả lời bằng sự kiện của một hồ sơ lượt chạy
đã lưu (mặc định ~/.credere/runs/web, nơi trang lưu hồ sơ mỗi lượt chạy). Đây chỉ là dữ liệu kiểm thử giao diện; trang thật luôn chạy thật.
Cần server đang chạy (python -m app.web) và Chrome trên máy (Playwright dùng Chrome có sẵn).
Báo lỗi console, request lỗi, request ra ngoài máy, thiếu bước quy trình; in ĐẠT/TRƯỢT và ghi report.json cạnh ảnh.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

from playwright.sync_api import sync_playwright

SIZES = {"1366": (1366, 768), "1920": (1920, 1080)}
RUNS = Path.home() / ".credere" / "runs"


def pick_record(folder: Path, key: str) -> dict | None:
    """Hồ sơ mới nhất của AI này có kế hoạch và câu trả lời (bỏ lượt trả lời ngay không có nhiệm vụ)."""
    for path in sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("app") == key and (rec.get("done") or {}).get("report") and any(
                i["event"]["event_type"] == "plan_saved" and i["event"]["detail"]["tasks"] for i in rec.get("events") or []):
            return rec
    return None


def sse_body(rec: dict) -> str:
    out = [f"event: event\ndata: {json.dumps(i['event'], ensure_ascii=False)}\n\n" for i in rec["events"]]
    return "".join(out) + f"event: done\ndata: {json.dumps(rec['done'], ensure_ascii=False)}\n\n"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--records", default=str(RUNS / "web"), help="thư mục hồ sơ lượt chạy dùng làm dữ liệu kiểm thử")
    ap.add_argument("--out", default=str(RUNS / f"ui_check_{datetime.now():%Y%m%d-%H%M}"))
    args = ap.parse_args()
    out, records = Path(args.out), Path(args.records)
    out.mkdir(parents=True, exist_ok=True)
    host = urlparse(args.base).hostname
    problems, checks, shots, skipped = [], [], [], []

    def check(ok: bool, what: str) -> None:
        checks.append({"ok": bool(ok), "what": what})
        if not ok:
            problems.append(what)
        print(("ĐẠT  " if ok else "TRƯỢT ") + what)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        stream = {"body": None}

        def on_ask(route):
            # không bao giờ chạy thật trong lúc kiểm tra: chỉ trả sự kiện của hồ sơ đã chọn, không có hồ sơ thì chặn
            if stream["body"] is None:
                route.abort()
            else:
                route.fulfill(status=200, headers={"Content-Type": "text/event-stream; charset=utf-8"}, body=stream["body"])

        pg = browser.new_page(viewport=dict(zip(("width", "height"), SIZES["1366"])))
        pg.on("console", lambda m: m.type == "error" and problems.append(f"lỗi console: {m.text}"))
        pg.on("pageerror", lambda e: problems.append(f"lỗi JS: {e}"))
        pg.on("response", lambda r: r.status >= 400 and problems.append(f"HTTP {r.status}: {r.url}"))
        pg.on("request", lambda r: urlparse(r.url).hostname not in (host, None) and not r.url.startswith("data:")
              and problems.append(f"request ra ngoài: {r.url}"))
        pg.route("**/api/ask*", on_ask)

        def shot(name: str) -> None:
            path = out / f"{name}.png"
            pg.screenshot(path=str(path))
            shots.append(str(path))

        pg.goto(args.base)
        apps = pg.evaluate("fetch('/api/apps').then(r => r.json())")
        for a in apps:
            key = a["key"]
            for size in SIZES:
                pg.set_viewport_size(dict(zip(("width", "height"), SIZES[size])))
                pg.goto(f"{args.base}/?app={key}")
                pg.wait_for_selector(".cr-suggest", timeout=15000)
                pg.wait_for_timeout(400)
                shot(f"{key}_chao_{size}")
                check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{key} {size}: không tràn ngang")
                box = pg.locator("#q").bounding_box()
                check(box is not None and box["y"] + box["height"] <= SIZES[size][1], f"{key} {size}: ô nhập nằm trong màn hình")
            pg.set_viewport_size(dict(zip(("width", "height"), SIZES["1366"])))
            check(pg.locator("[data-mode], #mode, .cr-pill--replay").count() == 0, f"{key}: không còn điều khiển phát lại")
            rec = pick_record(records, key)
            if rec is None:
                skipped.append(f"{key}: chưa có hồ sơ lượt chạy trong {records}, bỏ qua kiểm tra luồng hỏi đáp")
                print("BỎ QUA " + skipped[-1])
                continue
            stream["body"] = sse_body(rec)
            pg.goto(f"{args.base}/?app={key}&q={quote(rec['question'])}")
            pg.wait_for_selector(".cr-foot:not([hidden])", timeout=60000)
            name = f"{key}: {rec['question'][:50]}"
            check(len(pg.inner_text(".cr-md")) > 80, f"{name}: có câu trả lời")
            steps = pg.inner_text("#panel")
            check("Lập kế hoạch" in steps and "Nghiệm thu" in steps, f"{name}: quy trình có lập kế hoạch và nghiệm thu")
            if a["delegates"]:
                check(pg.locator("#panel .cr-lane").count() >= 1, f"{name}: có khung bước của AI con")
            pg.evaluate("document.querySelector('.cr-msg--user').scrollIntoView({block: 'start'})")
            pg.wait_for_timeout(300)
            shot(f"{key}_xong")
            stream["body"] = None

        pg.goto(f"{args.base}/cai-dat")
        pg.wait_for_timeout(1500)
        shot("cai_dat_1366")
        check(pg.locator("input[type=password]").count() >= 1, "Cài đặt: ô khóa là ô mật khẩu")
        check(not any(v for v in pg.eval_on_selector_all("input[type=password]", "els => els.map(e => e.value)")), "Cài đặt: ô khóa để trống")
        browser.close()

    report = {"base": args.base, "records": str(records), "checks": checks, "problems": problems, "skipped": skipped, "screenshots": shots}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{sum(c['ok'] for c in checks)}/{len(checks)} mục đạt; {len(problems)} vấn đề; {len(skipped)} mục bỏ qua. Ảnh và report.json: {out}")
    for x in dict.fromkeys(problems):
        print("  -", x)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
