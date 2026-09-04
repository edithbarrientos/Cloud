import os
import logging
from typing import Dict
from infrastructure.abstract_model_repository import AbstractModelRepository
from infrastructure.azure_blob_repository import AzureBlobRepository
from infrastructure.aws_s3_repository import AwsS3Repository
from infrastructure.gcp_gcs_repository import GcpGcsRepository

logger = logging.getLogger("ai_agentic_core.infrastructure")

class ModelRepositoryFactory:
    """🏭 FACTORÍA DE OBJECT STORAGE (MLES_STORE_REGISTRY)"""
    _cached_repos: Dict[str, AbstractModelRepository] = {}

    @staticmethod
    def get_model_repository() -> AbstractModelRepository:
        provider_env = os.getenv("ACTIVE_CLOUD_PROVIDER", "azure").lower().strip()
        
        if provider_env not in ModelRepositoryFactory._cached_repos:
            if provider_env in ["azure", "local"]:
                logger.info("[FACTORY_ML] 🪄 Inyectando: AzureBlobRepository (ADLS Gen2)")
                ModelRepositoryFactory._cached_repos[provider_env] = AzureBlobRepository()
            elif provider_env == "aws":
                logger.info("[FACTORY_ML] 🪄 Inyectando: AwsS3Repository (Amazon S3)")
                ModelRepositoryFactory._cached_repos[provider_env] = AwsS3Repository()
            elif provider_env == "gcp":
                logger.info("[FACTORY_ML] 🪄 Inyectando: GcpGcsRepository (Google Cloud Storage)")
                ModelRepositoryFactory._cached_repos[provider_env] = GcpGcsRepository()
        
        return ModelRepositoryFactory._cached_repos.get(provider_env, AzureBlobRepository())
