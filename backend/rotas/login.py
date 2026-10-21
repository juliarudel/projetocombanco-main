from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import conectar
import bcrypt
import jwt

router = APIRouter()

SECRET_KEY = "sua_chave_secreta_aqui"  
ALGORITHM = "HS256"

# Modelo para receber os dados do Swagger
class LoginDados(BaseModel):
    email: str
    senha: str

@router.post("/")
def login_usuario(dados: LoginDados):
    conn = conectar()
    # Usando dictionary=True para garantir a leitura correta das colunas por nome
    cursor = conn.cursor(dictionary=True) 
    
    try:
        # 1. Busca o usuário na tabela pelo e-mail informado
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (dados.email,))
        usuario = cursor.fetchone()
        
        # Se o e-mail não existir na tabela do phpMyAdmin
        if not usuario:
            return {"erro": "E-mail ou senha inválidos"}
            
        # 2. Converte para bytes e valida se o hash bate com a senha digitada
        senha_digitada_bytes = dados.senha.encode('utf-8')
        senha_banco_bytes = usuario['senha'].encode('utf-8')
        
        if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
            # 3. Monta o payload (o crachá) do Token com o e-mail e o tipo correto do banco
            token_dados = {
                "sub": usuario['email'],
                "tipo": usuario['tipo']  # Vai carregar 'admin' ou 'funcionario' automaticamente
            }
            
            # 4. Gera o token JWT de acesso
            token_gerado = jwt.encode(token_dados, SECRET_KEY, algorithm=ALGORITHM)
            
            return {
                "mensagem": "Login realizado com sucesso!",
                "access_token": token_gerado,
                "token_type": "bearer"
            }
        else:
            return {"erro": "E-mail ou senha inválidos"}
            
    except Exception as e:
        return {"erro": f"Erro interno no servidor: {str(e)}"}
    finally:
        cursor.close()
        conn.close()
