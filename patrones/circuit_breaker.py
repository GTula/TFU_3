"""
Patron Circuit Breaker - Proteccion contra fallos en cascada

Este patron previene que llamadas repetidas a un servicio fallido
sobrecarguen el sistema. Funciona como un interruptor electrico:
- CERRADO: Las llamadas pasan normalmente
- ABIERTO: Las llamadas fallan inmediatamente sin intentar
- SEMI_ABIERTO: Permite algunas llamadas de prueba
"""

import time
from enum import Enum

# estados posibles del circuit breaker
class EstadoCircuito(Enum):
    CERRADO = "CERRADO" # funcionamiento normal
    ABIERTO = "ABIERTO" # bloqueando llamadas
    SEMI_ABIERTO = "SEMI_ABIERTO" # permitiendo pruebas

# error lanzado cuando el circuito esta abierto
class CircuitBreakerError(Exception):
    pass


class CircuitBreaker:
    """
    Implementa el patron Circuit Breaker de forma simple.
    
    El circuito se abre cuando hay muchos fallos consecutivos,
    se mantiene abierto por un tiempo, y luego permite probar
    si el servicio se recupero.
    """
    
    def __init__(self, nombre, max_fallos=3, timeout_abierto=60, timeout_semi_abierto=30):
        """
        Args:
            nombre: Nombre descriptivo del circuit breaker
            max_fallos: Numero de fallos antes de abrir el circuito
            timeout_abierto: Segundos que el circuito permanece abierto
            timeout_semi_abierto: Segundos para probar en estado semi-abierto
        """
        self.nombre = nombre
        self.max_fallos = max_fallos
        self.timeout_abierto = timeout_abierto
        self.timeout_semi_abierto = timeout_semi_abierto
        
        # estado interno
        self.estado = EstadoCircuito.CERRADO
        self.contador_fallos = 0
        self.contador_exitos = 0
        self.tiempo_ultimo_fallo = None
        self.total_llamadas = 0
        self.total_exitos = 0
        self.total_fallos = 0
        
        print(f"[Circuit Breaker] '{nombre}' inicializado")
        print(f"  - Max fallos permitidos: {max_fallos}")
        print(f"  - Timeout abierto: {timeout_abierto}s")
    
    def llamar(self, funcion, *args, **kwargs):
        """
        Ejecuta una funcion protegida por el circuit breaker.
        
        Args:
            funcion: Funcion a ejecutar
            *args, **kwargs: Argumentos de la funcion
            
        Returns:
            Resultado de la funcion
            
        Raises:
            CircuitBreakerError: Si el circuito esta abierto
            Exception: Si la funcion falla
        """
        self.total_llamadas += 1

        # verificar si debemos cambiar de estado
        self._verificar_estado()
        
        # si el circuito esta abierto => rechazar inmediatamente
        if self.estado == EstadoCircuito.ABIERTO:
            self.total_fallos += 1
            print(f"[{self.nombre}] RECHAZADO - Circuito ABIERTO")
            raise CircuitBreakerError(
                f"Circuit breaker '{self.nombre}' esta ABIERTO. "
                f"Servicio temporalmente no disponible."
            )
        
        # intentar ejecutar la funcion
        try:
            print(f"[{self.nombre}] Ejecutando llamada (Estado: {self.estado.value})")
            resultado = funcion(*args, **kwargs)
            
            # la llamada fue exitosa
            self._registrar_exito()
            return resultado
            
        except Exception as error:
            # la llamada fallo
            self._registrar_fallo()
            raise error
    
    def _verificar_estado(self):
        """Verifica y actualiza el estado del circuito si es necesario"""
        
        if self.estado == EstadoCircuito.ABIERTO:
            # Verificar si ya paso el tiempo de timeout
            tiempo_transcurrido = time.time() - self.tiempo_ultimo_fallo
            
            if tiempo_transcurrido >= self.timeout_abierto:
                print(f"[{self.nombre}] Cambiando a SEMI_ABIERTO para probar recuperacion")
                self.estado = EstadoCircuito.SEMI_ABIERTO
                self.contador_exitos = 0
    
    def _registrar_exito(self):
        """Registra una llamada exitosa"""
        self.contador_exitos += 1
        self.contador_fallos = 0  # resetear contador de fallos
        self.total_exitos += 1
        
        print(f"[{self.nombre}] EXITO (exitos consecutivos: {self.contador_exitos})")
        
        # si estabamos en semi-abierto y tuvimos exito, cerrar el circuito
        if self.estado == EstadoCircuito.SEMI_ABIERTO:
            if self.contador_exitos >= 2:  # necesitamos al menos 2 exitos
                print(f"[{self.nombre}] Servicio recuperado - Cambiando a CERRADO")
                self.estado = EstadoCircuito.CERRADO
                self.contador_fallos = 0
    
    def _registrar_fallo(self):
        """Registra una llamada fallida"""
        self.contador_fallos += 1
        self.contador_exitos = 0  # resetear contador de exitos
        self.total_fallos += 1
        self.tiempo_ultimo_fallo = time.time()
        
        print(f"[{self.nombre}] FALLO (fallos consecutivos: {self.contador_fallos}/{self.max_fallos})")
        
        # si alcanzamos el maximo de fallos, abrir el circuito
        if self.contador_fallos >= self.max_fallos:
            print(f"[{self.nombre}] ABRIENDO CIRCUITO - Demasiados fallos")
            self.estado = EstadoCircuito.ABIERTO
    
    def obtener_estadisticas(self):
        """Retorna estadisticas del circuit breaker"""
        tasa_exito = 0
        if self.total_llamadas > 0:
            tasa_exito = (self.total_exitos / self.total_llamadas) * 100
        
        return {
            "nombre": self.nombre,
            "estado": self.estado.value,
            "total_llamadas": self.total_llamadas,
            "total_exitos": self.total_exitos,
            "total_fallos": self.total_fallos,
            "tasa_exito": round(tasa_exito, 2),
            "fallos_consecutivos": self.contador_fallos,
            "max_fallos_permitidos": self.max_fallos
        }
    
    def resetear(self):
        """Resetea el circuit breaker manualmente"""
        print(f"[{self.nombre}] Reseteando circuit breaker manualmente")
        self.estado = EstadoCircuito.CERRADO
        self.contador_fallos = 0
        self.contador_exitos = 0
        self.tiempo_ultimo_fallo = None


class GestorCircuitBreakers:
    """
    Gestor central para todos los circuit breakers del sistema.
    Patron Singleton para tener una unica instancia.
    """
    
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.circuit_breakers = {}
        return cls._instancia
    
    def crear_circuit_breaker(self, nombre, max_fallos=3, timeout_abierto=60, timeout_semi_abierto=30):
        """Crea y registra un nuevo circuit breaker"""
        if nombre not in self.circuit_breakers:
            cb = CircuitBreaker(nombre, max_fallos, timeout_abierto, timeout_semi_abierto)
            self.circuit_breakers[nombre] = cb
            print(f"[Gestor] Circuit breaker '{nombre}' registrado")
        return self.circuit_breakers[nombre]
    
    def obtener_circuit_breaker(self, nombre):
        """Obtiene un circuit breaker existente"""
        if nombre not in self.circuit_breakers:
            raise ValueError(f"Circuit breaker '{nombre}' no existe")
        return self.circuit_breakers[nombre]
    
    def obtener_todas_estadisticas(self):
        """Retorna estadisticas de todos los circuit breakers"""
        return {
            nombre: cb.obtener_estadisticas()
            for nombre, cb in self.circuit_breakers.items()
        }
    
    def resetear_todos(self):
        """Resetea todos los circuit breakers"""
        print("[Gestor] Reseteando todos los circuit breakers")
        for cb in self.circuit_breakers.values():
            cb.resetear()
