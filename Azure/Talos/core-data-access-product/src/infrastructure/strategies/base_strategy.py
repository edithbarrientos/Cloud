"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Contrato Universal Multi-Engine con Operaciones CRUD (BaseDataStrategy)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseDataStrategy(ABC):
    
    @abstractmethod
    async def conectar(self) -> None:
        pass
    
    @abstractmethod
    async def crear_registro(self, llave_id: str, datos: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def consultar_registro(self, llave_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def actualizar_registro(self, llave_id: str, datos_nuevos: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def borrar_registro(self, llave_id: str) -> bool:
        pass
    
    @abstractmethod
    async def desconectar(self) -> None:
        pass
