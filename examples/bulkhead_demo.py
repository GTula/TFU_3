"""
Ejemplo de Prueba del Patrón Bulkhead

Este script muestra cómo bulkhead aísla los servicios
y previene que un servicio sobrecargado afecte a otros.
"""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from patrones.bulkhead import BulkheadManager

def simular_operacion_lenta(nombre: str, duracion: float):
    """Simula una operación que tarda cierto tiempo"""
    print(f"[{nombre}] Iniciando operación (durará {duracion:.1f}s)")
    time.sleep(duracion)
    print(f"[{nombre}] Operación completada")
    return f"Resultado de {nombre}"


def simular_operacion_fallida(nombre: str):
    """Simula una operación que falla"""
    print(f"[{nombre}] Iniciando operación que fallará...")
    time.sleep(1)
    raise Exception(f"Error simulado en {nombre}")


def demo_basica():
    """
    Demostración de cómo se limita con bulkhead
    """
    print("\n" + "="*70)
    print("DEMO 1: Bulkhead Básico - Limitación de Concurrencia")
    print("="*70)
    
    manager = BulkheadManager()
    bulkhead = manager.create_bulkhead("demo", max_workers=2, timeout=5)
    
    print(f"\nBulkhead creado con máximo 2 workers")
    print("Intentando ejecutar 5 tareas simultáneas...\n")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(5):
            future = executor.submit(
                bulkhead.execute,
                simular_operacion_lenta,
                f"Tarea-{i+1}",
                2.0
            )
            futures.append(future)
        
        # Esperar a que todas terminen
        for i, future in enumerate(futures):
            try:
                result = future.result()
                print(f"✓ Tarea {i+1} completada: {result}")
            except Exception as e:
                print(f"✗ Tarea {i+1} falló: {str(e)}")
    
    stats = bulkhead.get_stats()
    print(f"\nEstadísticas finales:")
    print(f"  Total de requests: {stats['total_requests']}")
    print(f"  Requests exitosos: {stats['total_requests'] - stats['rejected_requests']}")
    print(f"  Tasa de éxito: {stats['success_rate']:.1f}%")
    
    bulkhead.shutdown()


def demo_timeout():
    """
    Demostración de timeout, básicamente cómo se previene
    operaciones que tardan demasiado
    """
    print("\n" + "="*70)
    print("DEMO 2: Protección de Timeout")
    print("="*70)
    
    manager = BulkheadManager()
    bulkhead = manager.create_bulkhead("demo_timeout", max_workers=3, timeout=3)
    
    print(f"\nBulkhead con timeout de 3 segundos")
    print("Ejecutando operaciones de diferentes duraciones...\n")
    
    tareas = [
        ("Rápida", 1.0), # debería completarse
        ("Media", 2.5), # debería completarse
        ("Lenta", 5.0), # debería fallar por timeout
        ("Muy-Lenta", 10.0), # debería fallar por timeout
    ]
    
    for nombre, duracion in tareas:
        try:
            result = bulkhead.execute(simular_operacion_lenta, nombre, duracion)
            print(f"✓ {nombre}: Completada exitosamente")
        except FuturesTimeoutError:
            print(f"✗ {nombre}: TIMEOUT - Operación cancelada")
        except Exception as e:
            print(f"✗ {nombre}: Error - {str(e)}")
    
    stats = bulkhead.get_stats()
    print(f"\nEstadísticas:")
    print(f"  Total: {stats['total_requests']}, "
          f"Exitosos: {stats['total_requests'] - stats['rejected_requests']}, "
          f"Rechazados: {stats['rejected_requests']}")
    
    bulkhead.shutdown()


def demo_aislamiento():
    """
    Demostración de aislamiento: muestra cómo diferentes
    bulkheads aislan los servicios entre sí
    """
    print("\n" + "="*70)
    print("DEMO 3: Aislamiento entre Servicios")
    print("="*70)
    
    manager = BulkheadManager()
    
    # Crear bulkheads separados para diferentes servicios
    productos_bh = manager.create_bulkhead("productos", max_workers=3, timeout=10)
    clientes_bh = manager.create_bulkhead("clientes", max_workers=3, timeout=10)
    
    print("\nSimulando: Servicio de PRODUCTOS sobrecargado")
    print("            Servicio de CLIENTES funcionando normalmente\n")
    
    # Sobrecargar el servicio de productos con operaciones lentas
    with ThreadPoolExecutor(max_workers=6) as executor:
        # 5 tareas lentas en productos (sobrecarga)
        productos_futures = []
        for i in range(5):
            future = executor.submit(
                productos_bh.execute,
                simular_operacion_lenta,
                f"Producto-{i+1}",
                3.0
            )
            productos_futures.append(future)
        
        time.sleep(0.5)  # Pequeña pausa
        
        # Mientras tanto, clientes sigue funcionando normal
        clientes_futures = []
        for i in range(3):
            future = executor.submit(
                clientes_bh.execute,
                simular_operacion_lenta,
                f"Cliente-{i+1}",
                1.0
            )
            clientes_futures.append(future)
        
        # Esperar resultados de clientes
        print("Esperando resultados de CLIENTES...")
        for i, future in enumerate(clientes_futures):
            try:
                future.result()
                print(f"  ✓ Cliente-{i+1} completado")
            except Exception as e:
                print(f"  ✗ Cliente-{i+1} falló: {str(e)}")
        
        print("\nCLIENTES completado - aún cuando PRODUCTOS está sobrecargado!")
        print("\nEsperando que PRODUCTOS termine...")
        
        for future in productos_futures:
            try:
                future.result()
            except:
                pass
    
    print("\n--- Estadísticas Finales ---")
    all_stats = manager.get_all_stats()
    for service_name, stats in all_stats.items():
        print(f"\n{service_name.upper()}:")
        print(f"  Requests totales: {stats['total_requests']}")
        print(f"  Tasa de éxito: {stats['success_rate']:.1f}%")
        print(f"  Workers activos: {stats['active_tasks']}/{stats['max_workers']}")
    
    manager.shutdown_all()

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" DEMOSTRACIÓN DEL PATRÓN BULKHEAD")
    print("="*70)

    demo_basica()        
    demo_timeout()
    demo_aislamiento()
    
    print("\n" + "="*70)
    print(" DEMOS COMPLETADAS")
    print("="*70 + "\n")
