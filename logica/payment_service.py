"""
Servicio de Pagos - Simula un sistema de procesamiento de pagos externo

Este servicio puede fallar aleatoriamente para demostrar el Circuit Breaker
"""

import time
import random

# error durante el procesamiento del pago
class ErrorProcesamiento(Exception):
    pass


class ServicioPagos:
    """
    Simula un servicio externo de procesamiento de pagos.
    Puede configurarse para fallar en ciertos escenarios.
    """
    
    def __init__(self, tasa_fallo=0.0, latencia_ms=100):
        """
        Args:
            tasa_fallo: Porcentaje de fallos (de 0 a 1)
            latencia_ms: Tiempo de respuesta simulado en milisegundos
        """
        self.tasa_fallo = tasa_fallo
        self.latencia_ms = latencia_ms
        self.pagos_procesados = 0
        self.pagos_fallidos = 0
        
        print(f"[Servicio Pagos] Inicializado")
        print(f"  - Tasa de fallo: {tasa_fallo*100}%")
        print(f"  - Latencia: {latencia_ms}ms")
    
    def procesar_pago(self, cliente_id, monto, metodo_pago="tarjeta"):
        """
        Procesa un pago de forma simulada.
        
        Args:
            cliente_id: ID del cliente que realiza el pago
            monto: Cantidad a cobrar
            metodo_pago: Tipo de pago (tarjeta, efectivo, etc)
            
        Returns:
            dict: Informacion del pago procesado
            
        Raises:
            ErrorProcesamiento: Si el pago falla
        """
        # simular latencia del servicio
        time.sleep(self.latencia_ms / 1000.0)

        # simular fallo aleatorio
        if random.random() < self.tasa_fallo:
            self.pagos_fallidos += 1
            print(f"[Servicio Pagos] ERROR - Fallo al procesar pago de ${monto}")
            raise ErrorProcesamiento(
                f"No se pudo procesar el pago. "
                f"Servicio de pagos temporalmente no disponible."
            )
        
        # pago exitoso
        self.pagos_procesados += 1
        transaccion_id = f"TXN-{int(time.time())}-{random.randint(1000, 9999)}"
        
        resultado = {
            "transaccion_id": transaccion_id,
            "cliente_id": cliente_id,
            "monto": monto,
            "metodo_pago": metodo_pago,
            "estado": "APROBADO",
            "timestamp": time.time()
        }
        
        print(f"[Servicio Pagos] EXITO - Pago aprobado: ${monto} (ID: {transaccion_id})")
        return resultado
    
    def verificar_pago(self, transaccion_id):
        """Verifica el estado de un pago"""
        # simulacion simple
        time.sleep(0.05)
        
        if random.random() < self.tasa_fallo:
            raise ErrorProcesamiento("No se pudo verificar el pago")
        
        return {
            "transaccion_id": transaccion_id,
            "estado": "COMPLETADO"
        }
    
    def obtener_estadisticas(self):
        """Retorna estadisticas del servicio"""
        total = self.pagos_procesados + self.pagos_fallidos
        tasa_exito = 0
        if total > 0:
            tasa_exito = (self.pagos_procesados / total) * 100
        
        return {
            "pagos_procesados": self.pagos_procesados,
            "pagos_fallidos": self.pagos_fallidos,
            "tasa_exito": round(tasa_exito, 2)
        }
    
    def configurar_tasa_fallo(self, nueva_tasa):
        """Cambia la tasa de fallo del servicio"""
        self.tasa_fallo = nueva_tasa
        print(f"[Servicio Pagos] Tasa de fallo actualizada a {nueva_tasa*100}%")
