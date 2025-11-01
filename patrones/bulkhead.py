"""
Patrón Bulkhead - Aislamiento de recursos mediante thread pools

Este patrón previene que un servicio que falle o se sobrecargue afecte a otros servicios
mediante el aislamiento de recursos (thread pools separados).
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Any
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Bulkhead:
    """
    Implementa el patrón Bulkhead usando thread pools separados para aislar recursos.
    
    Cada servicio tiene su propio pool de threads, limitando el impacto de un servicio
    sobrecargado o fallido en otros servicios.
    """
    
    def __init__(self, name: str, max_workers: int = 5, timeout: int = 30):
        """
        Args:
            name: Nombre del bulkhead (ej: "productos", "clientes")
            max_workers: Número máximo de threads concurrentes permitidos
            timeout: Tiempo máximo de espera en segundos para una operación
        """
        self.name = name
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"bulkhead-{name}-"
        )
        self.active_tasks = 0
        self.total_requests = 0
        self.rejected_requests = 0
        
        logger.info(
            f"Bulkhead '{name}' creado con {max_workers} workers y timeout de {timeout}s"
        )
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función en el thread pool del bulkhead.
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la función
            
        Raises:
            BulkheadFullException: Si el bulkhead está lleno
            TimeoutError: Si la operación excede el timeout
        """
        self.total_requests += 1
        
        try:
            self.active_tasks += 1
            logger.info(
                f"[{self.name}] Ejecutando tarea. Activas: {self.active_tasks}/{self.max_workers}"
            )
            
            future = self.executor.submit(func, *args, **kwargs)
            result = future.result(timeout=self.timeout)
            
            logger.info(f"[{self.name}] Tarea completada exitosamente")
            return result
            
        except TimeoutError:
            self.rejected_requests += 1
            logger.error(
                f"[{self.name}] Timeout después de {self.timeout}s. "
                f"Rechazadas: {self.rejected_requests}/{self.total_requests}"
            )
            raise TimeoutError(
                f"La operación en '{self.name}' excedió el timeout de {self.timeout}s"
            )
            
        except Exception as e:
            self.rejected_requests += 1
            logger.error(f"[{self.name}] Error en ejecución: {str(e)}")
            raise
            
        finally:
            self.active_tasks -= 1
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del bulkhead"""
        return {
            "name": self.name,
            "max_workers": self.max_workers,
            "active_tasks": self.active_tasks,
            "total_requests": self.total_requests,
            "rejected_requests": self.rejected_requests,
            "success_rate": (
                ((self.total_requests - self.rejected_requests) / self.total_requests * 100)
                if self.total_requests > 0 else 100.0
            )
        }
    
    def shutdown(self, wait: bool = True):
        """Cierra el thread pool del bulkhead"""
        logger.info(f"Cerrando bulkhead '{self.name}'")
        self.executor.shutdown(wait=wait)


class BulkheadManager:
    """
    Gestor central de todos los bulkheads del sistema.
    Permite crear y acceder a bulkheads por nombre.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.bulkheads = {}
        return cls._instance
    
    def create_bulkhead(self, name: str, max_workers: int = 5, timeout: int = 30) -> Bulkhead:
        """Crea un nuevo bulkhead si no existe"""
        if name not in self.bulkheads:
            self.bulkheads[name] = Bulkhead(name, max_workers, timeout)
            logger.info(f"Bulkhead '{name}' registrado en el gestor")
        return self.bulkheads[name]
    
    def get_bulkhead(self, name: str) -> Bulkhead:
        """Obtiene un bulkhead existente"""
        if name not in self.bulkheads:
            raise ValueError(f"Bulkhead '{name}' no existe. Créalo primero.")
        return self.bulkheads[name]
    
    def get_all_stats(self) -> dict:
        """Retorna estadísticas de todos los bulkheads"""
        return {
            name: bulkhead.get_stats() 
            for name, bulkhead in self.bulkheads.items()
        }
    
    def shutdown_all(self):
        """Cierra todos los bulkheads"""
        for bulkhead in self.bulkheads.values():
            bulkhead.shutdown()


def bulkhead_protected(bulkhead_name: str):
    """
    Decorador para proteger funciones con un bulkhead.
    
    Uso:
        @bulkhead_protected("productos")
        def obtener_producto(id):
            # ... código ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = BulkheadManager()
            bulkhead = manager.get_bulkhead(bulkhead_name)
            return bulkhead.execute(func, *args, **kwargs)
        return wrapper
    return decorator
