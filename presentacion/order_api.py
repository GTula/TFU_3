from fastapi import APIRouter, HTTPException, status
from logica.order_service import OrdenService
from logica.client_service import ClienteService
from patrones.queue import publish_order

router = APIRouter()
service = OrdenService()
client_service = ClienteService()

@router.post("/ordenes", status_code=status.HTTP_201_CREATED)
def crear_orden(orden_data: dict):
    client_id = orden_data.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="Falta client_id en la orden")

    if not client_service.obtenerCliente(client_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    order = service.crearOrden(orden_data)

    try:
        publish_order(order_id=order["id"], payload={"client_id": order["client_id"]})
    except Exception as e:
        # No dejamos que falle la creación por un fallo de la cola; loguea/alerta aquí.
        print(f"[WARN] fallo al publicar orden {order['id']} en la cola: {e}")

    return order

@router.get("/ordenes/{orden_id}")
def obtener_orden(orden_id: int):
    result = service.obtenerOrden(orden_id)
    if not result:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return result

@router.get("/ordenes")
def listar_ordenes():
    return service.listarOrdenes()