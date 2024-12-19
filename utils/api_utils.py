from dotenv import load_dotenv
import os
from openai import OpenAI
from prompts import prompt_1, prompt_2

# Load environment variables from .env file to make accessible to os.getenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt_1,
        }
    ],
    model="gpt-4o",
)

print(chat_completion.choices[0].message.content)