"""
Demo del patron Gatekeeper con JWT

Muestra como:
1. Crear un cliente en la base de datos
2. Hacer login y obtener un JWT
3. Validar el JWT (sin consultar BD)
4. El JWT expira automaticamente
"""
import sys
import os

# Esto agrega la carpeta TFU_3 al path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patrones.gatekeeper import GestorGatekeeper, ErrorAutenticacion, ErrorAutorizacion
from persistencia.client_repo import ClienteRepo
from persistencia.db import get_conn


def limpiar_datos_demo():
    """Elimina datos de prueba anteriores"""
    print("\n--- Limpiando datos de prueba anteriores ---")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE email LIKE 'demo%@ejemplo.com'")
        conn.commit()
    print("Datos limpios")


def crear_usuarios_demo():
    """Crea usuarios de prueba en la base de datos"""
    print("\n--- Creando usuarios de prueba ---")
    repo = ClienteRepo()
    
    # Usuario normal
    try:
        usuario1 = repo.save({
            "name": "Usuario Demo",
            "email": "demo@ejemplo.com",
            "password": "password123"
        })
        print(f"Usuario creado: {usuario1['name']} ({usuario1['email']})")
        
        # Asignar rol de usuario
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("UPDATE clients SET rol = 'usuario' WHERE id = %s", (usuario1['id'],))
            conn.commit()
    except Exception as e:
        print(f"Error creando usuario: {e}")
    
    # Usuario admin
    try:
        usuario2 = repo.save({
            "name": "Admin Demo",
            "email": "demo_admin@ejemplo.com",
            "password": "admin123"
        })
        print(f"Admin creado: {usuario2['name']} ({usuario2['email']})")
        
        # Asignar rol de admin
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("UPDATE clients SET rol = 'admin' WHERE id = %s", (usuario2['id'],))
            conn.commit()
    except Exception as e:
        print(f"Error creando admin: {e}")


def demo_login_logout():
    """Demuestra el proceso de login con JWT"""
    print("\n\n=== DEMO: LOGIN CON JWT ===\n")
    
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    # Intentar login con credenciales incorrectas
    print("1. Intentando login con credenciales incorrectas...")
    try:
        gatekeeper.login("demo@ejemplo.com", "password_incorrecta")
    except ErrorAutenticacion as e:
        print(f"   Error esperado: {e}")
    
    # Login exitoso
    print("\n2. Login con credenciales correctas...")
    resultado = gatekeeper.login("demo@ejemplo.com", "password123")
    print(f"   Login exitoso!")
    print(f"   Usuario: {resultado['nombre']}")
    print(f"   Email: {resultado['email']}")
    print(f"   Rol: {resultado['rol']}")
    print(f"   Token JWT: {resultado['token'][:50]}...")
    
    token = resultado['token']
    
    # Validar token
    print("\n3. Validando JWT (sin consultar BD)...")
    info = gatekeeper.validar_token(token)
    print(f"   JWT valido para: {info['nombre']} ({info['rol']})")
    print(f"   El JWT contiene: usuario_id={info['usuario_id']}, email={info['email']}")
    
    # Estadisticas
    print("\n4. Info del sistema JWT...")
    stats = gatekeeper.obtener_estadisticas()
    print(f"   Tipo: {stats['tipo']}")
    print(f"   Expiracion: {stats['expiracion_horas']} horas")
    
    # Con JWT no hay logout real (el token expira automaticamente)
    print("\n5. Nota sobre logout con JWT...")
    print("   Con JWT no hay logout real. El token expira en 24 horas.")
    print("   Para logout inmediato necesitarias una lista negra de tokens.")


def demo_permisos():
    """Demuestra la validacion de permisos"""
    print("\n\n=== DEMO: VALIDACION DE PERMISOS ===\n")
    
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    # Login como usuario normal
    print("1. Login como usuario normal...")
    usuario = gatekeeper.login("demo@ejemplo.com", "password123")
    token_usuario = usuario['token']
    print(f"   Token obtenido para: {usuario['nombre']} (rol: {usuario['rol']})")
    
    # Login como admin
    print("\n2. Login como admin...")
    admin = gatekeeper.login("demo_admin@ejemplo.com", "admin123")
    token_admin = admin['token']
    print(f"   Token obtenido para: {admin['nombre']} (rol: {admin['rol']})")
    
    # Usuario normal intenta hacer una accion de admin
    print("\n3. Usuario normal intenta hacer accion de admin...")
    try:
        gatekeeper.validar_permiso(token_usuario, "admin")
    except ErrorAutorizacion as e:
        print(f"   Error esperado: {e}")
    
    # Admin hace una accion de admin
    print("\n4. Admin hace accion de admin...")
    info = gatekeeper.validar_permiso(token_admin, "admin")
    print(f"   Permiso concedido para: {info['nombre']}")
    
    # Limpiar
    gatekeeper.revocar_token(token_usuario)
    gatekeeper.revocar_token(token_admin)


def demo_tokens_multiples():
    """Demuestra que con JWT cada login genera un token independiente"""
    print("\n\n=== DEMO: MULTIPLES JWT SIMULTANEOS ===\n")
    
    gestor = GestorGatekeeper()
    gatekeeper = gestor.obtener_gatekeeper()
    
    # Crear multiples JWT para el mismo usuario
    print("1. Creando 3 JWT para el mismo usuario...")
    tokens = []
    for i in range(3):
        resultado = gatekeeper.login("demo@ejemplo.com", "password123")
        tokens.append(resultado['token'])
        print(f"   JWT {i+1} creado: {resultado['token'][:50]}...")
    
    # Todos los JWT son validos
    print("\n2. Todos los JWT son validos simultaneamente...")
    for i, token in enumerate(tokens):
        try:
            info = gatekeeper.validar_token(token)
            print(f"   JWT {i+1}: Valido para {info['nombre']}")
        except ErrorAutenticacion as e:
            print(f"   JWT {i+1}: {e}")
    
    print("\n3. Con JWT no hay limite de sesiones...")
    print("   Cada JWT es independiente y valido hasta que expire.")


if __name__ == "__main__":
    print("=" * 60)
    print("DEMO: PATRON GATEKEEPER CON JWT")
    print("=" * 60)
    
    try:
        # Preparar datos
        limpiar_datos_demo()
        crear_usuarios_demo()
        
        # Ejecutar demos
        demo_login_logout()
        demo_permisos()
        demo_tokens_multiples()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETADA")
        print("\n")
        print("NOTA: Con JWT no hay tokens guardados en memoria ni BD.")
        print("El token contiene toda la info del usuario y expira en 24h.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError en la demo: {e}")
        import traceback
        traceback.print_exc()
