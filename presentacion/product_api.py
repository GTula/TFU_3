from fastapi import APIRouter, HTTPException
from logica.product_service import ProductoService

router = APIRouter()
service = ProductoService()

@router.get("/productos")
def listar_productos():
    return service.listarProductos()

@router.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    result = service.obtenerProducto(producto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result

@router.post("/productos")
def agregar_producto(producto_data: dict):
    return service.agregarProducto(producto_data)

@router.put("/productos/{producto_id}")
def actualizar_producto(producto_id: int, producto_data: dict):
    return service.actualizarProducto(producto_id, producto_data)

@router.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    return service.eliminarProducto(producto_id)