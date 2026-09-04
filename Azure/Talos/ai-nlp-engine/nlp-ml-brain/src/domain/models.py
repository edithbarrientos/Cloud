from pydantic import BaseModel, Field, field_validator, AfterValidator
from typing import List, Optional
from typing_extensions import Annotated

def clean_string_identifier(v: str) -> str:
    """Sanea de forma estricta los IDs de negocio removiendo espacios residuales."""
    return v.strip()

# Alias tipados fuertemente protegidos
SanitizedID = Annotated[str, AfterValidator(clean_string_identifier)]

class ExtractedEntity(BaseModel):
    """
    🧬 MODELO DE ENTIDAD EXTRACÍDA (NER)
    Representa un token crítico detectado en el texto por el algoritmo CRF de spaCy.
    """
    entity_type: str = Field(..., description="Categoría de la entidad (ej. CARD_NUMBER, ACCOUNT_ID)")
    value: str = Field(..., description="Texto explícito extraído de la conversación")

    model_config = {"frozen": True}


class AIAnalyticsResult(BaseModel):
    """
    🧬 MODELO CORE DE METADATOS DE INTELIGENCIA ARTIFICIAL
    Encapsula el dictamen probabilístico unificado calculado por los pipelines de NLP.
    """
    intent: str = Field(..., description="Categoría de intención asignada por el clasificador")
    
    # 🧮 Restricción de Probabilidad: Rango cerrado de 0.0 a 1.0 (Confianza)
    intent_confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Nivel de certeza probabilística del Intent (0.0 a 1.0)"
    )
    
    # 🧮 Restricción de Sentimiento: Rango cerrado continuo de -1.0 (Negativo) a +1.0 (Positivo)
    sentiment_score: float = Field(
        ..., 
        ge=-1.0, 
        le=1.0, 
        description="Polaridad continua del texto calculada por VADER (-1.0 a +1.0)"
    )
    
    entities: List[ExtractedEntity] = Field(
        default_factory=list, 
        description="Lista de entidades extraídas del chat"
    )

    model_config = {"frozen": True}


class InferenceResponse(BaseModel):
    """
    🧬 CONTRATO DE SALIDA ENRIQUECIDA (RESPUESTA HACIA FLINK)
    Define la estructura JSON final que el hilo asíncrono de Flink recibirá 
    de regreso tras completarse la inferencia multicliente no bloqueante.
    """
    status: str = Field(..., description="Estado de la inferencia (SUCCESS / ERROR)")
    tenant_id: SanitizedID = Field(..., description="Identificador único saneado de la cuenta matriz del inquilino")
    client_id: SanitizedID = Field(..., description="Identificador único saneado de la sub-cuenta o cliente específico")
    session_id: SanitizedID = Field(..., description="Código correlativo saneado de la sesión activa del chat")
    analytics: Optional[AIAnalyticsResult] = Field(None, description="Metadatos analíticos calculados de la IA")
    reason: Optional[str] = Field(None, description="Mensaje explicativo detallado en caso de fallos o excepciones")

    model_config = {"frozen": True}
