#!/usr/bin/env python
"""
Windows-safe async Playwright worker.
"""

import sys
import asyncio

# ✅ Set the correct loop policy immediately at process start
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import traceback
from playwright.async_api import async_playwright


async def run_search(keyword: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://www.bdjobs.com/", wait_until="domcontentloaded")
            await page.fill('input#txtKeyword', keyword)
            await page.click('input[type="submit"][value="Search"]')
            await page.wait_for_load_state("networkidle")

            page_title = await page.title()
            job_count = await page.locator(".job-title-text").count()

            await browser.close()

            return {
                "status": "ok",
                "keyword": keyword,
                "page_title": page_title,
                "job_count": job_count
            }

    except Exception as exc:
        tb = traceback.format_exc()
        return {
            "status": "error",
            "keyword": keyword,
            "error": str(exc),
            "traceback": tb
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "missing keyword"}))
        sys.exit(2)

    kw = sys.argv[1]
    result = asyncio.run(run_search(kw))
    print(json.dumps(result))
