from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import logging

linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4103332696&distance=25&f_AL=true&f_E=2&f_TPR=r86400&geoId=103644278&keywords=Junior%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("webdriver_manager").setLevel(logging.WARNING)

# any string that contains the words (anywhere): js, javascript, react, native, mobile, ios, android
regex_filter = r'(developer|engineer|js|javascript|react|native|mobile|ios|android|security)'
use_regex_filter = False
security_check_flag = False # whether to pause execution for manual security check

# Declare Chrome Driver
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

# Get helper functions
from utils.selenium_helper import Helper
s = Helper(driver, logging)

def answer_questions():
    logging.debug('Answering questions')

    # find all label-input pairs on the page
    modal = s.el('.jobs-easy-apply-modal')
    form_els = s.els('label, input, select', parent=modal)
    s.print_res(form_els)

    # scroll down the elements
    for form_el in form_els:
        driver.execute_script("arguments[0].scrollIntoView();", form_el)

# Main
def main():
    # Setup
    driver.get('https://www.linkedin.com/login')

    # Login
    try:
        s.type('input[id="username"]', 'henrymdeutsch@gmail.com')
        s.type('input[id="password"]', '525Joule!23')
        s.type('input[id="password"]', Keys.RETURN)
    except Exception as e:
        print('couldn\'t sign in automatically')
        pass

    if security_check_flag:
        input('Press Enter to continue...')

    # Job presets based on URL
    driver.get(linkedin_url)
    time.sleep(1)

    # Iterate through jobs
    job_listings = driver.find_elements(By.CSS_SELECTOR, '.job-card-container')
    for job in job_listings:
        try:
            # Scroll it into view
            job_title_element = s.el('strong', parent=job)
            job_title = job_title_element.text
            driver.execute_script("arguments[0].scrollIntoView();", job_title_element)

            # Skip if you've already applied
            bold_el = s.el_quick('.t-bold', parent=job)
            already_applied = bold_el and bold_el.text == 'Applied'
            if already_applied:
                continue

            # Don't click if using a regex filter and the job title doesn't match
            if use_regex_filter:
                if not re.search(regex_filter, job_title, re.IGNORECASE):
                    continue
            
            # Apply for job
            job_title_element.click()
            time.sleep(1)

            # Click "Easy Apply"
            s.click('button[aria-label^="Easy Apply"].jobs-apply-button')

            # Keep clicking "Next" and "Review your application"
            while True:
                try:
                    answer_questions()
                    s.click_quick('button[aria-label="Continue to next step"], button[aria-label="Review your application"]')
                    time.sleep(1)
                except:
                    break
                # break # don't keep clicking "Next" for testing

            # Hit Submit

        except Exception as e: continue
        break # Don't go to next job for testing

try:
    main()
    time.sleep(50)
except Exception as e:
    print(e)
finally:
    driver.quit()
