from dotenv import load_dotenv # type: ignore
import os
import requests
from openai import OpenAI
import sys
import threading
import itertools
import time
import timeit
try:
    from utils.prompts import test_prompt
except:
    from prompts import test_prompt
from functools import wraps

# OpenAI github: https://github.com/openai/openai-python

# Load environment variables to make accessible to os.getenv()
load_dotenv()

# OpenAI client
gpt_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Define request payload for Claude
claude_headers = {
    "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

def loading_indicator(task_title="API Response"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def spinner():
                spinner_chars = itertools.cycle(['-', '/', '|', '\\'])
                while not spinner.done:
                    sys.stdout.write(f'\rGenerating {task_title}... {next(spinner_chars)}')
                    sys.stdout.flush()
                    time.sleep(0.1)
                sys.stdout.write(f'\r✅ Done generating {task_title} in {spinner.execution_time:.2f}s             \n')

            spinner.done = False
            spinner.execution_time = 0
            spinner_thread = threading.Thread(target=spinner)
            spinner_thread.start()

            try:
                start_time = timeit.default_timer()
                result = func(*args, **kwargs)
                spinner.execution_time = timeit.default_timer() - start_time
            finally:
                spinner.done = True
                spinner_thread.join()

            return result
        return wrapper
    return decorator

@loading_indicator(task_title="OpenAI Response")
def get_openai_response(prompt):
    chat_completion = gpt_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )

    return chat_completion.choices[0].message.content

@loading_indicator(task_title="Claude Response")
def get_claude_response(prompt):
    data = {
        "model": "claude-3-opus-20240229",  # or another available model
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": 4096,
    }

    # Make API call
    response = requests.post("https://api.anthropic.com/v1/messages", headers=claude_headers, json=data)
    res_obj = response.json()
    if 'type' in res_obj and res_obj['type'] == 'error':
        raise Exception('Error calling Claude API: ', res_obj['error']['message'])
    return response.json()['content'][0]['text']
