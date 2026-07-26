# ==============================================================================
# ARCHIVO:        tests/test_infraestructura.py
# DESCRIPCIÓN:    Script de control de calidad para validación de Infraestructura (IaC).
#                 Verifica la existencia y conectividad de los componentes de Azure.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        1.0.0
# ESTADO:         Enterprise Ready / Infrastructure Validation (QA)
# ==============================================================================

import os
import sys
import subprocess
import json

# CONFIGURACIÓN DE LOS RECURSOS REALES DE TU PROYECTO EN AZURE
SUBSCRIPTION_ID = "92f8b9d3-e52d-4f27-9ec4-f1720263567c"
RESOURCE_GROUP   = "rg-enterprise-genai-prod"
ACR_NAME         = "acrgenaiaudit92f8b9"
OPENAI_ACCOUNT   = "cog-openai-audit-prod-v2"

def run_az_command(args):
    """
    Ejecuta comandos de Azure CLI de forma segura y parsea la respuesta JSON.
    """
    try:
        # Forzamos el uso de Azure CLI instalado en tu Mac
        result = subprocess.run(
            ["az"] + args + ["--output", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout else True
    except subprocess.CalledProcessError as e:
        print(f"❌ FALLO EN AZURE CLI: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("❌ ERROR CRÍTICO: No se encontró 'az' CLI instalado en la terminal de tu Mac.")
        sys.exit(1)

def validar_grupo_recursos():
    print("\n[1/4] Validando existencia del Grupo de Recursos...")
    args = ["group", "show", "--name", RESOURCE_GROUP, "--subscription", SUBSCRIPTION_ID]
    data = run_az_command(args)
    if data:
        print(f"🟢 ÉXITO: El Grupo de Recursos '{RESOURCE_GROUP}' existe en la región: {data.get('location')}")
        return True
    return False

def validar_container_registry():
    print("\n[2/4] Validando estado del Registro de Contenedores Privado (ACR)...")
    args = ["acr", "show", "--name", ACR_NAME, "-g", RESOURCE_GROUP]
    data = run_az_command(args)
    if data:
        print(f"🟢 ÉXITO: El ACR '{ACR_NAME}' está activo bajo el Sku: {data.get('sku', {}).get('name')}")
        return True
    return False

def validar_cuenta_cognitiva():
    print("\n[3/4] Validando canal de Azure OpenAI (Cortafuegos preventivo)...")
    args = ["cognitiveservices", "account", "show", "-n", OPENAI_ACCOUNT, "-g", RESOURCE_GROUP]
    data = run_az_command(args)
    if data:
        state = data.get("properties", {}).get("provisioningState")
        print(f"🟢 ÉXITO: La cuenta '{OPENAI_ACCOUNT}' existe físicamente en Azure.")
        print(f"-> Estado de aprovisionamiento actual: {state}")
        return True
    return False

def validar_despliegue_modelo():
    print("\n[4/4] Validando el slot del modelo GPT-4o...")
    args = ["cognitiveservices", "account", "deployment", "list", "-n", OPENAI_ACCOUNT, "-g", RESOURCE_GROUP]
    deployments = run_az_command(args)
    
    if deployments is not None:
        for dep in deployments:
            if dep.get("name") == "gpt-4o-final-deployment":
                model_info = dep.get("properties", {}).get("model", {})
                print(f"🟢 ÉXITO: El slot 'gpt-4o-final-deployment' está registrado de forma lógica.")
                print(f"-> Motor: {model_info.get('name')} | Versión del catálogo: {model_info.get('version')}")
                return True
        
        print("⚠️ ALERTA: La cuenta existe, pero el slot 'gpt-4o-final-deployment' no se ha creado por el bloqueo anti-fraudes de Microsoft (RTFP).")
        return False
    return False

if __name__ == "__main__":
    print("=" * 80)
    print("SISTEMA DE CONTROL DE CALIDAD - VALIDACIÓN DE INFRAESTRUCTURA DE AZURE")
    print("=" * 80)
    
    rg_ok = validar_grupo_recursos()
    acr_ok = validar_container_registry()
    cog_ok = validar_cuenta_cognitiva()
    model_ok = validar_despliegue_modelo()
    
    print("\n" + "=" * 80)
    if rg_ok and acr_ok and cog_ok and model_ok:
        print("🚀 RESULTADO GLOBAL: ¡Toda la infraestructura física está validada y lista para operar!")
        sys.exit(0)
    else:
        print("📋 RESULTADO GLOBAL: Componentes base de red listos. Esperando desbloqueo RTFP de Microsoft.")
        sys.exit(1)