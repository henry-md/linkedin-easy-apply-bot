from dotenv import load_dotenv
import os
import requests
from openai import OpenAI
from prompts import prompt_1, prompt_2

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

def get_claude_response(prompt):
    data = {
        "model": "claude-3-opus-20240229",  # or another available model
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": 300,
    }

    # Make API call
    response = requests.post("https://api.anthropic.com/v1/messages", headers=claude_headers, json=data)
    return response.json()['content'][0]['text']