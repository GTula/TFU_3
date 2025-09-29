from fastapi import FastAPI
from presentacion.product_api import router as product_router
from presentacion.client_api import router as client_router
from presentacion.order_api import router as order_router

app = FastAPI()

app.include_router(product_router)
app.include_router(client_router)
app.include_router(order_router)