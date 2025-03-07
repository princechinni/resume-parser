import tempfile
from fastapi import File, UploadFile
from utils.textExtractor import TextExtractor
from utils.linksExtractor import LinksExtractor
import os

text_extractor = TextExtractor()

async def read_file(file: File):
    # Create a temporary file with a secure random name
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_file_path = temp_file.name

    try:
        # Extract text from the uploaded file
        extracted_text = text_extractor.extract_text(temp_file_path)
    except Exception as e:
        print(f"Error extracting text: {str(e)}")

    return extracted_text, temp_file_path

async def extract_links_from_file(temp_file_path: str):
    """
    Endpoint to upload a file (PDF or DOCX) and extract LinkedIn links from it.
    """
    try:
        # Use the LinksExtractor class to extract links from the uploaded file
        links_extractor = LinksExtractor(temp_file_path)
        extracted_links = links_extractor.extract_links()

        # Filter out LinkedIn links
        linkedin_links = [link for link in extracted_links if "linkedin.com" in link]
        github_links = [link for link in extracted_links if "github.com" in link]

        result = {}
        if len(linkedin_links) > 0:
            result["linkedin"] = linkedin_links[0]
        if len(github_links) > 0:
            result["github"] = github_links[0]        

        # Return the dictionary as JSON
        return {"extracted_links": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Always remove the temporary file
        os.unlink(temp_file_path)