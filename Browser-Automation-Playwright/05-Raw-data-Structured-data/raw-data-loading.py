import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def get_raw_job_data_from_url(url: str) -> str | None:
    """
    Navigates to a bdjobs.com URL, extracts the raw text content from the 
    main job details block, and stops before the "Report Job" section.

    Args:
        url: The URL of the job posting.

    Returns:
        A single string containing the clean, raw text of the job details,
        or None if an error occurs.
    """
    print(f"Attempting to scrape raw job data from: {url}")
    
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to the live URL
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # This locator points to the high-level container that holds the job details.
            # It's a stable choice that contains the content we need plus the report section.
            main_container = page.locator("div.min-h-screen")
            
            # Wait for the container to be visible to ensure it's fully loaded
            await main_container.wait_for(state="visible", timeout=10000)

            print("Located main content container. Extracting and cleaning text...")

            # Get all the text from inside this container
            full_text = await main_container.inner_text()
            
            # Define the text that marks the beginning of the section we want to exclude.
            # This is a very reliable way to "cut off" the content.
            delimiter = "Report this Job / Company"
            
            # Split the full text at the delimiter and take only the part before it.
            if delimiter in full_text:
                raw_job_text = full_text.split(delimiter, 1)[0].strip()
            else:
                # Fallback in case the report section isn't found
                print("Warning: Delimiter 'Report this Job / Company' not found. Returning all text from the container.")
                raw_job_text = full_text.strip()
            
            await browser.close()
            return raw_job_text

        except PlaywrightTimeoutError:
            print(f"Error: Timed out. The page at {url} might be down or the content container was not found.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if 'browser' in locals() and not browser.is_closed():
                 await browser.close()
            return None

async def main():
    # The target URL for the job posting
    link = "https://jobs.bdjobs.com/jobdetails/?id=1386448&ln=1&JobKeyword=Data%20Science"
    
    raw_job_content = await get_raw_job_data_from_url(link)
    
    if raw_job_content:
        print("\n" + "="*50)
        print("--- START OF EXTRACTED RAW JOB CONTENT ---")
        print("="*50 + "\n")
        
        print(raw_job_content)
        
        print("\n" + "="*50)
        print("--- END OF EXTRACTED RAW JOB CONTENT ---")
        print("="*50)
    else:
        print("\nCould not retrieve job content.")

if __name__ == "__main__":
    asyncio.run(main())