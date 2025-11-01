from fastapi import APIRouter, HTTPException
from logica.product_service import ProductoService
from concurrent.futures import TimeoutError

router = APIRouter()
service = ProductoService()

@router.get("/productos")
def listar_productos():
    """
    Lista todos los productos.
    Protegido por Bulkhead - si el servicio se sobrecarga, fallará aisladamente.
    """
    try:
        return service.listarProductos()
    except TimeoutError:
        raise HTTPException(
            status_code=500,
            detail="Servicio de productos temporalmente no disponible (timeout)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Servicio de productos temporalmente no disponible"
        )

@router.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    try:
        result = service.obtenerProducto(producto_id)
        if not result:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return result
    except HTTPException:
        raise  # Re-lanzar HTTPExceptions
    except TimeoutError:
        raise HTTPException(
            status_code=500,
            detail="Servicio de productos temporalmente no disponible (timeout)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible")

@router.post("/productos")
def agregar_producto(producto_data: dict):
    try:
        return service.agregarProducto(producto_data)
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/productos/{producto_id}")
def actualizar_producto(producto_id: int, producto_data: dict):
    try:
        return service.actualizarProducto(producto_id, producto_data)
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    try:
        return service.eliminarProducto(producto_id)
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))