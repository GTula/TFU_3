"""
Demo del patron Federated Identity con emulador de Google OAuth

Muestra como:
1. Usuario se autentica con Google (emulado)
2. Google retorna un codigo de autorizacion
3. Nuestra app intercambia el codigo por un token de Google
4. Creamos/actualizamos el usuario en nuestra base de datos
5. Generamos nuestro propio token para la sesion
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patrones.federated_identity import GestorFederatedIdentity


def demo_login_con_google():
    """Demuestra el login con Google"""
    print("\n\n=== DEMO: LOGIN CON GOOGLE (FEDERATED IDENTITY) ===\n")
    
    gestor = GestorFederatedIdentity()
    manager = gestor.obtener_manager()
    print("----------------------------------- MANAGER:", manager)
    
    # Usuario 1: Login exitoso
    print("1. Usuario intenta hacer login con Google...")
    resultado = manager.login_with_google("juan@gmail.com", "google123")
    
    if resultado:
        print(f"\n   Login exitoso!")
        print(f"   Nombre: {resultado['nombre']}")
        print(f"   Email: {resultado['email']}")
        print(f"   Provider: {resultado['provider']}")
        print(f"   Token: {resultado['token'][:50]}...")
        
        token = resultado['token']
        
        # Validar nuestro token
        print("\n2. Validando token de nuestra app...")
        info = manager.validate_token(token)
        print(f"   Token valido para: {info['nombre']}")
        print(f"   Proveedor de identidad: {info['provider']}")
        print(f"   ID del proveedor: {info['provider_id']}")
    else:
        print("   Login fallido")


def demo_login_fallido():
    """Demuestra un login fallido"""
    print("\n\n=== DEMO: LOGIN FALLIDO ===\n")
    
    gestor = GestorFederatedIdentity()
    manager = gestor.obtener_manager()
    
    print("1. Usuario intenta login con credenciales incorrectas...")
    resultado = manager.login_with_google("juan@gmail.com", "password_incorrecta")
    
    if not resultado:
        print("   Login fallido (esperado)")


def demo_multiples_usuarios():
    """Demuestra multiples usuarios de Google"""
    print("\n\n=== DEMO: MULTIPLES USUARIOS ===\n")
    
    gestor = GestorFederatedIdentity()
    manager = gestor.obtener_manager()
    
    # Login de usuario 1
    print("1. Juan hace login con Google...")
    usuario1 = manager.login_with_google("juan@gmail.com", "google123")
    print(f"   Usuario 1: {usuario1['nombre']}")
    
    # Login de usuario 2
    print("\n2. Maria hace login con Google...")
    usuario2 = manager.login_with_google("maria@gmail.com", "google456")
    print(f"   Usuario 2: {usuario2['nombre']}")
    
    # Ambos tokens son validos
    print("\n3. Validando ambos tokens...")
    info1 = manager.validate_token(usuario1['token'])
    info2 = manager.validate_token(usuario2['token'])
    print(f"   Token 1 valido: {info1['nombre']}")
    print(f"   Token 2 valido: {info2['nombre']}")


def demo_usuario_existente():
    """Demuestra login de usuario que ya existe"""
    print("\n\n=== DEMO: USUARIO EXISTENTE ===\n")
    
    gestor = GestorFederatedIdentity()
    manager = gestor.obtener_manager()
    
    # Primer login
    print("1. Juan hace login por primera vez...")
    login1 = manager.login_with_google("juan@gmail.com", "google123")
    user_id_1 = login1['usuario_id']
    print(f"   Usuario creado con ID: {user_id_1}")
    
    # Segundo login (mismo usuario)
    print("\n2. Juan hace login nuevamente...")
    login2 = manager.login_with_google("juan@gmail.com", "google123")
    user_id_2 = login2['usuario_id']
    print(f"   Usuario actualizado con ID: {user_id_2}")
    
    # Verificar que es el mismo usuario
    if user_id_1 == user_id_2:
        print(f"\n   Correcto: Es el mismo usuario (ID: {user_id_1})")
    else:
        print(f"\n   Error: IDs diferentes")


def demo_info_completa():
    """Muestra toda la informacion del flujo"""
    print("\n\n=== DEMO: FLUJO COMPLETO DE FEDERATED IDENTITY ===\n")
    
    gestor = GestorFederatedIdentity()
    
    manager = gestor.obtener_manager()
    
    print("PASO 1: Usuario hace click en 'Login con Google'")
    print("        (En la vida real, seria redirigido a Google)")
    
    print("\nPASO 2: Usuario ingresa credenciales en Google")
    print("        Email: juan@gmail.com")
    print("        Password: ******")
    
    print("\nPASO 3: Google autentica al usuario y genera codigo")
    
    print("\nPASO 4: Nuestra app intercambia codigo por token de Google")
    
    print("\nPASO 5: Creamos/actualizamos usuario en nuestra base de datos")
    
    print("\nPASO 6: Generamos nuestro propio token para la sesion")
    
    print("\n>>> Ejecutando flujo completo...")
    resultado = manager.login_with_google("juan@gmail.com", "google123")
    
    print(f"\n>>> RESULTADO:")
    print(f"    Usuario autenticado: {resultado['nombre']}")
    print(f"    Email: {resultado['email']}")
    print(f"    Proveedor: {resultado['provider']}")
    print(f"    Token de nuestra app: {resultado['token'][:50]}...")
    
    print(f"\n>>> VENTAJAS DE FEDERATED IDENTITY:")
    print(f"    - No guardamos passwords de usuarios")
    print(f"    - Google maneja la seguridad")
    print(f"    - Usuario puede usar su cuenta existente")
    print(f"    - Un solo login para multiples apps")


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO: PATRON FEDERATED IDENTITY")
    print("Emulador de Google OAuth")
    print("=" * 70)
    
    try:
        demo_info_completa()
        demo_login_con_google()
        demo_login_fallido()
        demo_multiples_usuarios()
        demo_usuario_existente()
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError en la demo: {e}")
        import traceback
        traceback.print_exc()
