from persistencia.client_repo import ClienteRepo
from patrones.circuit_breaker import GestorCircuitBreakers, CircuitBreakerError
from logica.payment_service import ServicioPagos, ErrorProcesamiento


class ClienteService:
    def __init__(self):
        self.repo = ClienteRepo()
        self.servicio_pagos = ServicioPagos(tasa_fallo=0.0, latencia_ms=100)
        
        # obtener el circuit breaker para proteger llamadas a pagos
        gestor = GestorCircuitBreakers()
        self.circuit_breaker_pagos = gestor.obtener_circuit_breaker("servicio_pagos")

    def registrarCliente(self, cliente_data):
        return self.repo.save(cliente_data)

    def loginCliente(self, email, password):
        return self.repo.login(email, password)

    def actualizarCliente(self, cliente_id, cliente_data):
        return self.repo.update(cliente_id, cliente_data)

    def obtenerCliente(self, cliente_id):
        return self.repo.findById(cliente_id)
    
    def realizar_pago(self, cliente_id, monto, metodo_pago="tarjeta"):
        """
        Procesa un pago usando el servicio de pagos, protegido por Circuit Breaker.
        
        El Circuit Breaker protege contra fallos repetidos:
        - Si el servicio falla muchas veces, el circuito se abre
        - Cuando esta abierto, las llamadas fallan inmediatamente
        - Despues de un tiempo, permite probar si el servicio se recupero
        
        Args:
            cliente_id: ID del cliente
            monto: Monto a cobrar
            metodo_pago: Forma de pago
            
        Returns:
            dict: Informacion del pago procesado
            
        Raises:
            CircuitBreakerError: Si el circuito esta abierto
            ErrorProcesamiento: Si el pago falla
        """
        print(f"\n[Cliente Service] Procesando pago de ${monto} para cliente {cliente_id}")
        
        try:
            # usamos el circuit breaker para proteger la llamada
            resultado = self.circuit_breaker_pagos.llamar(
                self.servicio_pagos.procesar_pago,
                cliente_id,
                monto,
                metodo_pago
            )
            
            print(f"[Cliente Service] Pago completado exitosamente")
            return {
                "exito": True,
                "mensaje": "Pago procesado correctamente",
                "datos": resultado
            }
            
        except CircuitBreakerError as error:
            # el circuito esta abierto por lo que el servicio no está disponible
            print(f"[Cliente Service] Pago rechazado - Circuit breaker abierto")
            return {
                "exito": False,
                "mensaje": "Servicio de pagos temporalmente no disponible. Intente mas tarde.",
                "error": str(error)
            }
            
        except ErrorProcesamiento as error:
            # falló el procesamiento del pago
            print(f"[Cliente Service] Error al procesar pago: {str(error)}")
            return {
                "exito": False,
                "mensaje": "Error al procesar el pago. Intente nuevamente.",
                "error": str(error)
            }
    
    def verificar_estado_pago(self, transaccion_id):
        """
        Verifica el estado de un pago, protegido por Circuit Breaker.
        
        Args:
            transaccion_id: ID de la transaccion a verificar
            
        Returns:
            dict: Estado del pago
        """
        try:
            resultado = self.circuit_breaker_pagos.llamar(
                self.servicio_pagos.verificar_pago,
                transaccion_id
            )
            
            return {
                "exito": True,
                "datos": resultado
            }
            
        except CircuitBreakerError as error:
            return {
                "exito": False,
                "mensaje": "No se puede verificar el pago en este momento",
                "error": str(error)
            }
            
        except ErrorProcesamiento as error:
            return {
                "exito": False,
                "mensaje": "Error al verificar el pago",
                "error": str(error)
            }
    
    def obtener_estadisticas_pagos(self):
        """Retorna estadisticas del servicio de pagos y del circuit breaker"""
        return {
            "servicio_pagos": self.servicio_pagos.obtener_estadisticas(),
            "circuit_breaker": self.circuit_breaker_pagos.obtener_estadisticas()
        }
    
    def simular_fallos_pagos(self, tasa_fallo):
        """
        Configura la tasa de fallo del servicio de pagos para pruebas.
        
        Args:
            tasa_fallo: Porcentaje de fallos (0.0 a 1.0)
                       0.0 = sin fallos
                       0.3 = 30% de fallos
                       0.5 = 50% de fallos
        """
        self.servicio_pagos.configurar_tasa_fallo(tasa_fallo)
        print(f"[Cliente Service] Servicio de pagos configurado con {tasa_fallo*100}% de fallos")