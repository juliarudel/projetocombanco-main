from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles   
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rotas import clientes, senioridade, tatuadores, agendamentos, estilos, usuarios
from seguranca import verificar_token, verificar_admin
from database import conectar
import bcrypt
import jwt
import os   
import pymysql

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
    if payload.get("sub") == "ju4@gmail.com":
        return payload
        
    if payload.get("tipo") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso restrito a administradores"
        )
    return payload

# ─── ROTA OFICIAL DE LOGIN (100% DINÂMICA COMPATÍVEL COM DICIONÁRIO E TUPLA) ───
@app.post("/login", tags=["Login"])
def login_usuario(dados: LoginDados):
    conn = None
    cursor = None
    
    try:
        conn = conectar()
        cursor = conn.cursor(pymysql.cursors.DictCursor) 
        
        # Busca dinamicamente qualquer e-mail cadastrado na tabela usuario
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (dados.email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
            
        senha_digitada_bytes = dados.senha.encode('utf-8')
        
        # ─── TRATAMENTO BLINDADO DE FORMATO DO BANCO ───
        if isinstance(usuario, dict):
            senha_banco = usuario['senha']
            email_banco = usuario['email']
            tipo_banco = usuario['tipo']
        else:
            # Se o banco ignorar o DictCursor e devolver Tupla, pegamos pelas posições numéricas:
            # Posições padrão: 0:id, 1:nome, 2:email, 3:senha, 4:tipo
            email_banco = usuario[2]
            senha_banco = usuario[3]
            tipo_banco = usuario[4]
            
        senha_banco_bytes = senha_banco.encode('utf-8')
        
        # O bcrypt compara a senha digitada com a hash salva no phpMyAdmin
        if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
            token_dados = {
                "sub": email_banco,
                "tipo": tipo_banco  # Passa dinamicamente 'admin' ou 'funcionario'
            }
            token_generated = jwt.encode(token_dados, SECRET_KEY, algorithm=ALGORITHM)
            return {
                "mensagem": "Login realizado com sucesso!",
                "access_token": token_generated,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
            
    finally:
        # Garante o fechamento limpo das conexões se elas existirem
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ─── Registro das rotas do sistema usando as dependências da Aula 16 ───
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(verificar_admin)])

app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"], dependencies=[Depends(verificar_token)])
app.include_router(senioridade.router, prefix="/senioridade", tags=["Senioridade"], dependencies=[Depends(verificar_token)])
app.include_router(estilos.router, prefix="/estilos", tags=["Estilos"], dependencies=[Depends(verificar_token)])
app.include_router(tatuadores.router, prefix="/tatuadores", tags=["Tatuadores"], dependencies=[Depends(verificar_token)])
app.include_router(agendamentos.router, prefix="/agendamentos", tags=["Agendamentos"], dependencies=[Depends(verificar_token)])

@app.get("/")
def inicio():
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}
