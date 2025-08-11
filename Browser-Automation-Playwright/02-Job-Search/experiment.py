# ======================================================================
# Windows-specific asyncio fix for Playwright
# This MUST also be here for standalone runs
# ======================================================================
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ======================================================================
from playwright.async_api import async_playwright

async def search_job_on_bdjobs(keyword: str):
    """
    Launches a browser, searches for a job keyword on bdjobs.com, and returns a status.
    """
    print(f"Starting Playwright to search for: {keyword}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Change to True for headless mode
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Go to Bdjobs homepage
            await page.goto("https://www.bdjobs.com/", wait_until="domcontentloaded")

            # 2. Fill in the keyword
            await page.fill('input#txtKeyword', keyword)

            # 3. Click the search button
            await page.click('input[type="submit"][value="Search"]')

            # 4. Wait for results to load
            await page.wait_for_load_state('networkidle')

            # Page title confirmation
            page_title = await page.title()
            print(f"✅ Job search completed. Landed on page: '{page_title}'")

            await asyncio.sleep(2)

            job_listings = await page.locator(".job-title-text").count()
            print(f"Found {job_listings} job listings on the first page.")

            await browser.close()
            return f"Search for '{keyword}' completed successfully. Found {job_listings} jobs on the first page."

        except Exception as e:
            print(f"An error occurred: {e}")
            await browser.close()
            return f"An error occurred during the search for '{keyword}'."


async def main(keyword):
    print("call_main====")
    result = await search_job_on_bdjobs(keyword)
    return result


if __name__ == "__main__":
    results = asyncio.run(main(keyword="python"))
    print(results)
