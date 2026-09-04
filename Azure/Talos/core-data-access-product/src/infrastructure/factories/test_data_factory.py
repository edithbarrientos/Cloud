"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Fábrica de Datos Sintéticos para Suites de Simulación (TestDataFactory)
Descripción: Patrón Data Factory centralizado. Provee funciones estáticas inmutables
             para emular las respuestas de las operaciones CRUD, aislando el runtime 
             de dependencias de infraestructura física durante las pruebas.
"""
from typing import Dict, Any, Optional

class TestDataFactory:

    @staticmethod
    def simular_respuesta_create(cliente_id: str, exito: bool = True) -> Dict[str, Any]:
        """[DATA FACTORY - CREATE]: Genera el log de confirmación sintética de inserción"""
        return {
            "clienteId": cliente_id,
            "operacion": "INSERT_OR_WRITE",
            "confirmado": exito,
            "metadataFabricacion": "MOCK_DATA_FACTORY_ENGINE"
        }

    @staticmethod
    def simular_respuesta_read(cliente_id: str, segmento: str = "VIP") -> Optional[Dict[str, Any]]:
        """[DATA FACTORY - READ]: Construye cargas útiles canónicas normalizadas en camelCase"""
        if cliente_id == "FAIL_ID":
            return None
        return {
            "clienteId": cliente_id,
            "segmentoCorporativo": segmento,
            "saldoGlobalConsolidado": 0.0 if segmento == "VIP" else 15450.25,
            "scoreRiesgoFinanciero": 0.99 if segmento == "VIP" else 0.82,
            "fuenteOrigenCertificada": "MOCK_DATA_FACTORY_ANALYTICS"
        }

    @staticmethod
    def simular_respuesta_update(cliente_id: str, exito: bool = True) -> Dict[str, Any]:
        """[DATA FACTORY - UPDATE]: Emula el estatus de un parche o mutación en la RAM"""
        return {
            "clienteId": cliente_id,
            "operacion": "UPDATE_OR_PATCH",
            "mutadoInmutable": exito,
            "lineajeRegistrado": "DATA_FACTORY_AUDIT_TRAIL"
        }

    @staticmethod
    def simular_respuesta_delete(cliente_id: str, exito: bool = True) -> Dict[str, Any]:
        """[DATA FACTORY - DELETE]: Emula el éxito de una purga física del almacenamiento"""
        return {
            "clienteId": cliente_id,
            "operacion": "DELETE_OR_PURGE",
            "registrosRemovidos": 1 if exito else 0,
            "politicaRetencionAplicada": "VOLATILE_CLEANUP_IMMEDIATE"
        }