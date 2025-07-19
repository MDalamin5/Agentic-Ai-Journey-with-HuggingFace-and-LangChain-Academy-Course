from playwright.sync_api import sync_playwright, Page, TimeoutError
import re
import csv
import os

def save_to_csv(jobs_list, filename="jobs.csv"):
    """Saves a list of job dictionaries to a CSV file."""
    
    # If no jobs were found, don't create a file.
    if not jobs_list:
        print("No job data to save.")
        return

    # Define the headers for the CSV file based on the keys of the first job dictionary
    headers = jobs_list[0].keys()
    
    # Using 'with' ensures the file is properly closed even if errors occur
    # newline='' prevents extra blank rows from being created
    # encoding='utf-8' is important for handling special characters
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # DictWriter is convenient as it works directly with our list of dictionaries
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        
        # Write the header row
        writer.writeheader()
        
        # Write all the job data rows
        writer.writerows(jobs_list)
        
    print(f"✅ Successfully saved {len(jobs_list)} jobs to {filename}")

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
            company_ele = job_element.query_selector(".company")
            logo_ele = job_element.query_selector(".logo img")
            location_ele = job_element.query_selector(".loccal > p")
            deadline_ele = job_element.query_selector("p.dt")
            experience_ele = job_element.query_selector(".exp.loccal > p:not(.dt)")
        else:
            title_ele = job_element.query_selector(".job-title-text a")
            company_ele = job_element.query_selector(".comp-name-text")
            logo_ele = job_element.query_selector(".comp_logo img")
            location_ele = job_element.query_selector(".locon-text-d")
            deadline_ele = job_element.query_selector(".dead-text-d")
            experience_ele = job_element.query_selector(".exp-text-d")

        if title_ele:
            job['title'] = title_ele.inner_text().strip()
            job['details_link'] = title_ele.get_attribute('href')
        else:
            job['title'], job['details_link'] = "N/A", "N/A"

        if company_ele:
            job['company_name'] = company_ele.inner_text().strip()
        else:
            job['company_name'] = "N/A"

        if logo_ele:
            job['company_logo'] = logo_ele.get_attribute('src')
        else:
            job['company_logo'] = "N/A"

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
    """Launches browser, searches for a job, extracts the results, and saves to CSV."""
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
        
        # --- SAVE TO CSV INSTEAD OF PRINTING ---
        if extracted_jobs:
            # Create a directory named 'output' if it doesn't exist
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Sanitize keyword for filename (e.g., "Data Science" -> "data_science")
            safe_keyword = keyword.lower().replace(" ", "_")
            filepath = os.path.join(output_dir, f"{safe_keyword}_jobs.csv")
            
            save_to_csv(extracted_jobs, filepath)
        else:
            print("No jobs found to save.")

        browser.close()

if __name__ == "__main__":
    search_job_on_bdjobs("Python Developer")