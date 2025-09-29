from fastapi import APIRouter, HTTPException
from logica.order_service import obtener_todas_ordenes, obtener_una_orden, agregar_orden

router = APIRouter()

@router.get("/ordenes")
def get_ordenes():
    return obtener_todas_ordenes()

@router.get("/ordenes/{order_id}")
def get_orden(order_id: int):
    ord = obtener_una_orden(order_id)
    if not ord:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return ord

@router.post("/ordenes")
def post_orden(order: dict):
    try:
        return agregar_orden(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))