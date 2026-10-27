from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import conectar
import os

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
@router.get("")
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
@router.post("")
def criar_agendamento(agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO agendamento
                (idcliente, idtatuador, dataagendamento, horaagendamento,
                 descricaotatuagem, valortatuagem, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
                agendamento.status or "pendente"
            )
        )
        novo_id = cursor.lastrowid
        conn.commit()
        return {"mensagem": "Agendamento cadastrado com sucesso", "idagendamento": novo_id}
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# GET /agendamentos/{id} - busca um agendamento pelo ID
@router.get("/{id}")
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


# PUT /agendamentos/{id} - atualiza um agendamento existente
@router.put("/{id}")
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
                valortatuagem = %s,
                status = %s
            WHERE idagendamento = %s
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
                agendamento.status or "pendente",
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


# DELETE /agendamentos/{id} - deleta um agendamento
@router.delete("/{id}")
def deletar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamento WHERE idagendamento = %s", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Agendamento deletado com sucesso"}


# POST /agendamentos/{id}/desenho - faz o upload de um desenho
@router.post("/{id}/desenho")
async def upload_desenho(id: int, arquivo: UploadFile = File(...)):
    nome_arquivo = f"{id}_{arquivo.filename}"
    caminho = os.path.join("uploads", nome_arquivo)

    conteudo = await arquivo.read()
    with open(caminho, "wb") as f:
        f.write(conteudo)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE agendamento SET desenhoaprovado=%s WHERE idagendamento=%s", (nome_arquivo, id))
    conn.commit()
    conn.close()  # Corrigido aqui: estava incompleto no texto original
    return {"mensagem": "Desenho enviado com sucesso", "arquivo": nome_arquivo}
