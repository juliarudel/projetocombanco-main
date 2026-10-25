from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
ALGORITHM = "HS256"

security_scheme = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirou")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

def verificar_admin(payload: dict = Depends(verificar_token)):
    if payload.get("tipo") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return payload