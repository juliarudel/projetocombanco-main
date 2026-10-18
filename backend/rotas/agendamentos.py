from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import conectar

router = APIRouter()


class Agendamento(BaseModel):
    idcliente: int
    idtatuador: int
    dataagendamento: str
    horaagendamento: str
    descricaotatuagem: Optional[str] = None
    valortatuagem: Optional[float] = None
    status: Optional[str] = None


# GET /agendamentos - lista todos os agendamentos
@router.get("/agendamentos")
def listar_agendamentos():
    conn = conectar()

    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco")

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                agendamento.*,
                cliente.nome AS cliente,
                tatuador.nometatuador AS tatuador
            FROM agendamento
            JOIN cliente
                ON agendamento.idcliente = cliente.idcliente
            JOIN tatuador
                ON agendamento.idtatuador = tatuador.idtatuador
        """)
        return cursor.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# POST /agendamentos - cadastra um agendamento
@router.post("/agendamentos")
def criar_agendamento(agendamento: Agendamento):
    conn = conectar()

    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco")

    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agendamento (
                idcliente,
                idtatuador,
                dataagendamento,
                horaagendamento,
                descricaotatuagem,
                valortatuagem
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            agendamento.idcliente,
            agendamento.idtatuador,
            agendamento.dataagendamento,
            agendamento.horaagendamento,
            agendamento.descricaotatuagem,
            agendamento.valortatuagem
        ))

        conn.commit()
        return {"mensagem": "Agendamento cadastrado com sucesso"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# GET /agendamentos/{id} - busca um agendamento pelo ID
@router.get("/agendamentos/{id}")
def buscar_agendamento(id: int):
    conn = conectar()

    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco")

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM agendamento WHERE idagendamento = %s",
            (id,)
        )

        agendamento = cursor.fetchone()

        if agendamento is None:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )

        return agendamento

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()

@router.put("/agendamentos/{id}")
def atualizar_agendamento(id: int, agendamento: Agendamento):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            UPDATE agendamento
            SET idcliente = %s,
                idtatuador = %s,
                dataagendamento = %s,
                horaagendamento = %s,
                descricaotatuagem = %s,
                valortatuagem = %s
            WHERE idagendamento = %s
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
                id
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )

        conexao.commit()

        return {"mensagem": "Agendamento atualizado com sucesso"}

    except HTTPException:
        raise

    except Exception as erro:
        conexao.rollback()
        raise HTTPException(status_code=500, detail=str(erro))

    finally:
        cursor.close()
        conexao.close()

@router.delete("/agendamentos/{id}")
def deletar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamento WHERE idagendamento = %s", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Agendamento deletado com sucesso"}