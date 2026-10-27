from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import conectar

router = APIRouter()


class EstilosDoTatuador(BaseModel):
    idestilos: List[int]


class Tatuador(BaseModel):
    nometatuador: str
    cpf: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    datacontratacao: Optional[str] = None
    idsenioridade: int


@router.get("")
def listar_tatuadores():
    conn = conectar()
    cursor = None

    try:
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
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.get("/{id}")
def buscar_tatuador(id: int):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM tatuador WHERE idtatuador = %s",
            (id,)
        )
        tatuador = cursor.fetchone()
        if tatuador is None:
            raise HTTPException(status_code=404, detail="Tatuador não encontrado")
        return tatuador
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.post("")
def criar_tatuador(tatuador: Tatuador):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tatuador
                (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                tatuador.nometatuador,
                tatuador.cpf,
                tatuador.email,
                tatuador.telefone,
                tatuador.datacontratacao,
                tatuador.idsenioridade
            )
        )
        conn.commit()
        return {"mensagem": "Tatuador cadastrado com sucesso", "idtatuador": cursor.lastrowid}
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.put("/{id}")
def atualizar_tatuador(id: int, tatuador: Tatuador):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tatuador
            SET nometatuador = %s,
                cpf = %s,
                email = %s,
                telefone = %s,
                datacontratacao = %s,
                idsenioridade = %s
            WHERE idtatuador = %s
            """,
            (
                tatuador.nometatuador,
                tatuador.cpf,
                tatuador.email,
                tatuador.telefone,
                tatuador.datacontratacao,
                tatuador.idsenioridade,
                id
            )
        )
        if cursor.rowcount == 0:
            cursor.execute("SELECT idtatuador FROM tatuador WHERE idtatuador = %s", (id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Tatuador não encontrado")
        conn.commit()
        return {"mensagem": "Tatuador atualizado com sucesso"}
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.delete("/{id}")
def deletar_tatuador(id: int):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tatuador WHERE idtatuador = %s", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tatuador não encontrado")
        conn.commit()
        return {"mensagem": "Tatuador deletado com sucesso"}
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.get("/{id}/estilos")
def listar_estilos_do_tatuador(id: int):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT idtatuador FROM tatuador WHERE idtatuador = %s", (id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Tatuador não encontrado")

        cursor.execute(
            """
            SELECT estilo.idestilo, estilo.descricao
            FROM tatuador_estilo
            JOIN estilo ON estilo.idestilo = tatuador_estilo.idestilo
            WHERE tatuador_estilo.idtatuador = %s
            """,
            (id,)
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


@router.put("/{id}/estilos")
def atualizar_estilos_do_tatuador(id: int, estilos: EstilosDoTatuador):
    conn = conectar()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT idtatuador FROM tatuador WHERE idtatuador = %s", (id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Tatuador não encontrado")

        cursor.execute("DELETE FROM tatuador_estilo WHERE idtatuador = %s", (id,))
        if estilos.idestilos:
            cursor.executemany(
                "INSERT INTO tatuador_estilo (idtatuador, idestilo) VALUES (%s, %s)",
                [(id, idestilo) for idestilo in estilos.idestilos]
            )
        conn.commit()
        return {"mensagem": "Estilos do tatuador atualizados com sucesso"}
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()
