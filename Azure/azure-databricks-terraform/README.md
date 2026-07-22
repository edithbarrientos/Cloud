# Azure Databricks Workspace Seguro con Arquitectura Híbrida Interregional

Este proyecto implementa una arquitectura de grado empresarial y máxima seguridad para **Azure Databricks** utilizando Terraform de forma modular. El entorno está diseñado bajo un esquema de conectividad híbrida entre regiones para evadir de forma automatizada las restricciones de stock de hardware y las políticas de cuotas de cómputo en la nube, garantizando un aislamiento perimetral robusto.

---

## 🏗️ Arquitectura de Seguridad Implementada

El diseño de infraestructura garantiza el cumplimiento normativo mediante los siguientes componentes perimetrales distribuidos en dos regiones de Azure:

* **VNet Injection (Región `eastus2`)**: Los clústeres de Databricks se ejecutan dentro de una Red Virtual propia, divididos en subnets dedicadas (`Host` y `Container`) con delegación oficial de servicio.
* **Secure Cluster Connectivity (No Public IP)**: Los nodos del clúster se despliegan sin direcciones IP públicas. El tráfico de gestión se realiza de forma saliente mediante túneles seguros.
* **NAT Gateway (Región `eastus2`)**: Todo el tráfico saliente de los clústeres (descarga de librerías, parches o conexiones a APIs externas) se centraliza a través de una IP pública estática controlada, evitando la exposición de los nodos.
* **Private Link & Enlaces DNS**: El acceso a la interfaz web (UI) está protegido por un Private Endpoint conectado a una Zona DNS Privada. Esta zona se vincula por código a ambas redes para resolver las rutas web de forma interna.
* **VNet Peering Interregional**: Conecta de forma transparente la red de Databricks (`eastus2`) con la red de acceso (`eastus`) mediante la fibra óptica privada de Microsoft, permitiendo que la máquina de salto opere de forma 100% interna.
* **Acceso Público Controlado**: El espacio de trabajo expone su plano de autenticación pública de forma segura para permitir que los mecanismos de Single Sign-On (SSO) de Microsoft Entra ID procesen las credenciales del usuario de forma nativa sin perder el aislamiento de red de los datos.
* **Infraestructura de Acceso Seguro (Jumpbox + Bastion en `eastus`)**: Para administrar la plataforma visualmente evadiendo la falta de stock de hardware, se despliega una Máquina de Salto Linux moderna (`Standard_D2s_v4`) protegida dentro de la red satélite, accesible únicamente mediante un túnel HTTPS cifrado provisto por **Azure Bastion**.

---

## 📁 Estructura del Proyecto Actual (Híbrido)

El código está organizado de forma limpia utilizando submódulos locales y aislamiento de componentes:

```text
📦 azure-databricks-terraform
 ┣ 📜 main.tf                  # 🔵 Orquestador raíz (Resource Groups, VNets, Peering, Bastion y VM Linux)
 ┣ 📜 providers.tf             # 🟤 Definición de proveedores (AzureRM, Databricks y HTTP)
 ┣ 📜 README.md                # 🟢 Documentación técnica y Roadmap del proyecto
 ┗ 📂 modules
   ├── network/
   │   ├── main.tf             # 🟠 Configuración de VNet, Subnets, NAT Gateway y NSG obligatorio
   │   ├── outputs.tf          # 🟠 Exportación de IDs de red y asociaciones de seguridad
   │   └── variables.tf        # 🟠 Declaraciones de contexto (Resource Group y Location)
   └── databricks/
       ├── main.tf             # 🟣 Workspace Premium, Private Endpoint y registros DNS interregionales
       ├── outputs.tf          # 🟣 Exportación de la URL segura del Workspace y su ID de recurso
       └── variables.tf        # 🟣 Parámetros de configuración e inyección de red con validaciones
```

---

## 🛠️ Requisitos Previos

Antes de ejecutar los comandos en tu terminal de VS Code, asegúrate de contar con:
1. [Terraform CLI](https://hashicorp.com) (Versión `>= 1.5.0`).
2. [Azure CLI](https://microsoft.com) instalado.
3. Una suscripción activa de Azure con permisos de propietario o colaborador.

---

## 🚀 Guía de Despliegue Paso a Paso

Ejecuta los siguientes comandos de forma secuencial en la **terminal raíz** del proyecto dentro de VS Code:

### 1. Autenticación en Azure
Conéctate a tu suscripción activa iniciando sesión en la ventana del navegador que se abrirá automáticamente:
```bash
az login
```

### 2. Inicializar el Entorno
Descarga los proveedores en caché y registra las rutas de los módulos locales:
```bash
terraform init
```

### 3. Validar el Código
Comprueba que la sintaxis de todos los archivos y el circuito de variables entre módulos estén libres de errores:
```bash
terraform validate
```

### 4. Simular la Infraestructura (Plan)
Revisa detalladamente qué recursos se añadirán a tu cuenta antes de realizar cambios reales:
```bash
terraform plan
```

### 5. Desplegar los Recursos
Envía la configuración a la nube para iniciar la construcción. El parámetro `-lock=false` evita bloqueos por cancelaciones previas:
```bash
terraform apply -lock=false
```
*Escribe `yes` cuando la consola solicite tu aprobación y presiona Enter.*

---

## 🖥️ Cómo Conectarse al Área de Trabajo Web

Una vez completado el despliegue con éxito, sigue estos pasos para acceder de forma privada:

1. **Obtén tu URL única**: En tu terminal local de VS Code, ejecuta `terraform output` y copia el valor devuelto en `workspace_url` (ej: `https://dbw-secure-prod.azuredatabricks.net`).
2. **Accede al Portal de Azure**: Ve a tu grupo de recursos de acceso `rg-secure-databricks-access` y haz clic en la máquina virtual **`vm-jumpbox-prod`**.
3. **Inicia el túnel seguro**: En el menú superior o izquierdo de la máquina, selecciona **Bastion** e ingresa las credenciales del proyecto:
   * **Usuario**: `adminazure`
   * **Contraseña**: `P@ssw0rdDatabricks2026!`
4. **Abre Databricks**: Dentro de la pestaña de navegación de tu máquina de salto, ingresa a una ventana en **Modo Incógnito / InPrivate** (obligatorio para limpiar cookies), pega tu URL de Databricks e inicia sesión con tu cuenta normal de Azure (`edithbaga@tuta.com`) mediante Single Sign-On (SSO).

---

## 🛑 Destrucción Controlada (Limpieza de costos)

Cuando termines tus pruebas o validaciones de laboratorio, recuerda eliminar toda la infraestructura para evitar cargos no deseados en tu factura de Azure:
```bash
terraform destroy -lock=false
```
Escribe `yes` para confirmar la eliminación de todos los recursos de forma automatizada.

---

## 📈 Mejoras Pendientes (Roadmap de Target Enterprise)

Para elevar esta infraestructura a un estándar de grado de producción corporativo listo para auditorías internacionales, se deben planificar las siguientes implementaciones en el código:

### 1. Estado de Terraform Colaborativo (Remote Backend)
* **Objetivo:** Mover el archivo local `terraform.tfstate` de tu computadora hacia la nube para permitir que múltiples ingenieros colaboren sin pisarse el código.
* **Acción:** Configurar un bloque `backend "azurerm"` en el archivo `backend.tf` apuntando a un **Azure Storage Account** privado con un contenedor bloqueado con redundancia geográfica (RA-GRS).

### 2. Gobernanza de Datos Centralizada (Unity Catalog)
* **Objetivo:** Activar el motor de gobernanza de datos de Databricks para auditar accesos, compartir datos de forma segura y gestionar permisos a nivel de filas y columnas.
* **Acción:** Desplegar mediante Terraform un recurso `azurerm_databricks_access_connector` conectado a una cuenta de almacenamiento dedicada (**ADLS Gen2**) para que actúe como el almacenamiento raíz del Metastore.

### 3. Doble Capa de Enlace Privado (Private Link Completo Back-end)
* **Objetivo:** Aislar los clústeres de cómputo al 100%. Actualmente, el Private Endpoint protege el acceso de los usuarios (Front-end). Se requiere bloquear también el canal de comunicación entre las máquinas virtuales del clúster y el plano de control de Databricks.
* **Acción:** Configurar un segundo Private Endpoint en el módulo de Databricks con el subrecurso `browser_authentication`.

### 4. Gestión de Llaves por el Cliente (Customer-Managed Keys - CMK)
* **Objetivo:** Garantizar la propiedad absoluta del cifrado de datos en reposo para cumplir con regulaciones financieras o de salud (HIPAA / PCI-DSS).
* **Acción:** Desplegar un **Azure Key Vault** en el código raíz y configurar el Workspace para que use llaves criptográficas propias para cifrar los cuadernos (notebooks) y los discos duros temporales de las máquinas virtuales de Spark.

### 5. Monitoreo Analítico Centralizado (Diagnostic Settings)
* **Objetivo:** Capturar en tiempo real las bitácoras de auditoría de quién ejecuta códigos, qué clústeres se encienden y qué consultas SQL se realizan.
* **Acción:** Integrar el recurso `azurerm_monitor_diagnostic_setting` para redirigir de forma automática los logs nativos de Databricks hacia un servicio de **Azure Log Analytics Workspace**.

### 6. Control de Identidades Automatizado (SCIM Integration)
* **Objetivo:** Automatizar las altas, bajas y permisos de grupos de usuarios en tiempo real sincronizándolo de forma directa con tu Azure Entra ID (Azure AD).
* **Acción:** Declarar los recursos de aprovisionamiento de identidades de Databricks mediante el conector SCIM oficial corporativo.

---

```text
📦 Estructura de Carpetas Objetivo (Target Enterprise):
 ┣ 📜 backend.tf               # 🔵 Remote Backend con almacenamiento RA-GRS (Resiliencia Geográfica)
 ┣ 📜 main.tf                  # 🔵 Orquestador raíz (RG, Peering Híbrido, UDR, Bastion y VM Linux)
 ┣ 📜 providers.tf             # 🔵 Definición de proveedores con versiones estables fijadas
 ┣ 📜 terraform.tfvars         # 🔵 Inyección de valores específicos del ambiente actual
 ┣ 📜 variables.tf             # 🔵 Declaraciones y validaciones de variables del proyecto raíz
 ┗ 📂 modules
