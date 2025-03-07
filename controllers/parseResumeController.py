import json
from fastapi import File
from fastapi.encoders import jsonable_encoder
from database.db import get_user_profile, insert_user_profile
from services.openAIService import get_data_in_json_format
from utils.extracting_raw_text_from_files import extract_links_from_file, read_file
from utils.tokens_count import calculate_tokens

# OpenAI Pricing per 1000 tokens in USD (for GPT-3.5 Turbo)
OPENAI_COST_PER_1000_TOKENS = 0.0015

async def parse_resume_with_AI(file: File , userId: str):
    # Check if user profile exists using the new function
    try:
        user_profile = get_user_profile(userId)
    except Exception as e:
        return {"error": str(e)}

    # # If user profile exists, return a message and do not parse the file
    if user_profile:
        return jsonable_encoder({
            "parsed_data": user_profile, 
            "message": "A profile already exists for this user. File parsing is not allowed."
        })

    # Proceed with file parsing if no profile exists
    extracted_text, temp_file_path = await read_file(file)

    # # Estimate tokens before the API call
    num_tokens = calculate_tokens(extracted_text)    

    result = await get_data_in_json_format(extracted_text)

    if result:
        try:
            parsed_data = json.loads(result)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", str(e))
            return {"error": "Failed to parse JSON from OpenAI response", "details": str(e)}
        
        # Estimate cost
        total_tokens_used = calculate_tokens(result) + num_tokens
        estimated_cost = (total_tokens_used / 1000) * OPENAI_COST_PER_1000_TOKENS
    
        extracted_links = await extract_links_from_file(temp_file_path)

        parsed_data['socials'] = extracted_links['extracted_links']

        insert_user_profile(userId=userId, user_profile=parsed_data)

        final_user_profile = get_user_profile(userId=userId)

        return jsonable_encoder({
            "parsed_data": final_user_profile,
            "tokens_used": total_tokens_used,
            "estimated_cost": estimated_cost
        })

    else:
        return {"error": "OpenAI response was empty"}