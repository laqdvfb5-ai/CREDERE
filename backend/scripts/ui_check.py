"""Kiểm tra trang demo trước giờ trình diễn: mở từng AI, phát lại mọi câu mẫu có bản ghi, mở trang Cài đặt; chụp màn hình.

    python scripts/ui_check.py [--base http://127.0.0.1:8000] [--out thư_mục] [--fast]

Chỉ dùng chế độ phát lại: mọi /api/ask không có mode=replay đều bị chặn, nên không gọi AI thật, không tốn phí.
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


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--out", default=str(Path.home() / ".credere" / "runs" / f"ui_check_{datetime.now():%Y%m%d-%H%M}"))
    ap.add_argument("--fast", action="store_true", help="chỉ phát lại câu mẫu đầu tiên của mỗi AI")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    host = urlparse(args.base).hostname
    problems, checks, shots = [], [], []

    def check(ok: bool, what: str) -> None:
        checks.append({"ok": bool(ok), "what": what})
        if not ok:
            problems.append(what)
        print(("ĐẠT  " if ok else "TRƯỢT ") + what)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")

        def page_at(size: str):
            pg = browser.new_page(viewport=dict(zip(("width", "height"), SIZES[size])))
            pg.on("console", lambda m: m.type == "error" and problems.append(f"lỗi console: {m.text}"))
            pg.on("pageerror", lambda e: problems.append(f"lỗi JS: {e}"))
            pg.on("response", lambda r: r.status >= 400 and problems.append(f"HTTP {r.status}: {r.url}"))
            pg.on("request", lambda r: urlparse(r.url).hostname not in (host, None) and not r.url.startswith("data:")
                  and problems.append(f"request ra ngoài: {r.url}"))
            # lưới an toàn: không bao giờ chạy thật trong lúc kiểm tra
            pg.route("**/api/ask*", lambda route: route.continue_() if "mode=replay" in route.request.url else route.abort())
            return pg

        def shot(pg, name: str) -> None:
            path = out / f"{name}.png"
            pg.screenshot(path=str(path))
            shots.append(str(path))

        pg = page_at("1366")
        pg.goto(args.base)
        apps = pg.evaluate("fetch('/api/apps').then(r => r.json())")
        for a in apps:
            key = a["key"]
            for size in SIZES:
                pg.set_viewport_size(dict(zip(("width", "height"), SIZES[size])))
                pg.goto(f"{args.base}/?app={key}")
                pg.wait_for_selector(".cr-suggest", timeout=15000)
                pg.wait_for_timeout(400)
                shot(pg, f"{key}_chao_{size}")
                check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{key} {size}: không tràn ngang")
                box = pg.locator("#q").bounding_box()
                check(box is not None and box["y"] + box["height"] <= SIZES[size][1], f"{key} {size}: ô nhập nằm trong màn hình")
            pg.set_viewport_size(dict(zip(("width", "height"), SIZES["1366"])))
            replays = pg.evaluate(f"fetch('/api/replays?app={key}').then(r => r.json())")
            samples = pg.evaluate(f"fetch('/api/samples?app={key}').then(r => r.json())")
            check(len(replays) == len(samples), f"{key}: {len(replays)}/{len(samples)} câu mẫu có bản ghi")
            for i, q in enumerate(replays[:1] if args.fast else replays):
                pg.goto(f"{args.base}/?app={key}&mode=replay&q={quote(q)}")
                if i == 0:
                    pg.wait_for_timeout(6000)
                    shot(pg, f"{key}_{i + 1}_giua_chung")
                pg.wait_for_selector(".cr-foot:not([hidden])", timeout=150000)
                name = f"{key} câu {i + 1}"
                check(pg.locator(".cr-tags .cr-pill--replay").count() == 1, f"{name}: có nhãn phát lại")
                check(len(pg.inner_text(".cr-md")) > 80, f"{name}: có câu trả lời")
                steps = pg.inner_text("#panel")
                check("Lập kế hoạch" in steps and "Nghiệm thu" in steps, f"{name}: quy trình có lập kế hoạch và nghiệm thu")
                if a["delegates"]:
                    check(pg.locator("#panel .cr-lane").count() >= 1, f"{name}: có khung bước của AI con")
                pg.evaluate("document.querySelector('.cr-msg--user').scrollIntoView({block: 'start'})")
                pg.wait_for_timeout(300)
                shot(pg, f"{key}_{i + 1}_xong")

        pg.goto(f"{args.base}/cai-dat")
        pg.wait_for_timeout(1500)
        shot(pg, "cai_dat_1366")
        check(pg.locator("input[type=password]").count() >= 1, "Cài đặt: ô khóa là ô mật khẩu")
        check(not any(v for v in pg.eval_on_selector_all("input[type=password]", "els => els.map(e => e.value)")), "Cài đặt: ô khóa để trống")
        browser.close()

    report = {"base": args.base, "checks": checks, "problems": problems, "screenshots": shots}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{sum(c['ok'] for c in checks)}/{len(checks)} mục đạt; {len(problems)} vấn đề. Ảnh và report.json: {out}")
    for x in dict.fromkeys(problems):
        print("  -", x)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
