# Standard library imports
import time
import re
import logging
import json
import os
from enum import Enum

# Third-party imports
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.common.exceptions import StaleElementReferenceException # type: ignore

# Local application imports
from utils.selenium_helper import Helper
from utils.api_utils import get_openai_response, get_claude_response
from utils.prompts import specify_json_output_prompt_format, personal_info_prompt

class Model(Enum):
    CLAUDE = 'claude'
    OPENAI = 'openai'

# global vars for configuration
regex_filter = r'(developer|engineer|js|javascript|react|native|mobile|ios|android|security)' # Potential filter to skip jobs
use_regex_filter = False # Whether to use regex filter to skip some jobs in the sidebar
security_check_flag = False # Whether to pause execution for manual security check
first_model = Model.OPENAI # 'claude' or 'openai'
switch_model_on_fail = True # Whether to switch model on fail

# global vars for implementation
curr_model = first_model

# global vars for testing
pause_after_modal_fill = 10

# "junior software engineer"
linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4103332696&distance=25&f_AL=true&f_E=2&f_TPR=r86400&geoId=103644278&keywords=Junior%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true'
# For testing radio buttons and selection
# linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4109967443&distance=25&f_AL=true&f_TPR=r86400&geoId=103644278&keywords=%22Jr.%20Mobile%20Developer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true'
# For testing input fields
# linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4110243035&distance=25&f_AL=true&f_TPR=r86400&geoId=103644278&keywords=%22Dotnet%20Developer%22%20TalentBurst&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true'
# failing rn
linkedin_url = 'https://www.linkedin.com/jobs/search/?currentJobId=4115480028&geoId=103644278&keywords=Complete%20Business%20Intelligence%20Specialist%3A%20Cognos%20Developer%20by%20Complete%20Care%20Centers&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true'

# Logging configuration
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

# Fill out a single form modal within a single job listing
def fill_out_form_modal():
    # Try to submit if there isn't a warning message
    feedback_message = s.el('.artdeco-inline-feedback__message')
    if not feedback_message:
        return

    logging.debug('Answering questions')

    # Find all label-input pairs on the page
    modal = s.el_slow('.jobs-easy-apply-modal')

    # What's up with fieldset: linkedin stores radio buttons inside fieldset divs. Each radio button will have an input and label. To avoid selecting both, we treat inputs and labels separately depending on whether they have the fieldset parent.
    # Why :not([class*="hidden"]: Linkedin radio buttons (in the fieldset div) have duplicate spans for some reason, one of which is visually hidden. Let's not read both. 
    form_els = s.els_slow("""
        label:not(fieldset label):not([class*="hidden"]), 
        input:not(fieldset input):not([class*="hidden"]),
        select, fieldset span span:not([class*="hidden"]),
        fieldset label:not([class*="hidden"]),
        span[class="artdeco-inline-feedback__message"]
        """, parent=modal)
    stringified_form_elements = '\n'.join(s.stringify_elements(form_els))

    # Get json output commands
    json_output_commands = get_json_output_commands_from_stringified_form_elements(stringified_form_elements)
    execute_json_output_commands(json_output_commands, form_els)
    time.sleep(pause_after_modal_fill)

    # scroll down the elements
    for form_el in form_els:
        driver.execute_script("arguments[0].scrollIntoView();", form_el)

# Fill out all form modals within a single job listing
def fill_out_all_form_modals(job_title):
    global curr_model

    # Keep clicking "Next" and "Reviepw your application"
    num_errors = 0
    allowed_errors = 3
    curr_model = first_model
    while True:
        try:
            # Fill out modal and press continue
            fill_out_form_modal()
            continue_btn = s.el('button[aria-label="Continue to next step"], button[aria-label="Review your application"]')
            if continue_btn:
                s.click_js(continue_btn, driver)
                time.sleep(1)

            # Don't follow their stupid page
            follow_company_btn = s.el('label[for="follow-company-checkbox"]')
            if follow_company_btn:
                s.click_js(follow_company_btn, driver)
                time.sleep(0.5)
            
            # Submit if possible
            submit_btn = s.el('button[aria-label="Submit application"]')
            if submit_btn:
                s.click_js(submit_btn, driver)
                time.sleep(0.5)

                # Dismiss any modal popup
                not_now_btn = s.el('button[aria-label="Dismiss"]')
                if not_now_btn:
                    s.click_js(not_now_btn, driver)
                    time.sleep(0.5)
                break

        # Live to try filling out the modal again
        except Exception as e:
            print(f'Encountered error #{num_errors + 1} applying for job "{job_title}": {e}')
            num_errors += 1
            if switch_model_on_fail:
                print('\t\t\t\tswitching models from', curr_model)
                curr_model = Model.OPENAI if curr_model == Model.CLAUDE else Model.CLAUDE
                print('\t\t\t\tto', curr_model)
            if num_errors > allowed_errors: 
                print('Too many errors, breaking')
                break

# Apply to all jobs in side bar
def apply_to_all_jobs_in_side_bar():
    job_listings = driver.find_elements(By.CSS_SELECTOR, '.job-card-container')
    print('num jobs', len(job_listings))
    for job in job_listings:
        print(f'Applying to job {job}...')
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
            s.click_js(job_title_element, driver)
            time.sleep(1)

            # Click "Easy Apply"
            s.click_slow('button[aria-label^="Easy Apply"].jobs-apply-button', driver=driver)

            # Fill out all form modals
            fill_out_all_form_modals(job_title)

        except Exception as e: continue

# Get json output commands from stringified form elements
def get_json_output_commands_from_stringified_form_elements(stringified_form_elements):
    composite_prompt = specify_json_output_prompt_format + personal_info_prompt + f'\nOk, here are the form elements: \n{stringified_form_elements}'
    print('composite prompt', composite_prompt)
    print('\t\t\t\tcurr_model', curr_model)
    res = get_claude_response(composite_prompt) if curr_model == Model.CLAUDE else get_openai_response(composite_prompt)
    print('res', res)
    try:
        # delete anything before the first [ and the last index of ]
        first_bracket, last_bracket = res.index('['), res.rindex(']')
        res = res[first_bracket:last_bracket+1]
        return json.loads(res)
    except Exception as e:
        print('Error parsing JSON:', res, '\nand got error', e)
        return []

# Execute commands specified by api call in json response
def execute_json_output_commands(json_output_commands, elements):
    print('assert statement', len(json_output_commands), len(elements))
    assert len(json_output_commands) == len(elements)
    for command, element in zip(json_output_commands, elements):
        # click with js and bypass overlay
        # s.click_js(element, driver)
        # element.click()
        try:
            if 'click' in command and command['click'] == True:
                try:
                    s.click_js(element, driver)
                except StaleElementReferenceException:
                    print('Error clicking', element, 'and got error', e)
                # element.click()
            if 'text' in command and command['text']:
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, element, command['text'])
                # element.send_keys(command['text'])
            if 'option' in command and command['option']:
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, element, command['option'])
                # element.send_keys(command['option'])
        except Exception as e:
            print('Error executing', command, 'on element', element, 'and got error', e)

# Main execution
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
    print('PROGRAM DIED: OUTSIDE MAIN FUNCTION')
    time.sleep(50)
except Exception as e:
    print(e)
finally:
    driver.quit()
