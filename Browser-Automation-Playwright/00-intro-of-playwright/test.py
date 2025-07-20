import asyncio
from playwright.async_api import async_playwright
import time


async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    
    link = "https://linkedin.com/"
    await page.goto(link)
    await page.click("text=Sign in")
    # h1_text = await page.inner_text("body")
    # print("Extracted H1:", h1_text)

    
    time.sleep(5)
    await browser.close()
    await playwright.stop()  # ✅ Important: Clean shutdown to avoid warnings

asyncio.run(main())

