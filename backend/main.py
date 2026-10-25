from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles   
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rotas import clientes, senioridade, tatuadores, agendamentos, estilos, usuarios
# AJUSTADO: Importando apenas o verificar_token padrão do arquivo de segurança
from seguranca import verificar_token, verificar_admin
from database import conectar
import bcrypt
import jwt
import os   

app = FastAPI(title="Estúdio de Tatuagem API")

# Configuração de CORS para permitir a comunicação com o Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)   
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")   

# Configurações do Token JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
ALGORITHM = "HS256"

# Modelo para receber o login
class LoginDados(BaseModel):
    email: str
    senha: str

# ─── FUNÇÃO LOCAL DE VERIFICAÇÃO DE ADMIN (Blindada com Passe Livre) ───
def verificar_admin_local(payload: dict = Depends(verificar_token)):
    # Se o e-mail do token for o seu, libera o acesso na hora sem olhar o tipo!
    if payload.get("sub") == "ju4@gmail.com":
        return payload
        
    # Bloqueio padrão de segurança para usuários comuns
    if payload.get("tipo") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso restrito a administradores"
        )
    return payload

# ─── ROTA OFICIAL DE LOGIN ───
@app.post("/login", tags=["Login"])
def login_usuario(dados: LoginDados):
    if (dados.email == "ju4@gmail.com" and dados.senha == "ju4") or (dados.email == "admin@estudio.com" and dados.senha == "admin123"):
        token_dados = {
            "sub": dados.email,
            "tipo": "admin"
        }
        token_gerado = jwt.encode(token_dados, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "mensagem": "Login de Administrador realizado com sucesso!",
            "access_token": token_gerado,
            "token_type": "bearer"
        }

    conn = conectar()
    cursor = conn.cursor(dictionary=True) 
    try:
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (dados.email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
            
        senha_digitada_bytes = dados.senha.encode('utf-8')
        senha_banco_bytes = usuario['senha'].encode('utf-8')
        
        if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
            token_dados = {
                "sub": usuario['email'],
                "tipo": usuario['tipo']
            }
            token_gerado = jwt.encode(token_dados, SECRET_KEY, algorithm=ALGORITHM)
            return {
                "mensagem": "Login realizado com sucesso!",
                "access_token": token_gerado,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    finally:
        cursor.close()
        conn.close()

# ─── Registro das rotas do sistema usando a nova dependência blindada ───
# DEIXE ESSA LINHA LIMPA (SEM DEPENDENCIES), APENAS COM O PREFIXO:
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(verificar_admin)])

app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"], dependencies=[Depends(verificar_token)])
app.include_router(senioridade.router, prefix="/senioridade", tags=["Senioridade"], dependencies=[Depends(verificar_token)])
app.include_router(estilos.router, prefix="/estilos", tags=["Estilos"], dependencies=[Depends(verificar_token)])
app.include_router(tatuadores.router, prefix="/tatuadores", tags=["Tatuadores"], dependencies=[Depends(verificar_token)])
app.include_router(agendamentos.router, prefix="/agendamentos", tags=["Agendamentos"], dependencies=[Depends(verificar_token)])

@app.get("/")
def inicio():
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}
