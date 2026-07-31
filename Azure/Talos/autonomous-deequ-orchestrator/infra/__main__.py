import pulumi
import pulumi_kubernetes as k8s

flink_stream_pod = k8s.core.v1.Pod(
    "ado-flink-stream-engine-pod",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ado-flink-stream-engine",
        namespace="orchestra-governance",
        labels={"app": "autonomous-data-engine", "engine": "flink"}
    ),
    spec=k8s.core.v1.PodSpecArgs(
        host_network=True,
        dns_policy="ClusterFirstWithHostNet",
        restart_policy="Always",
        containers=[
            k8s.core.v1.ContainerArgs(
                name="flink-stream-agent",
                image="apache/flink:1.18.1-scala_2.12",
                command=[
                    "java", "-cp", "/app/spark-runtime-assembly-4.0.0.jar", 
                    "com.orchestra.ado.stream.StreamApp"
                ],
                env=[
                    k8s.core.v1.EnvVarArgs(name="FLINK_COMPONENT_NAME", value="ELITE_CONCURRENT_STREAM_AGENT"),
                    k8s.core.v1.EnvVarArgs(name="FLINK_VALIDATION_KEYS", value="tenantId,schemaContract"),
                    k8s.core.v1.EnvVarArgs(name="FLINK_ANOMALY_THRESHOLD", value="0.05"),
                    k8s.core.v1.EnvVarArgs(name="FLINK_STREAM_DURATION_MS", value="20000"),
                    k8s.core.v1.EnvVarArgs(name="HOME", value="/root")
                ],
                volume_mounts=[
                    k8s.core.v1.VolumeMountArgs(name="binaries-volume", mount_path="/app")
                ]
            )
        ],
        volumes=[
            k8s.core.v1.VolumeArgs(
                name="binaries-volume",
                host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                    path="/Users/edithbg/PoC/Cloud/Azure/Talos/autonomous-deequ-orchestrator/spark-runtime/target/scala-2.12"
                )
            )
        ]
    )
)

pulumi.export("flink_stream_agent_status", flink_stream_pod.metadata.name)
