from fastapi import APIRouter, HTTPException
from logica.client_service import obtener_todos_clientes, obtener_un_cliente, agregar_cliente

router = APIRouter()

@router.get("/clientes")
def get_clientes():
    return obtener_todos_clientes()

@router.get("/clientes/{client_id}")
def get_cliente(client_id: int):
    cli = obtener_un_cliente(client_id)
    if not cli:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cli

@router.post("/clientes")
def post_cliente(client: dict):
    try:
        return agregar_cliente(client)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))