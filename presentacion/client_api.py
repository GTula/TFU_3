from fastapi import APIRouter, HTTPException
from logica.client_service import ClienteService

router = APIRouter()
service = ClienteService()

@router.post("/clientes")
def registrar_cliente(cliente_data: dict):
    return service.registrarCliente(cliente_data)

@router.post("/clientes/login")
def login_cliente(data: dict):
    result = service.loginCliente(data["email"], data["password"])
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    return result

@router.put("/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente_data: dict):
    return service.actualizarCliente(cliente_id, cliente_data)

@router.get("/clientes/{cliente_id}")
def obtener_cliente(cliente_id: int):
    result = service.obtenerCliente(cliente_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result


# endpoints para pagos protegidos con el circuit breaker

@router.post("/clientes/{cliente_id}/pagos")
def procesar_pago(cliente_id: int, pago_data: dict):
    """
    Procesa un pago para un cliente.
    Protegido con Circuit Breaker para evitar llamadas a un servicio caido.
    
    Body esperado:
    {
        "monto": 100.50,
        "metodo_pago": "tarjeta"  (opcional)
    }
    """
    monto = pago_data.get("monto")
    metodo_pago = pago_data.get("metodo_pago", "tarjeta")
    
    if not monto or monto <= 0:
        raise HTTPException(status_code=400, detail="Monto invalido")
    
    resultado = service.realizar_pago(cliente_id, monto, metodo_pago)
    
    if resultado["exito"]:
        return resultado
    else:
        # el pago falló - retornar error apropiado
        raise HTTPException(
            status_code=503,
            detail=resultado["mensaje"]
        )


@router.get("/clientes/pagos/{transaccion_id}")
def verificar_pago(transaccion_id: str):
    """
    Verifica el estado de un pago por su ID de transaccion.
    Tambien protegido con Circuit Breaker.
    """
    resultado = service.verificar_estado_pago(transaccion_id)
    
    if resultado["exito"]:
        return resultado
    else:
        raise HTTPException(status_code=503, detail=resultado["mensaje"])


@router.get("/clientes/pagos/estadisticas/general")
def obtener_estadisticas_pagos():
    """
    Retorna estadisticas del servicio de pagos y del circuit breaker.
    Util para monitorear el estado del sistema.
    """
    return service.obtener_estadisticas_pagos()


@router.post("/clientes/pagos/configurar/fallos")
def configurar_tasa_fallos(config: dict):
    """
    SOLO PARA PRUEBAS: Configura la tasa de fallo del servicio de pagos.
    
    Body:
    {
        "tasa_fallo": 0.5  // 0.0 = sin fallos, 0.5 = 50% fallos
    }
    """
    tasa = config.get("tasa_fallo", 0.0)
    if tasa < 0 or tasa > 1:
        raise HTTPException(status_code=400, detail="Tasa debe estar entre 0.0 y 1.0")
    
    service.simular_fallos_pagos(tasa)
    return {"mensaje": f"Tasa de fallo configurada a {tasa*100}%"}