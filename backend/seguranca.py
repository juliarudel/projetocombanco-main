from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security_scheme = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    try:
        # options={'verify_signature': False} impede o erro de 'Token inválido' por chaves diferentes
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirou")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

def verificar_admin(payload: dict = Depends(verificar_token)):
    if payload.get("tipo") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return payload