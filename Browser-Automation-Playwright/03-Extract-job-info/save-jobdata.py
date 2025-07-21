# We need the 'csv' module to write to a CSV file
import csv
import re
from playwright.sync_api import sync_playwright, Page, TimeoutError

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
            # Ensure the link is absolute
            relative_link = title_ele.get_attribute('href')
            if relative_link and not relative_link.startswith('http'):
                job['details_link'] = "https://jobs.bdjobs.com/" + relative_link.lstrip('/')
            else:
                job['details_link'] = relative_link
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

def save_jobs_to_csv(jobs_data, keyword):
    """Saves a list of job dictionaries to a CSV file."""
    if not jobs_data:
        print("❌ No job data to save.")
        return
        
    # Sanitize the keyword to create a valid filename
    safe_keyword = re.sub(r'[^a-zA-Z0-9\s]', '', keyword).replace(' ', '_').lower()
    filename = f"{safe_keyword}_jobs.csv"
    
    print(f"\n💾 Saving {len(jobs_data)} jobs to '{filename}'...")

    # Define the headers for the CSV file. They must match the dictionary keys.
    fieldnames = ['title', 'details_link', 'location', 'deadline', 'experience']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # DictWriter is perfect for writing a list of dictionaries
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Write all the job data rows
            writer.writerows(jobs_data)
        
        print(f"✅ Data successfully saved to '{filename}'.")
    except IOError as e:
        print(f"❌ Error writing to file '{filename}': {e}")


def search_job_on_bdjobs(keyword):
    """Launches browser, searches for a job, and saves the results to a CSV file."""
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
        
        print("⏳ Clicking search and listening for the new tab to open...")
        with context.expect_page() as new_page_info:
            page.click('input[type="submit"][value="Search"]')
        
        job_results_page = new_page_info.value
        print(f"✅ New tab opened successfully with URL: {job_results_page.url}")

        job_results_page.wait_for_load_state("domcontentloaded", timeout=30000)
        print("✅ New tab content has loaded.")

        extracted_jobs = extract_job_data(job_results_page)
        
        # --- MODIFIED PART: Save to CSV instead of printing ---
        save_jobs_to_csv(extracted_jobs, keyword)
        # --- END OF MODIFICATION ---

        print("\n--- Scraper finished ---")
        browser.close()

if __name__ == "__main__":
    search_job_on_bdjobs("Data Science")