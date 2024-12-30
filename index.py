from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
import time
import re
import logging
import json
import os

from utils.selenium_helper import Helper
from utils.api_utils import get_openai_response, get_claude_response
from utils.prompts import specify_json_output_prompt_format

# any string that contains the words (anywhere): js, javascript, react, native, mobile, ios, android
regex_filter = r'(developer|engineer|js|javascript|react|native|mobile|ios|android|security)'
use_regex_filter = False
security_check_flag = True # whether to pause execution for manual security check

# "junior software engineer"
linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4103332696&distance=25&f_AL=true&f_E=2&f_TPR=r86400&geoId=103644278&keywords=Junior%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true'
# for testing radio buttons and selection
# linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4109967443&distance=25&f_AL=true&f_TPR=r86400&geoId=103644278&keywords=%22Jr.%20Mobile%20Developer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true'
# for testing input fields
linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4110243035&distance=25&f_AL=true&f_TPR=r86400&geoId=103644278&keywords=%22Dotnet%20Developer%22%20TalentBurst&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("webdriver_manager").setLevel(logging.WARNING)

# Declare Chrome Driver
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

# Get helper functions
s = Helper(driver, logging)

def fill_out_form_modal():
    # Try to submit if there isn't a warning message
    feedback_message = s.el('.artdeco-inline-feedback__message')
    if not feedback_message:
        return

    logging.debug('Answering questions')

    # find all label-input pairs on the page
    modal = s.el_slow('.jobs-easy-apply-modal')

    # What's up with fieldset: linkedin stores radio buttons inside fieldset divs. Each radio button will have an input and label. To avoid selecting both, we treat inputs and labels separately depending on whether they have the fieldset parent.
    # Why :not([class*="hidden"]: Linkedin radio buttons (in the fieldset div) have duplicate spans for some reason, one of which is visually hidden. Let's not read both. 
    form_els = s.els_slow('label:not(fieldset label):not([class*="hidden"]), input:not(fieldset input):not([class*="hidden"]), select, fieldset span span:not([class*="hidden"]), fieldset label:not([class*="hidden"])', parent=modal)
    stringified_form_elements = '\n'.join(s.stringify_elements(form_els))

    # Get json output commands
    json_output_commands = get_json_output_commands_from_stringified_form_elements(stringified_form_elements)
    execute_json_output_commands(json_output_commands, form_els)

    # scroll down the elements
    for form_el in form_els:
        driver.execute_script("arguments[0].scrollIntoView();", form_el)

def fill_out_all_form_modals(job_title):
    # Keep clicking "Next" and "Reviepw your application"
    while True:
        try:
            fill_out_form_modal()
            s.click('button[aria-label="Continue to next step"], button[aria-label="Review your application"]')
            time.sleep(1)

            # check for submission

        except Exception as e:
            print(f'Encountered error applying for job "{job_title}": {e}')
            break # for testing, ^c seems to do weird stuff if you don't break

def apply_to_all_jobs_in_side_bar():
    job_listings = driver.find_elements(By.CSS_SELECTOR, '.job-card-container')
    for job in job_listings:
        try:
            # Scroll it into view
            job_title_element = s.el_slow('strong', parent=job)
            job_title = job_title_element.text
            driver.execute_script("arguments[0].scrollIntoView();", job_title_element)

            # Skip if you've already applied
            bold_el = s.el('.t-bold', parent=job)
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
            s.click_slow('button[aria-label^="Easy Apply"].jobs-apply-button', driver=driver)

            # Fill out all form modals
            fill_out_all_form_modals(job_title)

        except Exception as e: continue
        break # Don't go to next job for testing

def get_json_output_commands_from_stringified_form_elements(stringified_form_elements):
    composite_prompt = specify_json_output_prompt_format + f'\nOk, here are the form elements: {stringified_form_elements}'
    res = get_openai_response(composite_prompt)
    try:
        # delete anything before the first [
        res = res[res.index('['):]
        return json.loads(res)
    except Exception as e:
        print('Error parsing JSON:', res, '\nand got error', e)
        return []

def execute_json_output_commands(json_output_commands, elements):
    assert len(json_output_commands) == len(elements)
    for command, element in zip(json_output_commands, elements):
        # click with js and bypass overlay
        # driver.execute_script("arguments[0].click();", element)
        # element.click()
        try:
            if command['click']:
                driver.execute_script("arguments[0].click();", element)
                # element.click()
            if command['text']:
                driver.execute_script("arguments[0].value = arguments[1];", element, command['text'])
                # element.send_keys(command['text'])
            if command['option']:
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, element, command['option'])
                # element.send_keys(command['option'])
        except Exception as e:
            print('Error executing', command, 'on element', element, 'and got error', e)

# Main
def main():
    # Setup
    driver.get('https://www.linkedin.com/login')

    # Login
    try:
        s.type('input[id="username"]', os.getenv('LINKEDIN_EMAIL'))
        s.type('input[id="password"]', os.getenv('LINKEDIN_PASSWORD'))
        s.type('input[id="password"]', Keys.RETURN)
    except Exception as e:
        print('couldn\'t sign in automatically')
        pass
    if security_check_flag:
        input('Press Enter to continue...')

    # Job presets based on URL
    driver.get(linkedin_url)
    time.sleep(1)

    # Apply to all jobs in side bar
    apply_to_all_jobs_in_side_bar()

# Quit driver after execution
try:
    main()
    time.sleep(50)
except Exception as e:
    print(e)
finally:
    driver.quit()
