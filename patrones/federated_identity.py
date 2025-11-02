"""
Patron Federated Identity - Emulador de proveedor externo (Google)

Este patron delega la autenticacion a un proveedor de identidad externo
(en este caso, simulamos Google OAuth).

El usuario se autentica con Google y nuestra app recibe un token
que valida con el proveedor externo.
"""

import jwt
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict


# ============================================================================
# EMULADOR DE GOOGLE OAUTH (Servicio Externo)
# ============================================================================

class GoogleOAuthEmulator:
    """
    Simula el servicio de autenticacion de Google.
    
    Aqui lo emulamos para demostrar el patron.
    """
    
    # Base de datos simulada de usuarios de Google
    GOOGLE_USERS = {
        "juan@gmail.com": {
            "id": "google_12345",
            "email": "juan@gmail.com",
            "name": "Juan Pérez",
            "picture": "https://lh3.googleusercontent.com/a/default-user",
            "password": "google123"  
        },
        "maria@gmail.com": {
            "id": "google_67890",
            "email": "maria@gmail.com",
            "name": "María González",
            "picture": "https://lh3.googleusercontent.com/a/maria-pic",
            "password": "google456"
        }
    }
    
    GOOGLE_SECRET = "clave-secreta-de-google"
    
    def __init__(self):
        print("[GoogleOAuth] Emulador de Google OAuth iniciado")
    
    def authenticate(self, email: str, password: str) -> Optional[str]:
        """
        Simula la autenticacion con Google.
        
        En la realidad, el usuario seria redirigido a la pagina de Google,
        ingresaria sus credenciales alli, y Google retornaria un codigo.
        
        Args:
            email: Email del usuario de Google
            password: Password del usuario de Google
            
        Returns:
            str: Codigo de autorizacion (authorization code)
        """
        user = self.GOOGLE_USERS.get(email)
        
        if not user or user["password"] != password:
            print(f"[GoogleOAuth] Autenticacion fallida para {email}")
            return None
        
        # Generar codigo de autorizacion
        code = hashlib.sha256(f"{email}:{time.time()}".encode()).hexdigest()
        
        if not hasattr(self, 'auth_codes'):
            self.auth_codes = {}
        
        self.auth_codes[code] = {
            "user": user,
            "expires": time.time() + 600  # expira en 10 minutos
        }
        
        print(f"[GoogleOAuth] Usuario autenticado: {user['name']}")
        print(f"[GoogleOAuth] Codigo de autorizacion generado: {code[:20]}...")
        
        return code
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """
        Intercambia el codigo de autorizacion por un token de acceso.
        
        Esto simula el endpoint de Google para obtener tokens.
        
        Args:
            code: Codigo de autorizacion
            
        Returns:
            dict: Token de acceso y informacion del usuario
        """
        if not hasattr(self, 'auth_codes') or code not in self.auth_codes:
            print("[GoogleOAuth] Codigo invalido")
            return None
        
        auth_data = self.auth_codes[code]
        
        # Verificar expiracion
        if time.time() > auth_data["expires"]:
            print("[GoogleOAuth] Codigo expirado")
            del self.auth_codes[code]
            return None
        
        user = auth_data["user"]
        
        # Generar token JWT de Google
        ahora = datetime.now()
        expira = ahora + timedelta(hours=1)
        
        payload = {
            "sub": user["id"],  # Subject (ID del usuario)
            "email": user["email"],
            "name": user["name"],
            "picture": user["picture"],
            "iss": "https://accounts.google.com",  # Issuer
            "aud": "mi-app-cliente-id",  # Audience
            "exp": int(expira.timestamp()),
            "iat": int(ahora.timestamp())
        }
        
        google_token = jwt.encode(payload, self.GOOGLE_SECRET, algorithm="HS256")
        
        # Eliminar codigo (solo se puede usar una vez)
        del self.auth_codes[code]
        
        print(f"[GoogleOAuth] Token de acceso generado para {user['name']}")
        
        return {
            "access_token": google_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": google_token,
            "user_info": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user["picture"]
            }
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifica un token de Google.
        
        Args:
            token: Token JWT de Google
            
        Returns:
            dict: Informacion del usuario si el token es valido
        """
        try:
            # Nota: Deshabilitamos la verificacion de 'aud' en el emulador
            # porque no estamos pasando un audience real en el decode.
            payload = jwt.decode(
                token,
                self.GOOGLE_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            print(f"[GoogleOAuth] Token verificado para {payload['email']}")
            return payload
        except jwt.ExpiredSignatureError:
            print("[GoogleOAuth] Token expirado")
            return None
        except jwt.InvalidTokenError:
            print("[GoogleOAuth] Token invalido")
            return None


# ============================================================================
# FEDERATED IDENTITY MANAGER (Nuestra Aplicacion)
# ============================================================================

class FederatedIdentityManager:
    """
    Gestor de identidad federada.
    
    Se encarga de:
    1. Redirigir al usuario al proveedor externo (Google)
    2. Recibir el codigo de autorizacion
    3. Intercambiar el codigo por un token
    4. Crear/actualizar el usuario en nuestra base de datos
    5. Generar nuestro propio JWT para la sesion
    """
    
    # Nuestra clave secreta (diferente a la de Google)
    OUR_SECRET = "clave-ut4"
    
    def __init__(self, google_oauth: GoogleOAuthEmulator):
        self.google_oauth = google_oauth
        # Mapeo de usuarios externos a usuarios internos
        self.federated_users = {}
        print("[FederatedIdentity] Gestor de identidad federada iniciado")
    
    def login_with_google(self, google_email: str, google_password: str) -> Optional[Dict]:
        """
        Inicia el flujo de autenticacion con Google.
        
        Pasos:
        1. Redirige al usuario al emulador
        2. Usuario se autentica con el servicio externo
        3. El servicio externo retorna codigo de autorizacion
        4. Intercambiamos codigo por token
        5. Creamos/actualizamos usuario en nuestra app
        6. Generamos nuestro propio token
        
        Args:
            google_email: Email del usuario en Google
            google_password: Password del usuario en Google
            
        Returns:
            dict: Nuestro token y datos del usuario
        """
        print(f"\n[FederatedIdentity] Iniciando login con Google para {google_email}")
        
        # Paso 1 y 2: Usuario se autentica con Google
        auth_code = self.google_oauth.authenticate(google_email, google_password)
        
        if not auth_code:
            print("[FederatedIdentity] Autenticacion con Google fallida")
            return None
        
        # Paso 3 y 4: Intercambiar codigo por token de Google
        google_response = self.google_oauth.exchange_code_for_token(auth_code)
        
        if not google_response:
            print("[FederatedIdentity] Error al obtener token de Google")
            return None
        
        # Paso 5: Verificar el token de Google
        google_user = self.google_oauth.verify_token(google_response["access_token"])
        
        if not google_user:
            print("[FederatedIdentity] Token de Google invalido")
            return None
        
        # Paso 6: Crear/actualizar usuario en nuestra base de datos
        user_id = self._create_or_update_user(google_user)
        
        # Paso 7: Generar nuestro propio JWT
        ahora = datetime.now()
        expira = ahora + timedelta(hours=24)

        our_payload = {
            "usuario_id": user_id,
            "email": google_user["email"],
            "nombre": google_user["name"],
            "picture": google_user["picture"],
            "provider": "google",
            "provider_id": google_user["sub"],
            "exp": int(expira.timestamp()),
            "iat": int(ahora.timestamp())
        }
        
        our_token = jwt.encode(our_payload, self.OUR_SECRET, algorithm="HS256")
        
        print(f"[FederatedIdentity] Usuario autenticado: {google_user['name']}")
        print(f"[FederatedIdentity] Token de nuestra app generado")
        return {
            "token": our_token,
            "usuario_id": user_id,
            "email": google_user["email"],
            "nombre": google_user["name"],
            "picture": google_user["picture"],
            "provider": "google"
        }
    
    def _create_or_update_user(self, google_user: Dict) -> str:
        """
        Crea o actualiza un usuario en nuestra base de datos.
        
        Args:
            google_user: Informacion del usuario de Google
            
        Returns:
            str: ID del usuario en nuestra app
        """
        provider_id = google_user["sub"]
        
        # Verificar si el usuario ya existe
        if provider_id in self.federated_users:
            # Actualizar informacion
            self.federated_users[provider_id].update({
                "email": google_user["email"],
                "name": google_user["name"],
                "picture": google_user["picture"],
                "last_login": datetime.now()
            })
            print(f"[FederatedIdentity] Usuario actualizado: {google_user['name']}")
        else:
            # Crear nuevo usuario
            user_id = f"user_{len(self.federated_users) + 1}"
            self.federated_users[provider_id] = {
                "id": user_id,
                "provider": "google",
                "provider_id": provider_id,
                "email": google_user["email"],
                "name": google_user["name"],
                "picture": google_user["picture"],
                "created_at": datetime.now(),
                "last_login": datetime.now()
            }
            print(f"[FederatedIdentity] Nuevo usuario creado: {google_user['name']}")
        
        return self.federated_users[provider_id]["id"]
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Valida nuestro token.
        
        Args:
            token: Nuestro JWT
            
        Returns:
            dict: Informacion del usuario
        """
        try:
            payload = jwt.decode(token, self.OUR_SECRET, algorithms=["HS256"])
            print(f"[FederatedIdentity] Token valido para {payload['nombre']}")
            return payload
        except jwt.ExpiredSignatureError:
            print("[FederatedIdentity] Token expirado")
            return None
        except jwt.InvalidTokenError:
            print("[FederatedIdentity] Token invalido")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene informacion de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Informacion del usuario
        """
        for user in self.federated_users.values():
            if user["id"] == user_id:
                return user
        return None


# ============================================================================
# SINGLETON
# ============================================================================

class GestorFederatedIdentity:
    """Singleton para acceso global al gestor de identidad federada"""
    
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            # Inicializar emulador de Google y gestor
            google_emulator = GoogleOAuthEmulator()
            cls._instancia.manager = FederatedIdentityManager(google_emulator)
        return cls._instancia
    
    def obtener_manager(self):
        return self.manager
