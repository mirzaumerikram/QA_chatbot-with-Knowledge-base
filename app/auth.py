import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class BearerTokenAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(BearerTokenAuth, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(BearerTokenAuth, self).__call__(request)
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme")
        if credentials.credentials != SECRET_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid or missing token")
        return credentials.credentials

auth_scheme = BearerTokenAuth()
