"""
Charvak Authentication Middleware
Requires login for all system features
"""
from functools import wraps
from fastapi import Request, HTTPException
from typing import Dict, Optional

def require_login(request: Request) -> Dict:
    """Require user to be logged in."""
    from auth import verify_token, get_current_user
    
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        # Check session cookie
        token = request.cookies.get("auth_token", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

def require_auth_middleware(func):
    """Decorator to require authentication."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = require_login(request)
        request.state.user = user
        return await func(request, *args, **kwargs)
    return wrapper