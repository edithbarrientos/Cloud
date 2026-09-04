import pulumi_gcp as gcp
from providers.base_mesh import BaseCloudMesh
from typing import Dict, Any

class GcpMeshProvider(BaseCloudMesh):
    def deploy_resources(self) -> Dict[str, Any]:
        redis_instance = gcp.redis.Instance(
            f"{self.name}-broker",
            name=f"ado-core-{self.config['tier']}-cache",
            tier="BASIC" if self.config["tier"] != "prod" else "STANDARD_HA",
            memory_size_gb=1 if self.config["tier"] != "prod" else 16,
            redis_version="REDIS_7_0",
            redis_configs={"maxmemory-policy": "volatile-hnsw"}
        )
        return {"provider": "gcp", "host": redis_instance.host}
