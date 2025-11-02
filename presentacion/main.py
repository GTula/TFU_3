from fastapi import FastAPI
from presentacion.product_api import router as producto_router
from presentacion.client_api import router as cliente_router
from presentacion.order_api import router as orden_router
from presentacion.proveedor_api import router as proveedor_router
from presentacion.auth_api import router as auth_router
from patrones.bulkhead import BulkheadManager
from patrones.circuit_breaker import GestorCircuitBreakers
from patrones.gatekeeper import GestorGatekeeper

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

# Inicializar el gestor de Circuit Breakers
print("\n--- Inicializando Circuit Breakers ---")
circuit_breaker_manager = GestorCircuitBreakers()

# Crear circuit breaker para el servicio de pagos
# max_fallos=3: Se abre despues de 3 fallos consecutivos
# timeout_abierto=60: Permanece abierto por 60 segundos
# timeout_semi_abierto=30: Prueba por 30 segundos antes de cerrar
circuit_breaker_manager.crear_circuit_breaker(
    "servicio_pagos",
    max_fallos=3,
    timeout_abierto=60,
    timeout_semi_abierto=30
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


# Endpoint para monitorear el estado de los circuit breakers
@app.get("/circuit-breaker/stats")
def get_circuit_breaker_stats():
    """Retorna estadisticas de todos los circuit breakers del sistema"""
    return circuit_breaker_manager.obtener_todas_estadisticas()


# Registrar routers
app.include_router(auth_router)  # Router de autenticacion
app.include_router(producto_router)
app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(proveedor_router)

# Evento de shutdown para cerrar los bulkheads limpiamente
@app.on_event("shutdown")
def shutdown_event():
    bulkhead_manager.shutdown_all()