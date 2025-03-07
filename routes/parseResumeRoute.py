from fastapi import APIRouter, Request, File, UploadFile
from controllers.parseResumeController import parse_resume_with_AI
from utils.jwt_handler import get_current_user

router = APIRouter()

@router.post("/parse-resume")
async def parse_resume(request: Request, file: UploadFile = File(...)):

    userId = get_current_user(request)
    
    return await parse_resume_with_AI(file, userId)

    
