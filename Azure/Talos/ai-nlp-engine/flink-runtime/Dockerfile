# 🪐 IMAGEN BASE OFICIAL DE ENTORNO DISTRIBUIDO DE APACHE FLINK
FROM flink:1.18.1-java11

# 🛡️ CAPA DE PROTECCIÓN CORE: Actualiza y parcha los paquetes de Debian para eliminar vulnerabilidades CVE (High)
USER root
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Definición del directorio de trabajo nativo del motor de streaming
WORKDIR /opt/flink

# Creación de la carpeta protegida de librerías de usuario
RUN mkdir -p /opt/flink/usrlib

# 🚀 INYECCIÓN DEL ARTEFACTO: Copiamos el Fat JAR unificado con soporte Jackson y Varints
COPY target/artifacts/ai-nlp-stream-agent.jar /opt/flink/usrlib/ai-nlp-stream-agent.jar

# Cambiamos los privilegios al usuario nativo de flink por estándares estrictos de seguridad de K8s
RUN chown -R flink:flink /opt/flink/usrlib

USER flink

# El contenedor hereda el punto de entrada oficial para levantar hilos JobManager o TaskManager
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["--help"]