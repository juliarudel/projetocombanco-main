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

# ─── ROTA OFICIAL DE LOGIN (TOTALMENTE PÚBLICA E DINÂMICA) ───
@app.post("/login", tags=["Login"])
def login_usuario(dados: LoginDados):
    conn = None
    cursor = None
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Busca o usuário na tabela pelo e-mail informado
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (dados.email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
            
        senha_digitada_bytes = dados.senha.encode('utf-8')
        
        # ─── MAPEAMENTO CORRIGIDO DA TUPLA DO BANCO ───
        # desc[0] captura estritamente o texto com o nome da coluna (ex: 'senha')
        colunas = [desc[0] for desc in cursor.description]
        usuario_dict = dict(zip(colunas, usuario))
        
        senha_banco = usuario_dict.get('senha')
        email_banco = usuario_dict.get('email')
        tipo_banco = usuario_dict.get('tipo')
        
        if not senha_banco:
            raise HTTPException(status_code=401, detail="Estrutura de senha inválida no banco")
            
        senha_banco_bytes = senha_banco.encode('utf-8')
        
        # O bcrypt compara a senha digitada com a hash salva no phpMyAdmin
        if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
            token_dados = {
                "sub": email_banco,
                "tipo": tipo_banco  # Retorna dinamicamente 'admin' ou 'funcionario'
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
