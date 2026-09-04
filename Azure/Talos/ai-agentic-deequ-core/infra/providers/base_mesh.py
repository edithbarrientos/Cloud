# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class BaseMeshProvider(ABC):
    """
    🏗️ TEMPLATE METHOD PATTERN: CAPA BASE IAC MULTI-CLOUD
    Contrato abstracto inmutable para aislar el aprovisionamiento de las nubes (Nivel 5).
    """
    @abstractmethod
    def deploy_resources(self) -> dict:
        """Punto de entrada declarativo que debe implementar cada proveedor cloud."""
        pass
