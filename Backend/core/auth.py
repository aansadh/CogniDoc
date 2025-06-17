from fastapi import Request, HTTPException

def clerk_only(request: Request):
    if getattr(request.state, "auth_method", None) != "clerk":
        raise HTTPException(status_code=403, detail="Only Clerk-authenticated users allowed")
    return request.state.user_id 

def token_only(request: Request):
    if getattr(request.state, "auth_method", None) != "token":
        raise HTTPException(status_code=403, detail="Only token-authenticated sessions allowed")
    return request.state.session_id  