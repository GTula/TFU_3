"""
Patron Gatekeeper - Validacion y seguridad 

El Gatekeeper actúa como una puerta de entrada que valida
las peticiones antes de permitir el acceso a los servicios internos.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from persistencia.client_repo import ClienteRepo

# Clave secreta para firmar los JWT (en produccion esto deberia estar en variables de entorno)
SECRET_KEY = "patrones-ut4"
ALGORITHM = "HS256"
TOKEN_EXPIRACION_HORAS = 24

# error cunando la autenticacion falla
class ErrorAutenticacion(Exception):
    pass

# error cuadno el usuario no tiene permisos
class ErrorAutorizacion(Exception):
    pass


class Gatekeeper:
    """
    Valida tokens y permisos
    """
    
    def __init__(self):
        self.cliente_repo = ClienteRepo()
        
        print("[Gatekeeper] Inicializado")
    
    def login(self, email, password):
        """
        Autentica un usuario y genera un JWT.
        
        Args:
            email: Email del usuario
            password: Password del usuario
            
        Returns:
            dict: JWT y datos del usuario
            
        Raises:
            ErrorAutenticacion: Si las credenciales son invalidas
        """
        # Buscar usuario en la base de datos
        usuario = self.cliente_repo.login(email, password)
        
        if not usuario:
            raise ErrorAutenticacion("Credenciales invalidas")
        
        # Obtener el rol (si existe en la BD, sino usar 'usuario' por defecto)
        rol = usuario.get('rol', 'usuario')
        
        # Crear payload del JWT
        payload = {
            "usuario_id": usuario['id'],
            "nombre": usuario['name'],
            "email": usuario['email'],
            "rol": rol,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRACION_HORAS),
            "iat": datetime.utcnow()
        }
        
        # Generar JWT
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        print(f"[Gatekeeper] Login exitoso para {email} (rol: {rol})")
        
        return {
            "token": token,
            "usuario_id": usuario['id'],
            "nombre": usuario['name'],
            "email": usuario['email'],
            "rol": rol
        }
    
    def validar_token(self, token):
        """
        Valida si un token es valido.
        
        Args:
            token: Token a validar
            
        Returns:
            dict: Informacion del usuario contenida en el JWT
            
        Raises:
            ErrorAutenticacion: Si el token no es valido o expiro
        """
        if not token:
            raise ErrorAutenticacion("No se proporciono token de autenticacion")
        
        try:
            # Decodificar y validar JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            print(f"[Gatekeeper] Token valido para usuario {payload['usuario_id']} ({payload['nombre']})")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ErrorAutenticacion("Token expirado")
        except jwt.InvalidTokenError:
            raise ErrorAutenticacion("Token invalido")
    
    def validar_permiso(self, token, permiso_requerido):
        """
        Valida si un token tiene un permiso especifico.
        
        Args:
            token: Token del usuario
            permiso_requerido: Permiso necesario (ej: "admin", "usuario")
            
        Returns:
            dict: Informacion del usuario
            
        Raises:
            ErrorAutenticacion: Si el token no es valido
            ErrorAutorizacion: Si no tiene el permiso
        """
        # Primero validar el token
        info = self.validar_token(token)
        
        # Verificar permisos
        rol_usuario = info["rol"]
        
        if permiso_requerido == "admin" and rol_usuario != "admin":
            raise ErrorAutorizacion(
                f"Se requiere rol 'admin'. Usuario tiene rol '{rol_usuario}'"
            )
        
        print(f"[Gatekeeper] Usuario {info['usuario_id']} autorizado para {permiso_requerido}")
        return info
    
    def revocar_token(self, token):
        """
        Con JWT no se pueden revocar tokens directamente.
        
        Para revocar tokens con JWT necesitarias:
        - Lista negra de tokens en BD o cache
        - Reducir el tiempo de expiracion
        - Usar refresh tokens
        
        Por ahora solo retornamos True para compatibilidad.
        """
        print("[Gatekeeper] Advertencia: JWT no soporta revocacion directa")
        return True
    
    def obtener_estadisticas(self):
        """
        Con JWT no hay tokens guardados para contar.
        Retorna info basica.
        """
        return {
            "tipo": "JWT",
            "expiracion_horas": TOKEN_EXPIRACION_HORAS,
            "algorithm": ALGORITHM
        }


class GestorGatekeeper:
    """
    Gestor central del Gatekeeper (Singleton).
    Permite acceso global al gatekeeper.
    """
    
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.gatekeeper = Gatekeeper()
        return cls._instancia
    
    def obtener_gatekeeper(self):
        """Retorna la instancia del gatekeeper"""
        return self.gatekeeper


# Funciones auxiliares para usar en FastAPI

def validar_autenticacion(token: Optional[str]):
    """
    Funcion auxiliar para validar autenticacion en endpoints.
    
    Args:
        token: Token de autenticacion
        
    Returns:
        dict: Informacion del usuario
        
    Raises:
        ErrorAutenticacion: Si no esta autenticado
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    return gatekeeper.validar_token(token)


def validar_admin(token: Optional[str]):
    """
    Funcion auxiliar para validar que el usuario sea admin.
    
    Args:
        token: Token de autenticacion
        
    Returns:
        dict: Informacion del usuario
        
    Raises:
        ErrorAutenticacion: Si no esta autenticado
        ErrorAutorizacion: Si no es admin
    """
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    return gatekeeper.validar_permiso(token, "admin")
