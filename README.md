# Shopify ↔ Acuity Appointments API (AWS CDK + Lambdas)
Este proyecto implementa una API en AWS para:
- Autenticar clientes de Shopify (Storefront) mediante un Lambda Authorizer.
- Consultar calendarios y disponibilidad en Acuity Scheduling.
- Crear, editar, cancelar y listar citas de usuarios en Acuity.
- Mantener el vínculo entre el cliente de Shopify y el cliente de Acuity en DynamoDB.

La solución está construida con AWS CDK (v2) en Python, AWS Lambda (Python 3.12), API Gateway REST y DynamoDB.
## Arquitectura (alto nivel)
- API Gateway (REST):
    - Protegido por un Lambda Authorizer (Token Authorizer) que valida el customerAccessToken de Shopify Storefront.

- Lambdas (Python 3.12):
    - authorizer: valida el token del cliente de Shopify contra Storefront GraphQL y adjunta datos del cliente al contexto de API Gateway.
    - get-calendars: lista los calendarios configurados en Acuity.
    - get-appointments: consulta citas por rango de fechas o disponibilidad por fecha.
    - get-user-appointment: obtiene las citas del usuario autenticado (filtrando por su clientID de Acuity).
    - create-appointment: crea una cita para el usuario autenticado (resolviendo/creando clientID en Acuity si falta).
    - edit-appointment: edita o reprograma una cita existente del usuario.
    - cancel-appointment: cancela una cita existente del usuario.

- DynamoDB:
    - Tabla users_links para relacionar cliente de Shopify ↔ cliente de Acuity (clientID).

## Requisitos e instalación de herramientas
- Python 3.12
- AWS CLI v2 instalado y configurado
- Node.js y npm (para instalar CDK CLI)
- AWS CDK v2 (CLI)
- virtualenv (recomendado)

Instalación y verificación:
``` bash
# Instalar CDK CLI (requiere npm)
npm install -g aws-cdk

# Verificar versiones
python3.12 --version
aws --version
cdk --version
```
Dependencias del proyecto:
- requirements.txt: dependencias para CDK y utilidades del proyecto.
- requirements_layers.txt (opcional): dependencias que irán en la Lambda Layer.

## Preparación del entorno
1. Crear y activar entorno virtual
``` bash
# Linux/Mac
python3.12 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
```
1. Actualizar pip (opcional pero recomendado)
``` bash
pip install --upgrade pip
```
1. Instalar dependencias del proyecto
``` bash
pip install -r requirements.txt
```
1. Instalar dependencias para la Lambda Layer (opcional)

- Carpeta objetivo: layers/dependencies/python/
``` bash
# Crear carpeta si no existe
mkdir -p layers/dependencies/python

# Instalar dependencias de la layer en la ruta esperada por Lambda
pip install -r requirements_layers.txt -t layers/dependencies/python
```
Notas:
- Mantén solo paquetes necesarios para reducir tamaño del asset (puedes limpiar tests, *.dist-info si fuera necesario).
- CDK empaquetará esta carpeta como asset de la layer si el stack la referencia.

## Variables de entorno (Lambdas)
Estas variables se inyectan a los Lambdas desde CDK. Importante:
- ACUITY_USER_ID y ACUITY_API_KEY siempre están presentes por diseño (no requieren validación en runtime).

Variables:
- USER_LINKS_TABLE: nombre de la tabla DynamoDB para vínculos Shopify↔Acuity.
- ACUITY_USER_ID: User ID numérico de Acuity (Basic Auth).
- ACUITY_API_KEY: API Key de Acuity (Basic Auth).
- SHOPIFY_STORE_DOMAIN: dominio myshopify.com de tu tienda (para el authorizer).
- SHOPIFY_STOREFRONT_ACCESS_TOKEN: token Storefront API para validar el customerAccessToken (authorizer).
- SHOPIFY_API_VERSION: versión de la Storefront API (ej.: 2024-07).

Sugerencia: define estos valores en cdk.json dentro del contexto (por ejemplo “sbx”) y consúmelos en app/stack.
## Estructura del repositorio (resumen)
- lambdas/
    - authorizer/
    - get-calendars/
    - get-appointments/
    - get-user-appointment/
    - create-appointment/
    - edit-appointment/
    - cancel-appointment/

- layers/
    - dependencies/
        - python/ (paquetes de la layer)

- project/
    - api_gateway.py (definición del API Gateway y rutas)
    - lambdas.py (creación y configuración de Lambdas)
    - permissions.py (políticas IAM y rol de ejecución)
    - stack.py (stack principal)
    - tables.py (tablas de DynamoDB)

- app.py (entrypoint CDK)
- requirements.txt
- requirements_layers.txt (opcional)
- requests.http (ejemplos de pruebas manuales)
- cdk.json

## Configurar credenciales y perfil de AWS (CLI)
1. Crear usuario IAM (consola web)

- Usuario con acceso programático (Access key).
- Permisos adecuados para CDK. En no productivo: AdministratorAccess (simple). En productivo: principio de mínimo privilegio (CloudFormation, S3, IAM, Lambda, API Gateway, DynamoDB, CloudWatch Logs, STS).

1. Configurar perfil en AWS CLI
``` bash
aws configure --profile mi-perfil
# AWS Access Key ID: <tu-access-key-id>
# AWS Secret Access Key: <tu-secret-access-key>
# Default region name: us-east-1
# Default output format: json
```
1. Verificar identidad y región
``` bash
aws sts get-caller-identity --profile mi-perfil
aws configure get region --profile mi-perfil
```
1. (Opcional) Exportar el perfil como variable de entorno
``` bash
# Linux/Mac
export AWS_PROFILE=mi-perfil

# Windows (PowerShell)
# $Env:AWS_PROFILE = "mi-perfil"
```
## Endpoints (API Gateway)
- POST / → create-appointment (requiere authorizer)
- PUT / → edit-appointment (requiere authorizer)
- GET / → get-calendars (requiere authorizer)
- POST /availability → get-appointments (availability o appointments)
- POST /user-appointments → get-user-appointment (citas del usuario)
- POST /cancel → cancel-appointment (cancelar cita)

Autorización:
- Lambda Authorizer (Token Authorizer) que espera: Authorization: Bearer .
- El authorizer adjunta al contexto: shopifyCustomerId, email, firstName, lastName, phone, shopDomain.

## Tablas DynamoDB
Tabla users_links:
- PK: customerId (string)
- SK: profile (string)
- Ítem canónico de perfil:
    - customerId: ""
    - profile: "les-aimants"
    - email, shopDomain, firstName, lastName, phone
    - acuityClientId (string)
    - createdAt (epoch ms), updatedAt (epoch ms)

Nota: SK fijo permite colgar más ítems del mismo usuario en el futuro (auditoría, cache, preferencias).
## Convenciones de manejo de errores
- 200/201: operación exitosa (se retorna la respuesta original de Acuity dentro de data).
- 400: parámetros faltantes o inválidos.
- 401: falta info crítica del authorizer (shopifyCustomerId o email).
- 404: recurso no encontrado o no pertenece al usuario.
- 502: error de upstream (Acuity) o fallos de red/timeout (incluir upstream.status/body si es posible).
- 500: error interno no controlado.

Buenas prácticas:
- No exponer llaves/secretos en respuestas o logs.
- ACUITY_USER_ID y ACUITY_API_KEY se asumen presentes.

## Despliegue (con perfil configurado)
Pre-requisito (una sola vez por cuenta/región): Bootstrap de CDK (crea bucket de assets y roles base).
1. Bootstrap
``` bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION> --profile mi-perfil
# O si exportaste AWS_PROFILE:
# cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```
1. Synth (generar CloudFormation)
``` bash
cdk synth --profile mi-perfil
# o: cdk synth
```
1. Deploy
``` bash
cdk deploy --profile mi-perfil
# Opcional: pasar contexto/stage
# cdk deploy -c stage=sbx --profile mi-perfil
```
Recursos que crea el stack:
- Tabla DynamoDB users_links
- Lambdas (authorizer, get-calendars, get-appointments, get-user-appointment, create-appointment, edit-appointment, cancel-appointment)
- API Gateway con rutas y Lambda Authorizer

## Pruebas rápidas
- Usa requests.http como guía.
- Autorización: header Authorization: Bearer <customerAccessToken_de_Shopify>.
- Ejemplos de cuerpos:
``` json
// availability (get-appointments)
{ "resource": "availability", "date": "YYYY-MM-DD", "appointmentTypeId": 123, "timezone": "America/Mexico_City" }

// appointments (get-appointments)
{ "resource": "appointments", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }

// create-appointment
{ "datetime": "2025-09-20T10:00:00-05:00", "calendarID": 12345, "appointmentTypeID": 6789, "timezone": "America/Mexico_City" }

// get-user-appointment
{ "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }

// edit-appointment (reschedule)
{ "action": "reschedule", "appointmentId": 11111, "datetime": "2025-09-21T10:00:00-05:00", "timezone": "America/Mexico_City" }

// cancel-appointment
{ "appointmentId": 11111, "reason": "Motivo (opcional)", "notifyClient": true }
```
## Notas y recomendaciones
- Usa el calendarID que viene en los “slots” de availability al crear citas.
- Mantén el vínculo Shopify↔Acuity (acuityClientId) en Dynamo para evitar lookups frecuentes.
- Maneja zonas horarias con IDs IANA para evitar errores.
- Evita hardcodear IDs cambiantes; usa endpoints de descubrimiento (get-calendars).
- Considera la latencia del authorizer; la caché de API Gateway ayuda.

## Soporte
- Verifica logs en CloudWatch por cada Lambda.
- Revisa el contexto en cdk.json y variables inyectadas.
- Valida credenciales de Acuity y Storefront de Shopify.
- Asegura que el perfil de AWS tenga permisos adecuados para CDK.
