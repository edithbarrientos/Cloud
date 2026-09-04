import pulumi_aws as aws
from providers.base_mesh import BaseCloudMesh
from typing import Dict, Any

class AwsMeshProvider(BaseCloudMesh):
    def deploy_resources(self) -> Dict[str, Any]:
        redis_cluster = aws.elasticache.Cluster(
            f"{self.name}-broker",
            cluster_id=f"ado-core-{self.config['tier']}-cache",
            engine="redis",
            node_type="cache.t3.micro" if self.config["tier"] != "prod" else "cache.r5.xlarge",
            num_cache_nodes=1,
            parameter_group_name="default.redis7"
        )
        return {"provider": "aws", "host": redis_cluster.cache_nodes.address}
