"""
Módulo de Optimización Estocástica y Entrenamiento Supervisado Multi-Tenant.

Este componente expone las capacidades de Machine Learning core para la plataforma,
permitiendo el re-entrenamiento dinámico en caliente de Redes Neuronales Convolucionales (CNN)
especializadas en la clasificación estadística de intenciones lingüísticas corporativas.
El motor implementa el algoritmo de descenso de gradiente Adam con decaimiento estocástico,
mecanismos estrictos de gobernanza de datos via Sets, y una guardia algorítmica de 
Early Stopping para salvaguardar la resiliencia del clúster de producción.

Versión de Runtime Certificada: Python 3.12+
"""

import os
import random
import logging
import time
import json
from typing import List, Tuple, Dict, Any, Set, Final
import spacy
from spacy.training import Example
from spacy.language import Language
from spacy.pipeline.textcat import TextCategorizer
from pydantic import BaseModel, Field

# ==============================================================================
# 📺 CONFIGURACIÓN DEL ESTÁNDAR DE OBSERVABILIDAD DE MACHINE LEARNING (LOGS)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] AI-Trainer-Core: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger: logging.Logger = logging.getLogger("Model-Trainer")

# 📋 CATÁLOGO INMUTABLE CORPORATIVO DE INTENCIONES (DATOS DE GOBERNANZA - WHITELIST)
APPROVED_INTENT_CATALOG: Final[Set[str]] = {
    "BILLING_SUPPORT",
    "GREETING",
    "TECH_SUPPORT",
    "SALES_INQUIRY",
    "HUMAN_AGENT_REQUEST"
}


# ==============================================================================
# 📋 MODELOS DE VALIDACIÓN E INMUTABILIDAD DE DATOS (DATA TRANSFER OBJECTS)
# ==============================================================================
class TrainingRowDTO(BaseModel):
    """
    Data Transfer Object (DTO) que valida una fila de entrenamiento del Golden Dataset.
    """
    text: str = Field(..., description="Muestra textual en lenguaje natural plano enviada por el usuario en el chat.")
    categories: Dict[str, float] = Field(..., description="Diccionario de mapeo probabilístico hash O(1) con los pesos de las intenciones.")

    class Config:
        frozen = True


class TrainingPayloadDTO(BaseModel):
    """
    Data Transfer Object (DTO) maestro que orquesta los hiperparámetros del entrenamiento.
    """
    tenantId: str = Field(..., description="Identificador único del inquilino corporativo asociado al sub-modelo.")
    epochs: int = Field(15, ge=1, le=100, description="Límite máximo de iteraciones iterativas sobre el dataset completo.")
    targetLoss: float = Field(0.0001, gt=0.0, description="Umbral límite de la función de coste para disparar la parada temprana.")
    dataset: List[TrainingRowDTO] = Field(..., description="Arreglo con el lote de filas de entrenamiento supervisadas.")

    class Config:
        frozen = True


# ==============================================================================
# 🏋️ MOTOR DE OPTIMIZACIÓN VECTORIZADO (CORE ALGORITHMIC STAGE)
# ==============================================================================
def train_custom_tenant_model(payload: TrainingPayloadDTO) -> Dict[str, Any]:
    """
    Ejecuta el ciclo de optimización estocástica Adam sobre el grafo analítico de la CNN.
    """
    start_time: float = time.perf_counter()
    
    # 📐 1. CONTROL DE EXCEPCIONES Y SANIDAD SINTÁCTICA DEL PAYLOAD
    if not payload.dataset:
        logger.error("💥 [Trainer-Input-Error] El lote de datos 'dataset' del DTO está vacío.")
        raise ValueError("El dataset de entrenamiento provisto en el payload JSON no contiene registros.")

    # 🛡️ 2. AUDITORÍA INTEGRAL DE GOBERNANZA UTILIZANDO SUSTRACCIÓN DE CONJUNTOS (SET MATH)
    incoming_labels: Set[str] = {label for row in payload.dataset for label in row.categories.keys()}
    
    illegal_labels: Set[str] = incoming_labels - APPROVED_INTENT_CATALOG
    if illegal_labels:
        error_msg: str = (
            f"🚨 [Gobernanza-Catastrophic] Intenciones no autorizadas detectadas en el JSON: {illegal_labels}. "
            f"El catálogo institucional inmutable solo admite las firmas: {APPROVED_INTENT_CATALOG}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # 🪐 3. CONVERSIÓN MATRICIAL VECTORIZADA (ELIMINACIÓN DE HARDCODING)
    TRAINING_DATA: List[Tuple[str, Dict[str, Dict[str, float]]]] = [
        (row.text, {"cats": row.categories}) for row in payload.dataset
    ]

    try:
        # 📡 4. INICIALIZACIÓN DEL COMPONENTE TEXT-CATEGORIZER DENTRO DEL GRAFO (LOAD STAGE)
        nlp: Language = spacy.load("es_core_news_sm")
        
        textcat: TextCategorizer = nlp.add_pipe("textcat", last=True) if "textcat" not in nlp.pipe_names else nlp.get_pipe("textcat") # type: ignore
            
        for label in incoming_labels:
            textcat.add_label(label)
            logger.info(f"🏷️  [Model-Registry-Labels] Firma analítica registrada con éxito en la CNN: [{label}]")

        # 🛡️ 5. CONGELAMIENTO SINTÁCTICO DE COMPONENTES ADYACENTES (PIPELINE FREEZING)
        disabled_pipes: List[str] = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]
        final_loss: float = 1.0
        early_stopped: bool = False
        
        # Apertura del contexto aislado de tensores
        with nlp.select_pipes(disable=disabled_pipes):
            optimizer = nlp.initialize()
            logger.info(f"🚀 [Network-Engine-Ready] Matrices inicializadas. Pipes congelados: {disabled_pipes}")
            logger.info(f"🏋️  [Training-Loop-Start] Optimizador Adam acoplado. Límite máximo: [{payload.epochs}] Épocas.")
            
            # 📈 6. LOOP DE OPTIMIZACIÓN VECTORIZADO (EPOCH CONVERGENCE)
            for epoch in range(payload.epochs):
                random.shuffle(TRAINING_DATA)
                losses: Dict[str, float] = {}
                batches = spacy.util.minibatch(TRAINING_DATA, size=3)
                
                for batch in batches:
                    examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in batch]
                    nlp.update(examples, sgd=optimizer, losses=losses)
                
                final_loss = losses.get("textcat", 1.0)
                logger.info(f"📉 Epoch {epoch + 1:02d}/{payload.epochs:02d} -> Pérdida Matemática (Loss): [{final_loss:.6f}]")
                
                # GUARDIA ALGOCRIÍTICA DE DETENCIÓN TEMPRANA (EARLY STOPPING)
                if final_loss <= payload.targetLoss:
                    logger.warning(
                        f"🎯 [Early-Stopping-Triggered] Convergencia matemática alcanzada en la Época {epoch + 1}. "
                        f"Error óptimo de la función de coste: [{final_loss:.6f}]."
                    )
                    early_stopped = True
                    break

        # 💾 7. MÓDULO DE PERSISTENCIA INMUTABLE EN DISCO (MODEL REGISTRY SINK)
        output_dir: str = f"./models_store/{payload.tenantId}"
        os.makedirs(output_dir, exist_ok=True)
        nlp.to_disk(output_dir)
        
        duration_sec: float = time.perf_counter() - start_time
        logger.info(f"💾 [Trainer-Success] Sub-modelo entrenado guardado con éxito en la ruta física: [{output_dir}]")

        return {
            "status": "SUCCESS",
            "tenant_id": payload.tenantId,
            "metrics": {
                "epochs_executed": epoch + 1,
                "early_stopping_triggered": early_stopped,
                "final_loss": round(final_loss, 6),
                "training_duration_seconds": round(duration_sec, 2)
            },
            "infrastructure": {
                "model_persisted_path": output_dir,
                "concurrency_mode": "Vectorized_Minibatch_Cython"
            }
        }

    except Exception as ex:
        logger.error(f"🚨 [Trainer-System-Failure] Colapso catastrófico en los hilos del optimizador Adam: {str(ex)}", exc_info=True)
        raise RuntimeError(f"Fallo crítico en ejecución interna de tensores ML: {str(ex)}")


# ==============================================================================
# 🪐 CONTROLADOR DE PRUEBA LOCAL (DRIVER CODE)
# ==============================================================================
if __name__ == "__main__":
    sample_raw_input = {
        "tenantId": "tenant_generic",
        "epochs": 15,
        "targetLoss": 0.0001,
        "dataset": [
            {
                "text": "Tengo un problema urgente, el sistema arroja un error critico y pesimo en mi pasarela de cobro.",
                "categories": {"BILLING_SUPPORT": 1.0, "GREETING": 0.0, "TECH_SUPPORT": 0.0}
            },
            {
                "text": "No se proceso mi pago de la suscripción mensual y me sale fallo de tarjeta.",
                "categories": {"BILLING_SUPPORT": 1.0, "GREETING": 0.0, "TECH_SUPPORT": 0.0}
            },
            {
                "text": "Hola buenas tardes, espero que se encuentren muy bien hoy.",
                "categories": {"BILLING_SUPPORT": 0.0, "GREETING": 1.0, "TECH_SUPPORT": 0.0}
            },
            {
                "text": "La API me esta arrojando un codigo de error 500 y no conecta al servidor.",
                "categories": {"BILLING_SUPPORT": 0.0, "GREETING": 0.0, "TECH_SUPPORT": 1.0}
            }
        ]
    }

    # 🚀 REEMPLAZO LOG: Mutamos los antiguos "print" por trazas formales del motor de observabilidad
    logger.info("🪐 [Enterprise-Test] Inicializando simulación de carga e inyección DTO...")
    validated_payload = TrainingPayloadDTO(**sample_raw_input)
    telemetry_report = train_custom_tenant_model(validated_payload)
    
    logger.info("📈 [Telemetría Recibida] Despachando reporte de auditoría en formato JSON estructurado:")
    logger.info(json.dumps(telemetry_report, indent=4, ensure_ascii=False))