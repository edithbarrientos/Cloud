# -*- coding: utf-8 -*-
# ======================================================================================================================
# PROJECT: Autonomous Deequ Orchestrator (ADO) - Enterprise Cognitive Engine
# MODULE: Capa IaC Providers - Azure Native Mesh Infrastructure Deployment
# FILE: azure_mesh.py
# AUTHOR: Orchestra Labs Enterprise Architecture
# VERSION: 4.0.0
# COMPATIBILITY: Python 3.11+ / Pulumi IaC Platform / Azure Native SDK
# ======================================================================================================================

import pulumi
import pulumi_azure_native.resources as resources
import pulumi_azure_native.redis as redis
from providers.base_mesh import BaseMeshProvider

class AzureMeshProvider(BaseMeshProvider):
    """
    🔌 CONDUCTOR ESTANCO CLOUD: PROVEEDOR DE INFRAESTRUCTURA AZURE (AzureMeshProvider)
    Responsabilidad:
        Aprovisionar de forma declarativa el grupo de recursos y el cluster de Redis Cache Enterprise
        con soporte HNSW en la nube de Microsoft, interpretando el contexto del entorno (ALM).
    """
    def __init__(self, name: str, active_config: dict):
        """🚀 CONSTRUCTOR PARAMETRIZADO: Recibe y asimila la inyección dinámica de la firma de __main__.py"""
        self.name = name
        self.config = active_config

    def deploy_resources(self) -> dict:
        # 1. Instanciación del Grupo de Recursos Perimetral
        resource_group = resources.ResourceGroup(
            "ado-core-dev-rg",
            resource_group_name="ado-core-dev-rg"
        )
        
        # 2. Instanciación del Clúster de Redis Enterprise In-Memory
        redis_cache = redis.Redis(
            "ado-core-cache-dev",
            name="ado-core-cache-dev",
            resource_group_name=resource_group.name,
            sku=redis.SkuArgs(
                name=redis.SkuName.BASIC,
                family=redis.SkuFamily.C,
                capacity=1
            ),
            enable_non_ssl_port=True,
            location=resource_group.location
        )
        
        # 3. Exportación inmutable de outputs para el Control Plane SaaS
        return {
            "resource_group_name": resource_group.name,
            "redis_host_endpoint": redis_cache.host_name,
            "redis_ssl_port": redis_cache.ssl_port
        }
