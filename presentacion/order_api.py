from fastapi import APIRouter, HTTPException
from logica.order_service import OrdenService

router = APIRouter()
service = OrdenService()

@router.post("/ordenes")
def crear_orden(orden_data: dict):
    return service.crearOrden(orden_data)

@router.get("/ordenes/{orden_id}")
def obtener_orden(orden_id: int):
    result = service.obtenerOrden(orden_id)
    if not result:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return result

@router.get("/ordenes")
def listar_ordenes():
    return service.listarOrdenes()