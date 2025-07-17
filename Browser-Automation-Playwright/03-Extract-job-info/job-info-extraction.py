from playwright.sync_api import sync_playwright, Page, TimeoutError
import re

def extract_job_data(page: Page):
    """Extracts job information from the current job listing page."""
    print("🔎 Starting job data extraction...")

    job_container_selector = ".featured-job, .norm-jobs-wrapper, .sout-jobs-wrapper"

    try:
        page.wait_for_selector(job_container_selector, timeout=15000)
    except TimeoutError:
        print("❌ Could not find job containers on the results page.")
        return []

    job_elements = page.query_selector_all(job_container_selector)
    print(f"✅ Found {len(job_elements)} job listings on this page.")

    jobs_data = []

    for job_element in job_elements:
        job = {}
        class_name = job_element.get_attribute('class') or ''
        is_featured = 'featured-job' in class_name

        if is_featured:
            title_ele = job_element.query_selector(".title a")
            location_ele = job_element.query_selector(".loccal > p")
            deadline_ele = job_element.query_selector("p.dt")
            experience_ele = job_element.query_selector(".exp.loccal > p:not(.dt)")
        else:
            title_ele = job_element.query_selector(".job-title-text a")
            location_ele = job_element.query_selector(".locon-text-d")
            deadline_ele = job_element.query_selector(".dead-text-d")
            experience_ele = job_element.query_selector(".exp-text-d")

        if title_ele:
            job['title'] = title_ele.inner_text().strip()
            job['details_link'] = title_ele.get_attribute('href')
        else:
            job['title'], job['details_link'] = "N/A", "N/A"

        if location_ele:
            job['location'] = location_ele.inner_text().strip()
        else:
            job['location'] = "N/A"

        if deadline_ele:
            full_text = deadline_ele.inner_text()
            job['deadline'] = re.sub(r'^\s*Deadline:\s*', '', full_text).strip()
        else:
            job['deadline'] = "N/A"

        if experience_ele:
            job['experience'] = experience_ele.inner_text().strip()
        else:
            job['experience'] = "N/A"
            
        jobs_data.append(job)
        
    return jobs_data

def search_job_on_bdjobs(keyword):
    """Launches browser, searches for a job, and extracts the results."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 Navigating to Bdjobs and searching for '{keyword}'...")
        page.goto("https://www.bdjobs.com/", timeout=60000)

        try:
            close_button_selector = "a.btn.close[href*='checkAssessmentCookie']"
            page.click(close_button_selector, timeout=5000)
            print("✓ Closed a promotional banner.")
        except TimeoutError:
            print("✓ No promotional banner to close.")

        page.fill('input#txtKeyword', keyword)
        
        # *** THE DEFINITIVE FIX IS HERE ***
        # This block listens for a new page to open because of target="_blank"
        print("⏳ Clicking search and listening for the new tab to open...")
        with context.expect_page() as new_page_info:
            page.click('input[type="submit"][value="Search"]')
        
        # Assign the new page object to a variable
        job_results_page = new_page_info.value
        print(f"✅ New tab opened successfully with URL: {job_results_page.url}")

        # It's crucial to wait for the new page to be fully loaded
        job_results_page.wait_for_load_state("domcontentloaded", timeout=30000)
        print("✅ New tab content has loaded.")

        # Now, all subsequent actions must be performed on `job_results_page`
        extracted_jobs = extract_job_data(job_results_page)

        print("\n--- Extracted Job Information ---")
        if not extracted_jobs:
            print("Could not find any jobs to display.")
        else:
            for i, job in enumerate(extracted_jobs, 1):
                print(f"\n--- Job {i} ---")
                print(f"  Title:      {job['title']}")
                print(f"  Link:       {job['details_link']}")
                print(f"  Location:   {job['location']}")
                print(f"  Deadline:   {job['deadline']}")
                print(f"  Experience: {job['experience']}")
        print("\n--- End of Extraction ---")

        browser.close()

if __name__ == "__main__":
    search_job_on_bdjobs("Data Science")