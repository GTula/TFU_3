"""
Demostracion del Patron Circuit Breaker

Este script muestra como el Circuit Breaker protege contra llamadas
repetidas a un servicio que esta fallando.
"""
import sys
import os

# Esto agrega la carpeta TFU_3 al path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from patrones.circuit_breaker import GestorCircuitBreakers, CircuitBreakerError, EstadoCircuito
from logica.payment_service import ServicioPagos, ErrorProcesamiento


def demo_1_funcionamiento_normal():
    """Demo 1: Circuit Breaker con servicio funcionando normalmente"""
    print("\n" + "="*70)
    print("DEMO 1: Servicio funcionando normalmente")
    print("="*70 + "\n")
    
    # Crear servicio de pagos sin fallos
    servicio = ServicioPagos(tasa_fallo=0.0, latencia_ms=100)
    
    # Crear circuit breaker
    gestor = GestorCircuitBreakers()
    cb = gestor.crear_circuit_breaker("demo1", max_fallos=3, timeout_abierto=10)
    
    print("Realizando 5 pagos exitosos...\n")
    
    for i in range(5):
        try:
            resultado = cb.llamar(servicio.procesar_pago, cliente_id=1, monto=100.0)
            print(f"  Pago {i+1}: EXITO - {resultado['transaccion_id']}\n")
        except Exception as e:
            print(f"  Pago {i+1}: ERROR - {str(e)}\n")
        
        time.sleep(0.5)
    
    stats = cb.obtener_estadisticas()
    print("\nEstadisticas finales:")
    print(f"  Estado: {stats['estado']}")
    print(f"  Total llamadas: {stats['total_llamadas']}")
    print(f"  Exitos: {stats['total_exitos']}")
    print(f"  Fallos: {stats['total_fallos']}")
    print(f"  Tasa de exito: {stats['tasa_exito']}%")


def demo_2_servicio_fallando():
    """Demo 2: Circuit Breaker abriendo por fallos consecutivos"""
    print("\n" + "="*70)
    print("DEMO 2: Servicio fallando - Circuit Breaker se abre")
    print("="*70 + "\n")
    
    # Crear servicio con 100% de fallos
    servicio = ServicioPagos(tasa_fallo=1.0, latencia_ms=100)
    
    # Crear circuit breaker
    gestor = GestorCircuitBreakers()
    cb = gestor.crear_circuit_breaker("demo2", max_fallos=3, timeout_abierto=10)
    
    print("Intentando procesar pagos con servicio fallido...\n")
    
    for i in range(6):
        try:
            resultado = cb.llamar(servicio.procesar_pago, cliente_id=1, monto=100.0)
            print(f"  Intento {i+1}: EXITO\n")
        except CircuitBreakerError as e:
            print(f"  Intento {i+1}: RECHAZADO - {str(e)}\n")
        except ErrorProcesamiento as e:
            print(f"  Intento {i+1}: FALLO - {str(e)}\n")
        
        time.sleep(0.5)
    
    stats = cb.obtener_estadisticas()
    print("\nEstadisticas finales:")
    print(f"  Estado: {stats['estado']}")
    print(f"  Fallos consecutivos: {stats['fallos_consecutivos']}/{stats['max_fallos_permitidos']}")
    print(f"  Total llamadas: {stats['total_llamadas']}")
    print(f"  Total fallos: {stats['total_fallos']}")


def demo_3_recuperacion():
    """Demo 3: Circuit Breaker recuperandose cuando el servicio mejora"""
    print("\n" + "="*70)
    print("DEMO 3: Recuperacion del servicio")
    print("="*70 + "\n")
    
    # Crear servicio que falla al principio
    servicio = ServicioPagos(tasa_fallo=1.0, latencia_ms=100)
    
    # Crear circuit breaker con timeouts cortos para la demo
    gestor = GestorCircuitBreakers()
    cb = gestor.crear_circuit_breaker("demo3", max_fallos=3, timeout_abierto=5)
    
    print("Fase 1: Servicio fallando - Circuit breaker se abrira\n")
    
    # Generar fallos para abrir el circuito
    for i in range(4):
        try:
            cb.llamar(servicio.procesar_pago, cliente_id=1, monto=100.0)
        except:
            pass
        time.sleep(0.3)
    
    stats = cb.obtener_estadisticas()
    print(f"\nEstado del circuito: {stats['estado']}")
    
    print("\nFase 2: Esperando timeout (5 segundos)...")
    time.sleep(6)
    
    print("\nFase 3: Arreglando el servicio y probando recuperacion\n")
    servicio.configurar_tasa_fallo(0.0)  # Arreglar el servicio
    
    # Intentar algunas llamadas
    for i in range(3):
        try:
            resultado = cb.llamar(servicio.procesar_pago, cliente_id=1, monto=100.0)
            print(f"  Intento {i+1}: EXITO - {resultado['transaccion_id']}\n")
        except CircuitBreakerError as e:
            print(f"  Intento {i+1}: RECHAZADO (circuito aun abierto)\n")
        except Exception as e:
            print(f"  Intento {i+1}: ERROR - {str(e)}\n")
        time.sleep(0.5)
    
    stats = cb.obtener_estadisticas()
    print("\nEstado final del circuito:")
    print(f"  Estado: {stats['estado']}")
    print(f"  Total exitos: {stats['total_exitos']}")
    print(f"  Total fallos: {stats['total_fallos']}")


def demo_4_estadisticas_multiples():
    """Demo 4: Monitoreando multiples circuit breakers"""
    print("\n" + "="*70)
    print("DEMO 4: Multiples Circuit Breakers")
    print("="*70 + "\n")
    
    gestor = GestorCircuitBreakers()
    
    # Crear varios circuit breakers
    cb_pagos = gestor.crear_circuit_breaker("pagos", max_fallos=3, timeout_abierto=10)
    cb_notificaciones = gestor.crear_circuit_breaker("notificaciones", max_fallos=5, timeout_abierto=15)
    cb_inventario = gestor.crear_circuit_breaker("inventario", max_fallos=2, timeout_abierto=20)
    
    print("\nCircuit breakers creados:")
    print("  - pagos")
    print("  - notificaciones")
    print("  - inventario")
    
    # Simular algunas llamadas
    servicio_ok = ServicioPagos(tasa_fallo=0.0, latencia_ms=50)
    servicio_malo = ServicioPagos(tasa_fallo=1.0, latencia_ms=50)
    
    print("\nSimulando uso de los servicios...\n")
    
    # Pagos: mayormente exitoso
    for i in range(5):
        try:
            cb_pagos.llamar(servicio_ok.procesar_pago, 1, 100.0)
        except:
            pass
    
    # Notificaciones: algunos fallos
    for i in range(7):
        try:
            servicio = servicio_ok if i % 3 != 0 else servicio_malo
            cb_notificaciones.llamar(servicio.procesar_pago, 1, 100.0)
        except:
            pass
    
    # Inventario: fallando mucho
    for i in range(4):
        try:
            cb_inventario.llamar(servicio_malo.procesar_pago, 1, 100.0)
        except:
            pass
    
    # Mostrar estadisticas de todos
    print("\n--- ESTADISTICAS DE TODOS LOS CIRCUIT BREAKERS ---\n")
    todas_stats = gestor.obtener_todas_estadisticas()
    
    for nombre, stats in todas_stats.items():
        print(f"{nombre.upper()}:")
        print(f"  Estado: {stats['estado']}")
        print(f"  Total llamadas: {stats['total_llamadas']}")
        print(f"  Tasa de exito: {stats['tasa_exito']}%")
        print(f"  Fallos consecutivos: {stats['fallos_consecutivos']}/{stats['max_fallos_permitidos']}")
        print()


def main():
    """Ejecutar todas las demos"""
    print("\n" + "="*70)
    print(" DEMOSTRACION DEL PATRON CIRCUIT BREAKER")
    print("="*70)
    
    try:
        demo_1_funcionamiento_normal()
        time.sleep(2)
        
        demo_2_servicio_fallando()
        time.sleep(2)
        
        demo_3_recuperacion()
        time.sleep(2)
        
        demo_4_estadisticas_multiples()
        
        print("\n" + "="*70)
        print(" DEMOS COMPLETADAS")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError en demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
