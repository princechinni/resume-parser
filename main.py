from fastapi import FastAPI, File, UploadFile
from textExtractor import TextExtractor
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import tiktoken  # For estimating token usage

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
text_extractor = TextExtractor()

# Set OpenAI API key from .env
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

# OpenAI Pricing per 1000 tokens in USD (for GPT-3.5 Turbo)
OPENAI_COST_PER_1000_TOKENS = 0.0015

# Helper function to calculate the number of tokens used
def calculate_tokens(text):
    # Use cl100k_base, which is the encoding for gpt-3.5-turbo
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

# API 1: Upload a file (PDF or DOCX) and extract text from it
@app.post("/extract-text/")
async def extract_text_from_file(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Extract text from the uploaded file
    extracted_text = text_extractor.extract_text(file_location)
    
    return {"extracted_text": extracted_text}

# API 2: Take text input and return the parsed resume data with cost
@app.post("/parse-resume-text/")
async def parse_resume_from_text(extracted_text: str):
    # Prepare the messages for the ChatCompletion API
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that extracts structured data from resumes."
        },
        {
            "role": "user",
            "content": f"Extract the following details from the text:\n{extracted_text}\n\n"
                       "Fill in the JSON template with the information you can extract:\n"
                       '''{
                           "personal_information": {
                               "first_name": "",
                               "last_name": "",
                               "email": "",
                               "phone": ""
                           },
                           "socials": {
                               "github": "",
                               "linkedin": "",
                               "twitter": "",
                               "website": ""
                           },
                           "courses": [],
                           "education": [],
                           "experience": [],
                           "publications": [],
                           "skills": [],
                           "personal_projects": [],
                           "awards_and_achievements": [],
                           "position_of_responsibility": [],
                           "competitions": [],
                           "extra_curricular_activities": []
                       }'''
        }
    ]

    # Estimate tokens before the API call
    num_tokens = calculate_tokens(extracted_text)

    # Call the OpenAI API for text analysis
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1500,
        temperature=0.7
    )

    # Log the raw response for debugging
    print("OpenAI API raw response:", response)

    # Check if the API response contains a valid message
    if response and "choices" in response and response.choices:
        result = response.choices[0].message.content.strip()
        print("Parsed result from OpenAI:", result)
        
        # Check if the result is not empty before attempting to load it as JSON
        if result:
            try:
                parsed_data = json.loads(result)
            except json.JSONDecodeError as e:
                return {"error": "Failed to parse JSON from OpenAI response", "details": str(e)}
            
            # Estimate cost
            total_tokens_used = calculate_tokens(result) + num_tokens
            estimated_cost = (total_tokens_used / 1000) * OPENAI_COST_PER_1000_TOKENS
            
            return {
                "parsed_data": parsed_data,
                "tokens_used": total_tokens_used,
                "estimated_cost": estimated_cost
            }
        else:
            return {"error": "OpenAI response was empty"}
    else:
        return {"error": "OpenAI API call failed", "response": response}

# API 3: Upload a file (PDF or DOCX), extract text, and return the parsed resume data with cost
@app.post("/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Extract text from the uploaded file
    extracted_text = text_extractor.extract_text(file_location)

    # Prepare the messages for the ChatCompletion API
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that extracts structured data from resumes."
        },
        {
            "role": "user",
            "content": f"Extract the following details from the text:\n{extracted_text}\n\n"
                       "Fill in the JSON template with the information you can extract:\n"
                       '''{
                           "personal_information": {
                               "first_name": "",
                               "last_name": "",
                               "email": "",
                               "phone": ""
                           },
                           "socials": {
                               "github": "",
                               "linkedin": "",
                               "twitter": "",
                               "website": ""
                           },
                           "courses": [],
                           "education": [],
                           "experience": [],
                           "publications": [],
                           "skills": [],
                           "personal_projects": [],
                           "awards_and_achievements": [],
                           "position_of_responsibility": [],
                           "competitions": [],
                           "extra_curricular_activities": []
                       }'''
        }
    ]

    # Estimate tokens before the API call
    num_tokens = calculate_tokens(extracted_text)

    # Call the OpenAI API for text analysis
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1500,
        temperature=0.7
    )




    result = response.choices[0].message.content.strip('```json').strip('```')
    print("Parsed result from OpenAI:", result)
    breakpoint()

    if result:
        try:
            parsed_data = json.loads(result)
        except json.JSONDecodeError as e:
            return {"error": "Failed to parse JSON from OpenAI response", "details": str(e)}
        
        # Estimate cost
        total_tokens_used = calculate_tokens(result) + num_tokens
        estimated_cost = (total_tokens_used / 1000) * OPENAI_COST_PER_1000_TOKENS
        
        return {
            "parsed_data": parsed_data,
            "tokens_used": total_tokens_used,
            "estimated_cost": estimated_cost
        }
    else:
        return {"error": "OpenAI response was empty"}

