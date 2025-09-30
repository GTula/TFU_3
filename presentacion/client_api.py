from fastapi import APIRouter, HTTPException
from logica.client_service import ClienteService

router = APIRouter()
service = ClienteService()

@router.post("/clientes")
def registrar_cliente(cliente_data: dict):
    return service.registrarCliente(cliente_data)

@router.post("/clientes/login")
def login_cliente(data: dict):
    result = service.loginCliente(data["email"], data["password"])
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return result

@router.put("/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente_data: dict):
    return service.actualizarCliente(cliente_id, cliente_data)

@router.get("/clientes/{cliente_id}")
def obtener_cliente(cliente_id: int):
    result = service.obtenerCliente(cliente_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result