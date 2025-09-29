from fastapi import APIRouter, HTTPException
from logica.product_service import obtener_todos_productos, obtener_un_producto, agregar_producto

router = APIRouter()

@router.get("/productos")
def get_productos():
    return obtener_todos_productos()

@router.get("/productos/{product_id}")
def get_producto(product_id: int):
    prod = obtener_un_producto(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@router.post("/productos")
def post_producto(product: dict):
    try:
        return agregar_producto(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))