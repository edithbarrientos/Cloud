# -*- coding: utf-8 -*-
"""
Autor: EdithBG
Capa de Dominio: Algoritmia Polimórfica de Modelado de Tráfico
"""

from abc import ABC, abstractmethod


class LoadInjectionStrategy(ABC):
    """Contrato abstracto para la conmutación de rampas de inyección elástica."""
    @abstractmethod
    def calcular_parametros_carga(self, usuarios_max: int) -> tuple[int, int]:
        """Retorna de forma determinista la tupla estructurada (usuarios_totales, spawn_rate)."""
        pass

class StandardStressStrategy(LoadInjectionStrategy):
    """Carga Progresiva Balanceada: Evalúa la capacidad habitual del sistema (Carga y Rendimiento)."""
    def calcular_parametros_carga(self, usuarios_max: int) -> tuple[int, int]:
        # Incremento paulatino: Aceleración fijada al 10% del volumen total solicitado
        spawn_rate = max(1, int(usuarios_max * 0.10))
        return usuarios_max, spawn_rate

class TrafficSpikeStrategy(LoadInjectionStrategy):
    """Picos Súbitos Masivos: Evalúa la resiliencia y velocidad de apertura del Circuit Breaker (Estrés)."""
    def calcular_parametros_carga(self, usuarios_max: int) -> tuple[int, int]:
        # Inyección instantánea: Todos los hilos atacan el socket al mismo segundo
        return usuarios_max, usuarios_max

class ContinuousSoakStrategy(LoadInjectionStrategy):
    """Pruebas de Remanencia (Soak): Evalúa fugas de memoria y estabilidad a largo plazo (Fiabilidad)."""
    def calcular_parametros_carga(self, usuarios_max: int) -> tuple[int, int]:
        # Rampa amortiguada: Opera a la mitad de la capacidad máxima con una tasa mínima de entrada
        return int(usuarios_max * 0.50), 2

class StrategyContext:
    """Contexto operacional encargado de resolver las estrategias inyectadas en caliente."""
    _strategies = {
        "stress": StandardStressStrategy(),
        "spike": TrafficSpikeStrategy(),
        "soak": ContinuousSoakStrategy()
    }

    @classmethod
    def resolver_carga(cls, tipo: str, usuarios_max: int) -> tuple[int, int]:
        """Enruta dinámicamente el algoritmo correspondiente según la metadata de ingesta."""
        estrategia = cls._strategies.get(tipo.lower(), StandardStressStrategy())
        return estrategia.calcular_parametros_carga(usuarios_max)
