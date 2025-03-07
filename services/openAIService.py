from dotenv import load_dotenv
import os
from openai import OpenAI
from utils.system_prompts.parse_resume_prompt import parse_resume_system_prompt

load_dotenv()


api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key)

async def get_data_in_json_format(extracted_text: str):
    messages = [
        {
            "role": "system",
            "content": "You are an expert resume parser AI. Your task is to accurately extract and structure information from resumes into a predefined JSON format. Only include information that is explicitly stated or can be directly inferred from the resume text. Leave fields empty if the information is not present or cannot be confidently determined."
        },
        {
            "role": "user",
            "content": parse_resume_system_prompt.format(extracted_text=extracted_text)
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=6000,
        temperature=0
    )

    return response.choices[0].message.content.strip('```json').strip('```')