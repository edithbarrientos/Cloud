from abc import ABC, abstractmethod

class AbstractModelRepository(ABC):
    """
    📜 CONTRATO COMPARTIDO DE OBJECT STORAGE (MLOPS LAYER)
    Interfaz abstracta para la persistencia del estado del modelo de ML en multi-nube.
    """
    @abstractmethod
    async def load_model_binary(self, remote_path: str) -> bytes:
        """Descarga el cerebro del modelo desde el Object Storage de la nube en milisegundos."""
        pass

    @abstractmethod
    async def save_model_binary(self, remote_path: str, data: bytes) -> bool:
        """Sube y congela de forma asíncrona la nueva matriz de pesos de ML en el Object Storage."""
        pass
