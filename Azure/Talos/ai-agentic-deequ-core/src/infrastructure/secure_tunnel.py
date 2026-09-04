# -*- coding: utf-8 -*-
# ======================================================================================================================
# PROJECT: Autonomous Deequ Orchestrator (ADO) - Enterprise Cognitive Engine
# MODULE: Infrastructure Support Layer - Reverse SSH Tunneling Matrix
# FILE: secure_tunnel.py
# AUTHOR: Orchestra Labs Enterprise Architecture
# VERSION: 1.0.0
# COMPATIBILITY: Python 3.11+ / asyncio Async Event Loop Engine / Native SSH Sockets
# ======================================================================================================================

import asyncio
import logging
import time
import sys
from typing import Dict, Any

class SecureInferenceTunnel:
    """
    🔌 INFRASTRUCTURE TUNNEL MATRIX
    Responsabilidad:
        Establecer y gobernar un canal inverso cifrado (Reverse SSH Tunnel) no bloqueante.
        Mapea el puerto local de inferencia 8001 hacia el puerto 8001 del host remoto de la nube,
        permitiendo una interconexión elástica multi-tenant sin abrir firewalls públicos.
    """
    def __init__(self, config_blueprint: Dict[str, Any] = None):
        self.logger = logging.getLogger("SecureInferenceTunnel")
        self.config = config_blueprint or {}
        
        # Parámetros de conexión cifrada extraídos de la configuración activa
        self.remote_cloud_host = self.config.get("cloud_gateway_ip", "127.0.0.1")
        self.ssh_user = self.config.get("ssh_tunnel_user", "orchestra_telemetry_proxy")
        self.ssh_key_path = self.config.get("ssh_key_absolute_path", "~/.ssh/id_rsa_ado")
        
        # Puertos de la matriz de transporte
        self.local_engine_port = 8001
        self.remote_forward_port = 8001
        
        self.is_tunnel_active = False

    async def establish_reverse_tunnel_async(self) -> None:
        """
        Gatilla una sub-tarea asíncrona no bloqueante que invoca al cliente SSH binario del OS.
        Implementa reconexión automática infinita ante caídas de red o sisiones cerradas por hardware.
        """
        self.logger.info(f"[TUNNEL_START] Configurando pasarela criptografica inversa hacia: {self.remote_cloud_host}")
        
        # Comando POSIX estricto para túnel inverso: ssh -N -R remoto:local user@host
        # -N: No ejecuta comandos remotos (Optimizado para puros túneles de puertos)
        # -R: Forwarding inverso de sockets directos en la RAM
        # -o ServerAliveInterval=10: Watchdog que envía pings de salud cada 10 segundos para evitar deadlocks
        ssh_command = (
            f"ssh -N -R {self.remote_forward_port}:127.0.0.1:{self.local_engine_port} "
            f"-o StrictHostKeyChecking=no -o ServerAliveInterval=10 "
            f"-i {self.ssh_key_path} {self.ssh_user}@{self.remote_cloud_host}"
        )

        while True:
            try:
                self.logger.info("[TUNNEL_CONNECTING] Abriendo tunel SSH inverso y enlazando descriptores de red...")
                
                # Ejecución de subproceso asíncrono cediendo el control al event loop de asyncio
                process = await asyncio.create_subprocess_shell(
                    ssh_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                self.is_tunnel_active = True
                self.logger.info(f"[TUNNEL_ESTABLISHED_SUCCESS] Sockets mapeados con exito. Canal seguro abierto: Cloud:{self.remote_forward_port} -> Local:127.0.0.1:{self.local_engine_port}")
                
                # Espera no bloqueante hasta que el subproceso del sistema termine o falle por red
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    self.logger.error(f"[TUNNEL_DISCONNECTED] El tunel se cerro con codigo de salida: {process.returncode}. Motivo: {stderr.decode().strip()}")
                
            except asyncio.CancelledError:
                self.logger.warning("[TUNNEL_CANCELLED] Solicitud de apagado de la pasarela interceptada. Cerrando sockets de forma limpia...")
                if 'process' in locals():
                    try: process.terminate()
                    except ProcessLookupError: pass
                self.is_circuit_open = False
                break
                
            except Exception as system_error:
                self.logger.error(f"[TUNNEL_NETWORK_CRASH] Fallo critico en la conexion de hardware del tunel: {str(system_error)}")
            
            # Reconexión automática con degradación controlada: Espera 5 segundos antes de reintentar el enlace
            self.is_tunnel_active = False
            self.logger.warning("[TUNNEL_RETRY_BACKOFF] Reintentando inicializacion de la pasarela criptografica en 5 segundos...")
            await asyncio.sleep(5.0)
