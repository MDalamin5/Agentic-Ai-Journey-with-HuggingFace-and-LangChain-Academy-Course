import asyncio
from playwright.async_api import async_playwright

async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    
    link = "https://jobs.bdjobs.com/jobdetails/?id=1375785&ln=1&JobKeyword=machine%20learning%20enginner"
    await page.goto(link)
    h1_text = await page.inner_text("body")
    print("Extracted H1:", h1_text)

    await browser.close()
    await playwright.stop()  # ✅ Important: Clean shutdown to avoid warnings

asyncio.run(main())
