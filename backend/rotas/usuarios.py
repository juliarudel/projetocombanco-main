from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from database import conectar
import bcrypt      # biblioteca que gera e confere o hash da senha
import jwt         # biblioteca que gera o token de acesso (JWT)

router = APIRouter()

# Configurações do Token JWT (idênticas às usadas nos testes de validação)
SECRET_KEY = "sua_chave_secreta_aqui"  
ALGORITHM = "HS256"

# Modelo de dados para Cadastro de Usuário
class Usuario(BaseModel):
    nome: str     
    email: str    
    senha: str    
    tipo: Optional[str] = "funcionario" # admin, funcionario ou cliente
    idcliente: Optional[int] = None

# Modelo de dados exclusivo para receber a tentativa de Login
class LoginDados(BaseModel):
    email: str
    senha: str

# ─── POST /usuarios — Cadastra um novo usuário ───
@router.post("")
def criar_usuario(usuario: Usuario):
    senha_hash = bcrypt.hashpw(usuario.senha.encode("utf-8"), bcrypt.gensalt())

    conn = conectar()
    cursor = conn.cursor()

    try:
        # Atualizado para incluir as colunas tipo e idcliente criadas no banco
        cursor.execute(
            "INSERT INTO usuario (nome, email, senha, tipo, idcliente) VALUES (%s, %s, %s, %s, %s)",
            (usuario.nome, usuario.email, senha_hash.decode("utf-8"), usuario.tipo, usuario.idcliente)
        )
        conn.commit()
        return {"mensagem": "Usuário cadastrado com sucesso"}
    except Exception:
        conn.rollback()
        return {"erro": "Não foi possível cadastrar. Verifique se esse e-mail já está em uso."}
    finally:
        cursor.close()
        conn.close()

# ─── POST /usuarios/login — Nova rota criada para autenticar o Usuário ───
@router.post("/login")
def login_usuario(dados: LoginDados):
    conn = conectar()
    # Usando dictionary=True para que o Python leia os campos por nome (ex: usuario['senha'])
    cursor = conn.cursor(dictionary=True) 
    
    try:
        # 1. Busca o usuário na tabela pelo e-mail digitado no Swagger
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (dados.email,))
        usuario = cursor.fetchone()
        
        # Se o e-mail não existir na tabela
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
            
        # 2. Converte as senhas para bytes e confere se o hash bate
        senha_digitada_bytes = dados.senha.encode('utf-8')
        senha_banco_bytes = usuario['senha'].encode('utf-8')
        
        if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
            # 3. Se a senha estiver correta, monta o payload (o crachá) do Token
            token_dados = {
                "sub": usuario['email'],
                "tipo": usuario['tipo'] # Aqui vai carregar se o usuário é 'admin' ou 'funcionario'
            }
            
            # 4. Fabrica o token JWT de acesso
            token_gerado = jwt.encode(token_dados, SECRET_KEY, algorithm=ALGORITHM)
            
            return {
                "mensagem": "Login realizado com sucesso!",
                "access_token": token_gerado,
                "token_type": "bearer"
            }
        else:
            # Se a senha estiver errada
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()
