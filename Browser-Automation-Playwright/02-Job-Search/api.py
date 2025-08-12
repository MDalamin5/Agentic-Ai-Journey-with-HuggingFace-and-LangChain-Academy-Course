# --- START OF FILE api.py ---

# ======================================================================
#  CRITICAL FIX FOR PLAYWRIGHT ON WINDOWS WITH FASTAPI/UVICORN
#  This MUST be at the very top of your main script.
# ======================================================================
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ======================================================================


from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
import traceback

app = FastAPI(
    title="Job Search API",
    description="An API to scrape job listings using Playwright."
)


async def search_job_on_bdjobs(keyword: str):
    """
    Launches a browser, searches for a job keyword on bdjobs.com, and returns a result dict.
    This function now runs directly inside the FastAPI process.
    """
    print(f"Starting in-process Playwright search for: {keyword}")
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
            print(f"✅ Search for '{keyword}' completed successfully.")

            return {
                "status": "ok",
                "keyword": keyword,
                "page_title": page_title,
                "job_count": job_count
            }

    except Exception as exc:
        # It's good practice to log the full error for debugging
        tb = traceback.format_exc()
        print(f"❌ An error occurred during search for '{keyword}':\n{tb}")
        return {
            "status": "error",
            "keyword": keyword,
            "error_message": str(exc),
        }


@app.get("/search-job/{keyword}")
async def run_job_search_endpoint(keyword: str):
    """
    Endpoint to perform a job search on bdjobs.com.
    """
    print(f"API endpoint called for keyword: '{keyword}'")
    result = await search_job_on_bdjobs(keyword)

    # If the scraping function returned an error, raise a 500 server error
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)

    return result