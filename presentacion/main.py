from fastapi import FastAPI
from presentacion.product_api import router as producto_router
from presentacion.client_api import router as cliente_router
from presentacion.order_api import router as orden_router
from presentacion.proveedor_api import router as proveedor_router

app = FastAPI()
app.include_router(producto_router)
app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(proveedor_router)