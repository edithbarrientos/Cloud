import pulumi
import pulumi_azure_native as azure_native
from abc import ABC, abstractmethod
from typing import Optional, Dict

# ==============================================================================
# 🎛️ 1. CONFIGURATION REGISTRY (Inmutable & Tipado)
# ==============================================================================
class EnvironmentConfig:
    """ Registro único de configuración con tipado estricto para evitar mutaciones erróneas. """
    def __init__(self) -> None:
        config = pulumi.Config()
        # Detección del proveedor (Estrategia)
        self.cloud_provider: str = config.get("cloudProvider") or "azure"
        
        # Parámetros específicos de Azure
        self.rg_name: str = config.get("rgName") or "rg-ai-agentic-deequ-dev"
        self.kv_name: str = config.get("kvName") or "kv-deequ-core-dev"
        self.vault_sku: str = config.get("vaultSku") or "standard"
        self.soft_delete_days: int = config.get_int("vaultSoftDeleteDays") or 7
        
        # Tags globales de gobernanza de TI
        self.global_tags: Dict[str, str] = {
            "Environment": pulumi.get_stack(),
            "Architecture-Pattern": "Abstract-Strategy-Factory",
            "Project": "AI-Agentic-Deequ-Core"
        }

# ==============================================================================
# 🛡️ 2. COMPONENT RESOURCE (Encapsulamiento de Seguridad)
# ==============================================================================
class SecureVaultComponent(pulumi.ComponentResource):
    """ Encapsula la bóveda criptográfica aislando las políticas de acceso del exterior. """
    def __init__(self, name: str, env: EnvironmentConfig, rg_name: pulumi.Output[str], location: pulumi.Output[str], opts: Optional[pulumi.ResourceOptions] = None) -> None:
        super().__init__("custom:security:SecureVaultComponent", name, {}, opts)
        
        client = azure_native.authorization.get_client_config()
        
        self.vault = azure_native.keyvault.Vault(f"{name}-kv",
            resource_group_name=rg_name,
            vault_name=env.kv_name,
            location=location,
            properties=azure_native.keyvault.VaultPropertiesArgs(
                tenant_id=client.tenant_id,
                sku=azure_native.keyvault.SkuArgs(family="A", name=env.vault_sku),
                access_policies=[azure_native.keyvault.AccessPolicyEntryArgs(
                    tenant_id=client.tenant_id,
                    object_id=client.object_id,
                    permissions=azure_native.keyvault.PermissionsArgs(
                        secrets=["get", "set", "delete", "list", "recover"]
                    )
                )],
                soft_delete_retention_in_days=env.soft_delete_days,
                enable_purge_protection=False
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )

    def inject_secret(self, secret_id: str, secret_name: str, value: pulumi.Output[str]) -> None:
        """ Abstracción inyectora de secretos con herencia de ciclo de vida (Parenting). """
        azure_native.keyvault.Secret(secret_id,
            resource_group_name=self.vault.resource_group_name,
            vault_name=self.vault.name,
            secret_name=secret_name,
            properties=azure_native.keyvault.SecretPropertiesArgs(value=value),
            opts=pulumi.ResourceOptions(parent=self)
        )

# ==============================================================================
# 🔌 3. INTERFAZ ABSTRACTA (Contrato del Patrón Strategy)
# ==============================================================================
class CloudInfrastructureStrategy(ABC):
    """ Contrato agnóstico que obliga a cualquier nube a implementar los mismos entregables. """
    @abstractmethod
    def deploy(self, env: EnvironmentConfig) -> None:
        pass

# ==============================================================================
# 🇨🇴 4. ESTRATEGIA CONCRETA: AZURE CLOUD PROVIDER
# ==============================================================================
class AzureInfrastructureStrategy(CloudInfrastructureStrategy):
    """ Implementación específica del aprovisionamiento en la nube de Microsoft. """
    def deploy(self, env: EnvironmentConfig) -> None:
        pulumi.log.info("[STRATEGY_ENGINE] 🛰️ Ejecutando estrategia nativa de Azure...")

        # A. Contenedor Lógico
        rg = azure_native.resources.ResourceGroup("ado-core-dev-rg",
            resource_group_name=env.rg_name,
            tags=env.global_tags
        )

        # B. Capa de Persistencia Cache (Redis Segura)
        redis_cache = azure_native.redis.Redis("ado-core-cache-dev",
            resource_group_name=rg.name,
            location=rg.location,
            sku=azure_native.redis.SkuArgs(name="Basic", family="C", capacity=0),
            enable_non_ssl_port=False,
            minimum_tls_version="1.2"
        )

        # C. Capa de Seguridad (Key Vault encapsulado)
        secure_vault = SecureVaultComponent("deequ-core-security", env, rg.name, rg.location)

        # D. Orquestación Interna de Secretos (Pipeline de Datos Cruzado)
        redis_token = redis_cache.access_keys.apply(lambda keys: keys.primary_access_key)
        secure_vault.inject_secret("redis-primary-key", "redis-access-token", redis_token)

        # E. Exportación de Outputs
        pulumi.export("active_cloud_provider", "azure")
        pulumi.export("active_resource_group", rg.name)
        pulumi.export("vault_secure_uri", secure_vault.vault.properties.vault_uri)
        pulumi.export("redis_host_endpoint", redis_cache.host_name)
        pulumi.export("redis_ssl_port", redis_cache.ssl_port)

# ==============================================================================
# 🏭 5. FACTORÍA CON INYECCIÓN DE ESTRATEGIA DILIGENTE
# ==============================================================================
class CloudOrchestratorFactory:
    """ Determina dinámicamente el comportamiento del despliegue en tiempo de ejecución. """
    @staticmethod
    def run() -> None:
        env = EnvironmentConfig()
        pulumi.log.info(f"[IaC_ORCHESTRATOR] Inicializando factoria dinamica para el ambiente: {pulumi.get_stack()}")

        # Diccionario de Estrategias Habilitadas (Open-Closed Principle)
        strategies: Dict[str, CloudInfrastructureStrategy] = {
            "azure": AzureInfrastructureStrategy()
            # "aws": AwsInfrastructureStrategy() <- Fácil de expandir mañana sin alterar nada más!
        }

        selected_strategy = strategies.get(env.cloud_provider.lower())
        
        if not selected_strategy:
            raise ValueError(f"❌ La estrategia de nube '{env.cloud_provider}' no está soportada actualmente.")
            
        # Inyección de dependencias e inicio del despliegue
        selected_strategy.deploy(env)

# Bloque de inicialización estándar de Python
if __name__ == "__main__":
    CloudOrchestratorFactory.run()
