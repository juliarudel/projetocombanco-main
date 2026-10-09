from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from rotas import clientes, senioridade   # ← adiciona senioridade aqui

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(senioridade.router)   # ← registra a nova rota


@app.get("/")
def inicio():
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}

from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from rotas import clientes, senioridade, tatuadores   # ← adiciona tatuadores aqui

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(senioridade.router)
app.include_router(tatuadores.router)   # ← registra a nova rota


@app.get("/")
def inicio():
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}