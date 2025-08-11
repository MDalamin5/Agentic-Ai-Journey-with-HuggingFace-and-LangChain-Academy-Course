# ======================================================================
# Windows-specific asyncio fix for Playwright
# This MUST be at the very top of the entry file
# ======================================================================
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ======================================================================
from fastapi import FastAPI
from experiment import main  # import after fixing loop policy

app = FastAPI(
    title="Job Search API",
    description="An API to scrape job listings using Playwright."
)


@app.get("/search-job/{keyword}")
async def run_job_search(keyword: str):
    """
    Performs a job search on bdjobs.com for the given keyword.
    Example: /search-job/python_developer
    """
    print(f"API endpoint called. Triggering Playwright function for keyword: '{keyword}'")
    response_message = await main(keyword)
    return {
        "status": "completed",
        "message": response_message
    }
