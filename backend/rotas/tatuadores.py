from fastapi import APIRouter # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional, List
from database import conectar

router = APIRouter()

class EstilosDoTatuador(BaseModel):
    idestilos: List[int]

# Modelo de dados — define os campos que o tatuador deve ter
class Tatuador(BaseModel):
    nometatuador: str                      # obrigatório
    cpf: str                               # obrigatório
    email: Optional[str] = None            # opcional
    telefone: Optional[str] = None         # opcional
    datacontratacao: Optional[str] = None  # opcional
    idsenioridade: int                     # obrigatório — aponta para a tabela senioridade

# GET /tatuadores — lista todos os tatuadores, já com o nome da senioridade
@router.get("")
def listar_tatuadores():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tatuador.*, senioridade.nome AS senioridade,
               GROUP_CONCAT(estilo.descricao SEPARATOR ', ') AS estilos
        FROM tatuador
        JOIN senioridade ON tatuador.idsenioridade = senioridade.idsenioridade
        LEFT JOIN tatuador_estilo ON tatuador.idtatuador = tatuador_estilo.idtatuador
        LEFT JOIN estilo ON tatuador_estilo.idestilo = estilo.idestilo
        GROUP BY tatuador.idtatuador
    """)
    tatuadores = cursor.fetchall()
    conn.close()
    return tatuadores

# GET /tatuadores/{id} — busca um tatuador pelo ID
@router.get("/{id}")
def buscar_tatuador(id: int):
    # (O código continuaria aqui abaixo de acordo com as funções do seu arquivo original)
    pass
