from fastapi import FastAPI
from presentacion.product_api import router as producto_router
from presentacion.client_api import router as cliente_router
from presentacion.order_api import router as orden_router
from presentacion.proveedor_api import router as proveedor_router
from patrones.bulkhead import BulkheadManager

# Inicializar la aplicación FastAPI
app = FastAPI(title="E-Commerce API con Patrones de Resiliencia")

# Inicializar el gestor de Bulkheads
bulkhead_manager = BulkheadManager()

# Crear bulkheads separados para cada servicio
# Cada servicio tiene su propio pool de threads aislado
bulkhead_manager.create_bulkhead("productos", max_workers=5, timeout=30)
bulkhead_manager.create_bulkhead("clientes", max_workers=5, timeout=30)
bulkhead_manager.create_bulkhead("ordenes", max_workers=3, timeout=45)  # Menos workers, más timeout
bulkhead_manager.create_bulkhead("proveedores", max_workers=4, timeout=30)

# Endpoint para monitorear el estado de los bulkheads
@app.get("/bulkhead/stats")
def get_bulkhead_stats():
    """Retorna estadísticas de todos los bulkheads del sistema"""
    return bulkhead_manager.get_all_stats()

# Registrar routers
app.include_router(producto_router)
app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(proveedor_router)

# Evento de shutdown para cerrar los bulkheads limpiamente
@app.on_event("shutdown")
def shutdown_event():
    bulkhead_manager.shutdown_all()