from fastapi import APIRouter, HTTPException
from logica.proveedor_service import ProveedorService

router = APIRouter()
service = ProveedorService()

@router.get("/proveedores")
def listar_proveedores():
    return service.listarProveedores()

@router.get("/proveedores/{proveedor_id}")
def obtener_proveedor(proveedor_id: int):
    result = service.obtenerProveedor(proveedor_id)
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.post("/proveedores")
def agregar_proveedor(proveedor_data: dict):
    return service.agregarProveedor(proveedor_data)

@router.put("/proveedores/{proveedor_id}")
def actualizar_proveedor(proveedor_id: int, proveedor_data: dict):
    return service.actualizarProveedor(proveedor_id, proveedor_data)

@router.delete("/proveedores/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int):
    return service.eliminarProveedor(proveedor_id)