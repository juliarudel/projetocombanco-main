from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from database import conectar
import jwt

router = APIRouter()

security_scheme = HTTPBearer()

class Cliente(BaseModel):
    nome: str                         
    cpf: str                          
    telefone: Optional[str] = None    
    datacadastro: Optional[str] = None 
    cidade: Optional[str] = None      
    uf: Optional[str] = None          

def obter_usuario_atual(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirou")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# GET /clientes
@router.get("")
def listar_clientes(usuario_logado: dict = Depends(obter_usuario_atual)):
    conn = conectar()                        
    cursor = conn.cursor(dictionary=True)    
    cursor.execute("SELECT * FROM cliente")  
    clientes = cursor.fetchall()             
    conn.close()                             
    return clientes                          

# POST /clientes
@router.post("")
def criar_cliente(cliente: Cliente):      
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (cliente.nome, cliente.cpf, cliente.telefone, 
         cliente.datacadastro, cliente.cidade, cliente.uf)
    )
    conn.commit()  
    conn.close()   
    return {"mensagem": "Cliente cadastrado com sucesso!"}

# PUT /clientes/{id}
@router.put("/{id}")
def atualizar_cliente(id: int, cliente: Cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE cliente 
        SET nome=%s, cpf=%s, telefone=%s, datacadastro=%s, cidade=%s, uf=%s
        WHERE idcliente=%s""",
        (cliente.nome, cliente.cpf, cliente.telefone,
         cliente.datacadastro, cliente.cidade, cliente.uf, id)
    )
    conn.commit()
    conn.close()
    return {"mensagem": "Cliente atualizado com sucesso"}

# DELETE /clientes/{id}
@router.delete("/{id}")
def deletar_cliente(id: int):
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cliente WHERE idcliente = %s", (id,))
        conn.commit()
        conn.close()
        return {"mensagem": "Cliente deletado com sucesso"}
    except Exception as erro:
        conn.rollback()
        conn.close()
        return {"erro": "Não foi possível excluir este cliente. Verifique se ele possui agendamentos."}
