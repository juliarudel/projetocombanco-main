from fastapi import APIRouter        # organiza rotas em grupos
from pydantic import BaseModel      # valida os dados que chegam na API
from typing import Optional         # permite campos opcionais
from database import conectar       # nossa função de conexão

router = APIRouter()                # cria o grupo de rotas
