import jwt
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException, Request
import os

JWT_TOKEN_SECRET_KEY = os.environ.get('JWT_TOKEN_SECRET_KEY')


def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_TOKEN_SECRET_KEY, algorithms=["HS256"])
        return payload.get("_id") or payload.get("id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token missing")
    
    token = auth_header.split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return ObjectId(user_id)