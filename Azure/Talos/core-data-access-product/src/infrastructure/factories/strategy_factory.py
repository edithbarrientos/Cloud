"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Fábrica Temática de Enrutamiento Elástico Desacoplado (StrategyFactory)
"""
from src.infrastructure.strategies.base_strategy import BaseDataStrategy

class StrategyFactory:
    
    @staticmethod
    def obtener_estrategia_activa(engine_name: str) -> BaseDataStrategy:
        """
        Matriz de enrutamiento elástico corporativo. Instancia dinámicamente
        el adaptador físico mediante rutas absolutas estrictas de FastAPI.
        """
        target = engine_name.strip().lower()
        
        if target == "postgres":
            from src.infrastructure.strategies.relational.postgres_strategy import PostgresStrategy
            return PostgresStrategy()
            
        elif target == "snowflake":
            from src.infrastructure.strategies.analytical.snowflake_strategy import SnowflakeStrategy
            return SnowflakeStrategy()
            
        elif target == "aws_s3":
            from src.infrastructure.strategies.object_storage.aws_s3_strategy import AwsS3Strategy
            return AwsS3Strategy()
            
        elif target == "azure_blob":
            from src.infrastructure.strategies.object_storage.azure_blob_strategy import AzureBlobStrategy
            return AzureBlobStrategy()
            
        else:
            raise ValueError(f"[CORE_FACTORY_ERROR]: El motor o repositorio '{engine_name}' no está registrado.")