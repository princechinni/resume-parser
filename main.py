from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from textExtractor import TextExtractor
from linksExtractor import LinksExtractor
from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv
import json
import tiktoken  # For estimating token usage
import re #usedd for the link extraction.

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
text_extractor = TextExtractor()

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

async def read_file(file):
    # Create a temporary file with a secure random name
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_file_path = temp_file.name

    try:
        # Extract text from the uploaded file
        extracted_text = text_extractor.extract_text(temp_file_path)
    finally:
        # Always remove the temporary file
        os.unlink(temp_file_path)

    return extracted_text

@app.get("/api/resume/health_check/")
async def health_check():
    return {"message": "Resume Parser is healthy"}

# API 1: Upload a file (PDF or DOCX) and extract text from it
# @app.options("/api/resume/extract-text/")
# async def options_extract_text():
#     return {}

@app.post("/api/resume/extract-text/")
async def extract_text_from_file(request: Request, file: UploadFile = File(...)):
    print("Received request")
    print("Request headers:", request.headers)
    print("Received file:", file.filename)
    
    try:
        extracted_text = await read_file(file)
        return {"extracted_text": extracted_text}
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {"error": str(e)}

#links extrator.
# Endpoint to extract links from a PDF or DOCX file
@app.post("/api/resume/extract-links/")
async def extract_links_from_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file (PDF or DOCX) and extract LinkedIn links from it.
    """
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_file_path = temp_file.name

    try:
        # Use the LinksExtractor class to extract links from the uploaded file
        links_extractor = LinksExtractor(temp_file_path)
        extracted_links = links_extractor.extract_links()

        # Filter out LinkedIn links
        linkedin_links = [link for link in extracted_links if "linkedin.com" in link]
        github_links = [link for link in extracted_links if "github.com" in link]

        # Create a dictionary with the key "linkedin" and the value being the LinkedIn link(s)
        result = {"linkedin": linkedin_links[0],"github": github_links[0]}
        

        # Return the dictionary as JSON
        return {"extracted_links": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Always remove the temporary file
        os.unlink(temp_file_path)


# API 2: Upload a file (PDF or DOCX), extract text, and return the parsed resume data with cost
@app.post("/api/resume/parse-resume/")
async def parse_resume(request: Request, file: UploadFile = File(...)):
    extracted_text = await read_file(file)
    
    # Prepare the messages for the ChatCompletion API
    messages = [
        {
            "role": "system",
            "content": "You are an expert resume parser AI. Your task is to accurately extract and structure information from resumes into a predefined JSON format. Only include information that is explicitly stated or can be directly inferred from the resume text. Leave fields empty if the information is not present or cannot be confidently determined."
        },
        {
            "role": "user",
            "content": f"Carefully analyze the following resume text and extract all relevant information:\n\n{extracted_text}\n\n"
                       "Fill in the JSON template below with the extracted information. Follow these guidelines:\n"
                       "1. Only include information that is explicitly stated or can be directly inferred from the resume.\n"
                       "2. Leave fields empty (use null for numbers/dates, empty string for text, or empty array for lists) if the information is not present.\n"
                       "3. Use your best judgment to categorize skills and determine proficiency levels.\n"
                       "4. Format dates as ISO 8601 strings (YYYY-MM) when possible.\n"
                       "5. Ensure all extracted information is accurate and relevant to the field it's placed in.\n"
                       "6. cgpa_or_percentage should be a number.\n"
                       "7. For all 'id' fields, use a string of numbers(size of Date.now().toString() strings) that represents a unique identifier.\n"
                       "8. For all 'description' fields, use an array of strings that represents the description.\n"
                       "9. make sure awards_and_achievements, extra_curricular_activities are an arrays of strings.\n"
                       "10. For the phone number, remove the '+91' prefix if present. Only include the digits of the phone number.\n"
                       "11. For the email, remove the 'mailto:' prefix if present. Only include the email address.\n"
                       "JSON template to fill:"
                       '''
                       {
                           "personal_information": {
                               "first_name": "",
                               "last_name": "",
                               "email": "",
                               "phone": "",
                               "expected_salary": null
                           },
                           "socials": {
                               "github": "",
                               "linkedin": "",
                               "twitter": "",
                               "website": ""
                           },
                           "courses": [
                               {
                                   "id": "",
                                   "course_name": "",
                                   "course_link": "",
                                   "course_provider": "",
                                   "completion_date": null
                               }
                           ],
                           "education": [
                               {
                                   "id": "",
                                   "institution": "",
                                   "degree": "",
                                   "start_date": null,
                                   "end_date": null,
                                   "cgpa_or_percentage": null,
                                   "description": []
                               }
                           ],
                           "experience": [
                               {
                                   "id": "",
                                   "company": "",
                                   "position": "",
                                   "start_date": null,
                                   "end_date": null,
                                   "description": [],
                                   "currently_working": false
                               }
                           ],
                           "publications": [
                               {
                                   "id": "",
                                   "name": "",
                                   "link": "",
                                   "date": null
                               }
                           ],
                           "skills": [
                               {
                                   "id": "",
                                   "skill_name": "",
                                   "skill_proficiency": ""
                               }
                           ],
                           "personal_projects": [
                               {
                                   "id": "",
                                   "name": "",
                                   "description": [],
                                   "link": "",
                                   "start_date": null,
                                   "end_date": null
                               }
                           ],
                           "awards_and_achievements": [],
                           "position_of_responsibility": [
                               {
                                   "id": "",
                                   "title": "",
                                   "organization": "",
                                   "start_date": null,
                                   "end_date": null,
                                   "description": []
                               }
                           ],
                           "competitions": [
                               {
                                   "id": "",
                                   "name": "",
                                   "description": [],
                                   "date": null
                               }
                           ],
                           "extra_curricular_activities": []
                       }
                       '''
        }
    ]

    print("messages: ", messages)

    # Estimate tokens before the API call
    num_tokens = calculate_tokens(extracted_text)

    # Call the OpenAI API for text analysis
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=3000,
        temperature=0
    )

    result = response.choices[0].message.content.strip('```json').strip('```')
    print("Parsed result from OpenAI:", result)

    if result:
        try:
            parsed_data = json.loads(result)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", str(e))
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

    