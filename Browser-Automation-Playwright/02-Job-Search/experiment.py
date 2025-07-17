import time
import asyncio
from playwright.async_api import async_playwright

async def search_job_on_bdjobs(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Go to Bdjobs homepage
        await page.goto("https://www.bdjobs.com/")

        # 2. Fill in the keyword
        await page.fill('input#txtKeyword', keyword)

        # 3. Click the search button
        await page.click('input[type="submit"][value="Search"]')

        # 4. Wait for navigation and display results
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        print("✅ Job search completed")

        # Optional: You can extract results here
        # jobs = await page.locator('your-job-selector').all_text_contents()
        # print(jobs)
        
        time.sleep(10)

        await browser.close()

# Run the function
asyncio.run(search_job_on_bdjobs("Data Science"))

