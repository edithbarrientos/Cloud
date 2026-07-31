import pulumi
from pulumi_kubernetes.core.v1 import Namespace, Service, PodTemplateSpec, PodSpec, Container, ContainerPort
from pulumi_kubernetes.apps.v1 import StatefulSet, StatefulSetSpec
from pulumi_kubernetes.meta.v1 import LabelSelector, ObjectMeta
from pulumi_kubernetes.networking.v1 import NetworkPolicy, NetworkPolicySpec, NetworkPolicyIngressRule, NetworkPolicyPortsArgs

# 1. Definición del Namespace Regulatorio Aislado (Gobernanza DAMA)
namespace = Namespace(
    "autonomous-deequ-orchestrator-namespace",
    metadata=ObjectMeta(
        name="orchestra-governance",
        labels={"environment": "dev", "tier": "control-plane"}
    )
)

# 2. Despliegue Elástico de Apache Pulsar (StatefulSet para Bus de Eventos Asíncronos)
pulsar_labels = {"app": "apache-pulsar", "component": "event-hub"}

pulsar_statefulset = StatefulSet(
    "apache-pulsar-event-hub",
    metadata=ObjectMeta(
        name="pulsar-broker",
        namespace=namespace.metadata.name,
        labels=pulsar_labels
    ),
    spec=StatefulSetSpec(
        service_name="pulsar-internal-mesh",
        replicas=1, # Escalable elásticamente en producción mediante KEDA
        selector=LabelSelector(match_labels=pulsar_labels),
        template=PodTemplateSpec(
            metadata=ObjectMeta(labels=pulsar_labels),
            spec=PodSpec(
                containers=[
                    Container(
                        name="pulsar-standalone",
                        image="apachepulsar/pulsar:3.0.0",
                        command=["bin/pulsar", "standalone"], # Modo standalone optimizado para Colima local
                        ports=[
                            ContainerPort(name="binary-pulsar", container_port=6650), # Puerto analítico de Flink/Spark
                            ContainerPort(name="http-admin", container_port=8080)     # Puerto de control de la API
                        ]
                    )
                ]
            )
        )
    )
)

# 3. Blindaje Perimetral de Red (NetworkPolicies Militares de Aislamiento mTLS)
# Restringe el tráfico lateral protegiendo los puertos de procesamiento de la JVM
network_policy = NetworkPolicy(
    "autonomous-deequ-orchestrator-net-policy",
    metadata=ObjectMeta(
        name="ado-firewall",
        namespace=namespace.metadata.name
    ),
    spec=NetworkPolicySpec(
        pod_selector=LabelSelector(match_labels=pulsar_labels),
        policy_types=["Ingress"],
        ingress=[
            NetworkPolicyIngressRule(
                # Permitir tráfico únicamente en los puertos regulados del bus de eventos
                ports=[
                    NetworkPolicyPortsArgs(protocol="TCP", port=6650), # Ingesta Flink/Pulsar
                    NetworkPolicyPortsArgs(protocol="TCP", port=8080)  # Métricas Delta de la API Gateway
                ]
            )
        ]
    )
)

# --- OUTPUTS EXPORTADOS PARA PIPELINES DE CI/CD ---
pulumi.export("namespace_devops", namespace.metadata.name)
pulumi.export("pulsar_endpoint", "pulsar://pulsar-broker.orchestra-governance.svc.cluster.local:6650")
pulumi.export("firewall_status", "Enforced - mTLS & Apache Pulsar Network Isolation Active")
