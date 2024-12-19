from api_utils import get_openai_response, get_claude_response
from prompts import prompt_1, prompt_2

response_1 = get_openai_response(prompt_1)
print(response_1)

response_1 = get_claude_response(prompt_2)
print(response_1)
