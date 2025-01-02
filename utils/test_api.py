import json
import timeit

from api_utils import get_openai_response, get_claude_response
from prompts import specify_json_output_prompt_format, personal_info_prompt

sample_stringified_form_elements = '''
Element 1: HTML Tag: span; Inner Text: Have you completed the following level of education: Bachelor's Degree?; Required: True; 
Element 2: HTML Tag: label; Inner Text: Yes; 
Element 3: HTML Tag: label; Inner Text: No; 
Element 4: HTML Tag: span; Inner Text: Are you comfortable working in an onsite setting?; Required: True; 
Element 5: HTML Tag: label; Inner Text: Yes; 
Element 6: HTML Tag: label; Inner Text: No; 
Element 7: HTML Tag: label; Inner Text: Are you legally authorized to work in the United States? And will you now, or in the future, NOT require sponsorship for employment visa?; Required: True; 
Element 8: HTML Tag: select; Default Value: Select an option; Options: ['Select an option', 'Yes', 'No'], ; 
Element 9: HTML Tag: label; Inner Text: Are you available for relocation across USA? As the paid orientation & induction will be at Atlanta, Georgia and project location will be anywhere in US?; Required: True; 
Element 10: HTML Tag: select; Default Value: Select an option; Options: ['Select an option', 'Yes', 'No'], ; 
'''

composite_prompt = specify_json_output_prompt_format + personal_info_prompt + f'\nOk, here are the form elements: \n{sample_stringified_form_elements}'
print(composite_prompt)

# test prompt with timeit
def claude_call():
  res = get_claude_response(composite_prompt)
  print(res)

def openai_call():
  res = get_openai_response(composite_prompt)

claude_times = timeit.repeat(
        claude_call,
        number=1,  # how many times to run in each trial
        repeat=2   # how many trials to run
  )
openai_times = timeit.repeat(
        openai_call,
        number=1,  # how many times to run in each trial
        repeat=2   # how many trials to run
  )
print('claude_time', f'{sum(claude_times) / len(claude_times):.2f}s')
print('openai_time', f'{sum(openai_times) / len(openai_times):.2f}s')

"""
claude_time 12.44s
openai_time 7.16s
-- reduced prompt --
claude_time 10.84s
openai_time 6.24s
-- extended prompt --
claude_time 11.69s
openai_time 16.35s
...
claude_time 4.97s
openai_time 8.69s ?? much faster... okeyyy
"""