from fastapi import FastAPI

from infraestructura.config_store import cfg
from patrones.bulkhead import BulkheadManager
from patrones.circuit_breaker import GestorCircuitBreakers
from patrones.gatekeeper import GestorGatekeeper

# Inicializar la aplicación FastAPI
app = FastAPI(title="E-Commerce API con Patrones de Resiliencia")

# se inicializa el gestor de Bulkheads y Circuit Breakers antes de importar los routers
# De este modo, los servicios que se importen (y pidan bulkheads) los encontrarán creados.
bulkhead_manager = BulkheadManager()


# bulkhead sizes/timeouts configurables vía ConfigStore (env/Consul)
bulkhead_manager.create_bulkhead(
    "productos",
    max_workers=cfg.get("BULKHEAD_PRODUCTOS_WORKERS", default=5, as_type=int),
    timeout=cfg.get("BULKHEAD_PRODUCTOS_TIMEOUT", default=30, as_type=int),
)
bulkhead_manager.create_bulkhead(
    "clientes",
    max_workers=cfg.get("BULKHEAD_CLIENTES_WORKERS", default=5, as_type=int),
    timeout=cfg.get("BULKHEAD_CLIENTES_TIMEOUT", default=30, as_type=int),
)
bulkhead_manager.create_bulkhead(
    "ordenes",
    max_workers=cfg.get("BULKHEAD_ORDENES_WORKERS", default=3, as_type=int),
    timeout=cfg.get("BULKHEAD_ORDENES_TIMEOUT", default=45, as_type=int),
)
bulkhead_manager.create_bulkhead(
    "proveedores",
    max_workers=cfg.get("BULKHEAD_PROVEEDORES_WORKERS", default=4, as_type=int),
    timeout=cfg.get("BULKHEAD_PROVEEDORES_TIMEOUT", default=30, as_type=int),
)


print("\n--- Inicializando Circuit Breakers ---")
circuit_breaker_manager = GestorCircuitBreakers()
circuit_breaker_manager.crear_circuit_breaker(
    "servicio_pagos",
    max_fallos=cfg.get("CB_PAGOS_MAX_FALLOS", default=3, as_type=int),
    timeout_abierto=cfg.get("CB_PAGOS_TIMEOUT_ABIERTO", default=60, as_type=int),
    timeout_semi_abierto=cfg.get("CB_PAGOS_TIMEOUT_SEMI", default=30, as_type=int),
)
print("--- Circuit Breakers inicializados ---\n")

# Inicializar el Gatekeeper
print("--- Inicializando Gatekeeper ---")
gatekeeper_manager = GestorGatekeeper()
print("--- Gatekeeper inicializado ---\n")

# Endpoint para monitorear el estado de los bulkheads
@app.get("/bulkhead/stats")
def get_bulkhead_stats():
    """Retorna estadísticas de todos los bulkheads del sistema"""
    return bulkhead_manager.get_all_stats()


@app.get("/circuit-breaker/stats")
def get_circuit_breaker_stats():
    return circuit_breaker_manager.obtener_todas_estadisticas()

# Ahora importamos y registramos los routers (después de crear los recursos)
from presentacion.product_api import router as producto_router
from presentacion.client_api import router as cliente_router
from presentacion.order_api import router as orden_router
from presentacion.proveedor_api import router as proveedor_router


# Registrar routers
app.include_router(auth_router)  # Router de autenticacion
app.include_router(producto_router)
app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(proveedor_router)


@app.on_event("shutdown")
def shutdown_event():
    bulkhead_manager.shutdown_all()