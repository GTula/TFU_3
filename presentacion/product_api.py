from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from logica.product_service import ProductoService
from concurrent.futures import TimeoutError
from patrones.gatekeeper import validar_autenticacion, validar_admin, ErrorAutenticacion, ErrorAutorizacion

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
    """
    Obtiene un producto especifico.
    PUBLICO - No requiere autenticacion.
    """
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
def agregar_producto(producto_data: dict, authorization: Optional[str] = Header(None)):
    """
    Agrega un nuevo producto.
    REQUIERE AUTENTICACION - Solo usuarios autenticados pueden agregar productos.
    
    Header requerido:
    Authorization: <token>
    """
    try:
        # Validar que el usuario este autenticado
        validar_autenticacion(authorization)
        
        return service.agregarProducto(producto_data)
    except ErrorAutenticacion as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/productos/{producto_id}")
def actualizar_producto(producto_id: int, producto_data: dict, authorization: Optional[str] = Header(None)):
    """
    Actualiza un producto.
    REQUIERE SER ADMIN - Solo administradores pueden actualizar productos.
    
    Header requerido:
    Authorization: <token de admin>
    """
    try:
        # Validar que el usuario sea admin
        validar_admin(authorization)
        
        return service.actualizarProducto(producto_id, producto_data)
    except ErrorAutenticacion as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ErrorAutorizacion as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, authorization: Optional[str] = Header(None)):
    """
    Elimina un producto.
    REQUIERE SER ADMIN - Solo administradores pueden eliminar productos.
    
    Header requerido:
    Authorization: <token de admin>
    """
    try:
        # Validar que el usuario sea admin
        validar_admin(authorization)
        
        return service.eliminarProducto(producto_id)
    except ErrorAutenticacion as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ErrorAutorizacion as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TimeoutError:
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible (timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))