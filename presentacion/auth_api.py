"""
API de Autenticacion - Endpoints para login y registro

Estos endpoints usan el Gatekeeper para autenticar usuarios.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from patrones.gatekeeper import GestorGatekeeper, ErrorAutenticacion, ErrorAutorizacion


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("/auth/login")
def login(datos: LoginRequest):
    """
    Endpoint de login - autentica con email y password.
    
    Body esperado:
    {
        "email": "usuario@ejemplo.com",
        "password": "password123"
    }
    
    Retorna un token de autenticacion.
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    try:
        resultado = gatekeeper.login(datos.email, datos.password)
        return resultado
    except ErrorAutenticacion as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    """
    Endpoint de logout - revoca un token.
    
    Header esperado:
    Authorization: <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    # Revocar token
    revocado = gatekeeper.revocar_token(authorization)
    
    if revocado:
        return {
            "exito": True,
            "mensaje": "Logout exitoso"
        }
    else:
        raise HTTPException(status_code=404, detail="Token no encontrado")


@router.get("/auth/validar")
def validar_token(authorization: Optional[str] = Header(None)):
    """
    Endpoint para validar si un token es valido.
    
    Header esperado:
    Authorization: <token>
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    try:
        info = gatekeeper.validar_token(authorization)
        return {
            "exito": True,
            "valido": True,
            "usuario_id": info["usuario_id"],
            "nombre": info["nombre"],
            "email": info["email"],
            "rol": info["rol"]
        }
    except ErrorAutenticacion as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/auth/stats")
def obtener_estadisticas_auth():
    """
    Endpoint para ver estadisticas del gatekeeper.
    Util para monitoreo.
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    return gatekeeper.obtener_estadisticas()
