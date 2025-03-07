from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import parseResumeRoute

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/resume/health_check")
async def health_check():
    return {"message": "Resume Parser is healthy"}

# Upload a file (PDF or DOCX), extract text, and return the parsed resume data with cost estimate
# This route is protected by JWT
# The user must be authenticated to access this route
app.include_router(parseResumeRoute.router, prefix="/api/resume", tags=["Resume Parser"])
