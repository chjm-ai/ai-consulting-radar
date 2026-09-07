"""打开一个真实(有头)浏览器窗口让用户手动登录 x.com,登录成功后自动导出 cookie
到 data/x_cookies_default.json,供 TwitterPlaywrightScraper 使用。

用法: uv run python3 scripts/x_login_export_cookies.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "x_cookies_default.json"
SHOT_PATH = Path("/tmp/x-login-logs/screenshot.png")
LOGIN_TIMEOUT_SEC = 900


def _get_proxy() -> str:
    for key in ("PROXY", "https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy"):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return ""


async def main():
    proxy = _get_proxy()
    async with Stealth().use_async(async_playwright()) as p:
        launch_kwargs = {"headless": False}
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}
            print(f"使用代理: {proxy}", file=sys.stderr)
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="Asia/Shanghai",
        )
        page = await context.new_page()
        await page.goto("https://x.com/login", wait_until="domcontentloaded")

        print(f"\n浏览器窗口已打开,请在里面登录你的 X 账号。", file=sys.stderr)
        print(f"登录完成后脚本会自动检测并导出 cookie(最多等待 {LOGIN_TIMEOUT_SEC}s)。\n", file=sys.stderr)

        SHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

        deadline = time.time() + LOGIN_TIMEOUT_SEC
        logged_in = False
        tick = 0
        while time.time() < deadline:
            cookies = await context.cookies()
            names = {c["name"] for c in cookies}
            # auth_token only appears after a successful login
            if "auth_token" in names:
                logged_in = True
                break
            if tick % 3 == 0:
                try:
                    await page.screenshot(path=str(SHOT_PATH))
                except Exception as exc:
                    print(f"截图失败: {exc}", file=sys.stderr)
            tick += 1
            await asyncio.sleep(2)

        if not logged_in:
            print("超时未检测到登录态,未导出 cookie。可重新运行脚本重试。", file=sys.stderr)
            await browser.close()
            sys.exit(1)

        # Let the session settle a moment after login redirect
        await asyncio.sleep(2)
        cookies = await context.cookies()

        out = []
        for c in cookies:
            if "twitter.com" not in c["domain"] and "x.com" not in c["domain"]:
                continue
            out.append(
                {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c["domain"],
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False),
                    "expirationDate": c.get("expires"),
                }
            )

        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

        print(f"登录成功,已导出 {len(out)} 条 cookie 到 {OUT_PATH}", file=sys.stderr)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
