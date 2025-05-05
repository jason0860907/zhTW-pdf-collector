import os
import re
import time
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def download_twse_pdfs(co_id: str, year: str, output_dir: str = "pdfs", headless: bool = True):
    """
    Scrapes the TWSE (台灣證交所) site to download financial report PDFs for a specific company and year.
    Uses Selenium to handle JavaScript-based navigation and requests to download final PDFs.
    """
    # --- Step 1: Construct the URL for the list of disclosures
    base_url = "https://doc.twse.com.tw"
    list_url = f"{base_url}/server-java/t57sb01?step=1&colorchg=1&seamon=&mtype=A&co_id={co_id}&year={year}"

    # --- Step 2: Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # --- Step 3: Set up a headless Chrome browser using Selenium
    options = Options()
    if headless:
        options.add_argument("--headless")  # Runs browser in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    # --- Step 4: Load the listing page for the given company/year
    driver.get(list_url)
    time.sleep(3)  # Allow time for JavaScript to render the page

    # --- Step 5: Find all anchor tags that trigger readfile2(...) JS function (PDF entries)
    a_tags = driver.find_elements(By.XPATH, "//a[contains(@href, 'readfile2')]")

    # Regular expression to extract file metadata from readfile2 JS function call
    pdf_pattern = re.compile(r'readfile2\("([A-Z])","(\d+)","([^"]+\.pdf)"\)')

    # Use requests to download the actual PDF file once the final URL is found
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    print(f"Found {len(a_tags)} PDF entries for company {co_id}, year {year}.")

    # --- Step 6: Iterate over each PDF entry link
    for idx, a in enumerate(a_tags):
        href = a.get_attribute("href")
        text = a.text.strip()
        match = pdf_pattern.search(href)
        if not match:
            continue  # Skip if the link doesn't match the expected pattern

        print(f"({idx+1}) Clicking on {text} ...")
        try:
            # Record the original window
            main_window = driver.current_window_handle
            before_handles = set(driver.window_handles)

            # --- Step 7: Click the link to open the intermediate page (opens in a new window)
            a.click()
            time.sleep(2)

            # --- Step 8: Detect and switch to the new window
            new_window = (set(driver.window_handles) - before_handles).pop()
            driver.switch_to.window(new_window)

            # --- Step 9: Locate the final PDF link on the intermediate page
            pdf_elem = driver.find_element(By.XPATH, "//a[contains(@href, '.pdf')]")
            pdf_url = pdf_elem.get_attribute("href")
            pdf_name = os.path.basename(pdf_url)
            pdf_path = os.path.join(output_dir, pdf_name)

            # --- Step 10: Download the PDF using requests for speed
            print(f"Downloading {pdf_name} ...")
            r = session.get(pdf_url)
            with open(pdf_path, "wb") as f:
                f.write(r.content)

            # --- Step 11: Close the new window and return to the main listing
            driver.close()
            driver.switch_to.window(main_window)
            time.sleep(1.5)

        except Exception as e:
            print(f"Failed on {text}: {e}")
            # Always return to main window if an error occurs
            try:
                driver.switch_to.window(main_window)
            except:
                pass

    # --- Step 12: Clean up the Selenium browser
    driver.quit()
    print(f"All PDFs for company {co_id} in year {year} downloaded to '{output_dir}'.")


if __name__ == "__main__":
    # --- Command-line interface using argparse ---
    parser = argparse.ArgumentParser(description="Download TWSE company PDFs for a given year.")
    parser.add_argument("--co_id", type=str, required=True, help="TWSE company ID (e.g., 1101)")
    parser.add_argument("--year", type=str, required=True, help="Year in ROC calendar (e.g., 110)")
    parser.add_argument("--output", type=str, default="pdfs", help="Output directory (default: ./pdfs)")
    parser.add_argument("--no-headless", action="store_true", help="Disable headless mode to see browser")

    # Parse the CLI arguments
    args = parser.parse_args()

    # Call main function with parsed arguments
    download_twse_pdfs(
        co_id=args.co_id,
        year=args.year,
        output_dir=args.output,
        headless=not args.no_headless
    )
