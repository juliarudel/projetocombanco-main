# GET /clientes - lista todos os clientes
from fastapi import APIRouter      # organiza rotas em grupos
from pydantic import BaseModel     # valida os dados que chegam na API
from typing import Optional        # permite campos opcionais
from database import conectar      # nossa função de conexão

router = APIRouter()               # cria o grupo de rotas

# Modelo de dados - define os campos que o cliente deve ter
class Cliente(BaseModel):
    nome: str                         # obrigatório
    cpf: str                          # obrigatório
    telefone: Optional[str] = None    # opcional
    datacadastro: Optional[str] = None # opcional
    cidade: Optional[str] = None      # opcional
    uf: Optional[str] = None          # opcional


# POST /clientes - cadastra um novo cliente
@router.post("/clientes")
def criar_cliente(cliente: Cliente):      # recebe os dados no corpo da requisição
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (cliente.nome, cliente.cpf, cliente.telefone, 
         cliente.datacadastro, cliente.cidade, cliente.uf)
    )
    conn.commit()  # confirma a gravação no banco
    conn.close()   # não se esqueça de fechar a conexão!
    return {"mensagem": "Cliente cadastrado com sucesso!"}

    # PUT /clientes/{id} - atualiza um cliente existente
@router.put("/clientes/{id}")
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

# DELETE /clientes/{id} - deleta um cliente
@router.delete("/clientes/{id}")
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
