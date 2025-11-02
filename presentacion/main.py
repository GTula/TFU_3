from fastapi import FastAPI
from patrones.bulkhead import BulkheadManager
from patrones.circuit_breaker import GestorCircuitBreakers

# Inicializar la aplicación FastAPI
app = FastAPI(title="E-Commerce API con Patrones de Resiliencia")

# Inicializar el gestor de Bulkheads y Circuit Breakers ANTES de importar los routers
# De este modo, los servicios que se importen (y pidan bulkheads) los encontrarán creados.
bulkhead_manager = BulkheadManager()
bulkhead_manager.create_bulkhead("productos", max_workers=5, timeout=30)
bulkhead_manager.create_bulkhead("clientes", max_workers=5, timeout=30)
bulkhead_manager.create_bulkhead("ordenes", max_workers=3, timeout=45)
bulkhead_manager.create_bulkhead("proveedores", max_workers=4, timeout=30)

print("\n--- Inicializando Circuit Breakers ---")
circuit_breaker_manager = GestorCircuitBreakers()
circuit_breaker_manager.crear_circuit_breaker(
    "servicio_pagos",
    max_fallos=3,
    timeout_abierto=60,
    timeout_semi_abierto=30
)
print("--- Circuit Breakers inicializados ---\n")

# Endpoints para monitoreo
@app.get("/bulkhead/stats")
def get_bulkhead_stats():
    return bulkhead_manager.get_all_stats()


@app.get("/circuit-breaker/stats")
def get_circuit_breaker_stats():
    return circuit_breaker_manager.obtener_todas_estadisticas()

# Ahora importamos y registramos los routers (después de crear los recursos)
from presentacion.product_api import router as producto_router
from presentacion.client_api import router as cliente_router
from presentacion.order_api import router as orden_router
from presentacion.proveedor_api import router as proveedor_router

app.include_router(producto_router)
app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(proveedor_router)


@app.on_event("shutdown")
def shutdown_event():
    bulkhead_manager.shutdown_all()