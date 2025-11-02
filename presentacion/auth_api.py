"""
API de Autenticacion - Endpoints para login y registro

Estos endpoints usan el Gatekeeper para autenticar usuarios.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from patrones.gatekeeper import GestorGatekeeper, ErrorAutenticacion, ErrorAutorizacion
from patrones.federated_identity import GestorFederatedIdentity


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    """Credenciales del emulador de Google"""
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


@router.post("/auth/google/login")
def login_con_google(datos: GoogleLoginRequest):
    """
    Login usando Federated Identity con el emulador de Google.

    Nota importante:
    - Este endpoint es solo para la demo con el emulador de Google.
    - En un flujo OAuth real, se redirige al usuario a Google y luego
      se procesa un callback. Aquí simplificamos solicitando email/password
      del emulador y devolviendo NUESTRO token JWT.

    Body esperado:
    {
        "email": "juan@gmail.com",
        "password": "google123"
    }
    """
    gestor_fed = GestorFederatedIdentity()
    manager = gestor_fed.obtener_manager()

    resultado = manager.login_with_google(datos.email, datos.password)
    if not resultado:
        raise HTTPException(status_code=401, detail="Autenticacion con Google fallida")

    # Resultado ya contiene nuestro JWT y datos basicos del usuario
    return resultado


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


@router.get("/auth/google/validar")
def validar_token_google(authorization: Optional[str] = Header(None)):
    """
    Valida el token emitido por el flujo de Federated Identity (nuestro JWT).

    Header esperado:
    Authorization: <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    gestor_fed = GestorFederatedIdentity()
    manager = gestor_fed.obtener_manager()

    payload = manager.validate_token(authorization)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

    return {
        "exito": True,
        "valido": True,
        "usuario_id": payload.get("usuario_id"),
        "nombre": payload.get("nombre"),
        "email": payload.get("email"),
        "provider": payload.get("provider"),
    }


@router.get("/auth/stats")
def obtener_estadisticas_auth():
    """
    Endpoint para ver estadisticas del gatekeeper.
    Util para monitoreo.
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    return gatekeeper.obtener_estadisticas()
