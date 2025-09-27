
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
  - get-appointments: consulta citas (appointments) por rango de fechas o disponibilidad (availability) por fecha.
  - get-user-appointment: obtiene las citas en Acuity del usuario autenticado (filtrando por su clientID de Acuity).
  - create-appointment: crea una cita en Acuity para el usuario autenticado (resolviendo/creando clientID en Acuity si falta).
  - edit-appointment: edita o reprograma una cita existente del usuario.
  - cancel-appointment: cancela una cita existente del usuario.
- DynamoDB:
  - Tabla de vínculos users_links para relacionar cliente de Shopify ↔ cliente de Acuity (clientID).


## Estructura del repositorio

lambdas/ authorizer/ get-calendars/ get-appointments/ get-user-appointment/ create-appointment/ edit-appointment/ cancel-appointment/ layers/ dependencies/python/ # utilidades compartidas (db_repository, http_utils, etc.) project/ api_gateway.py # definición del API Gateway y rutas lambdas.py # creación y configuración de Lambdas permissions.py # políticas IAM y rol de ejecución stack.py # stack principal (tablas, lambdas, api) tables.py # tablas de DynamoDB app.py # entrypoint CDK requirements.txt # dependencias CDK requirements_layers.txt # (opcional) dependencias para la layer requests.http # ejemplos de pruebas manuales


## Variables de entorno

Estas variables se inyectan a los Lambdas desde CDK (ver `project/lambdas.py`). Importante:
- ACUITY_USER_ID y ACUITY_API_KEY siempre están presentes por diseño. No es necesario validarlas en los lambdas.

Variables:
- USER_LINKS_TABLE: nombre de la tabla DynamoDB para vínculos Shopify↔Acuity (la provee CDK).
- ACUITY_USER_ID: User ID numérico de Acuity (Basic Auth).
- ACUITY_API_KEY: API Key de Acuity (Basic Auth).
- SHOPIFY_STORE_DOMAIN: dominio myshopify.com de tu tienda (para el authorizer).
- SHOPIFY_STOREFRONT_ACCESS_TOKEN: token Storefront API para validar el customerAccessToken del cliente (authorizer).
- SHOPIFY_API_VERSION: versión de la Storefront API (ej.: 2024-07). 

Sugerencia: puedes definir estos valores en `cdk.json` dentro del contexto (e.g. “sbx”) y leerlos en `app.py`/`stack.py`.


## Tablas DynamoDB

Tabla users_links (creada por `project/tables.py`):
- Partition Key (PK): customerId (string)
- Sort Key (SK): profile (string)
- Item “perfil principal”:
  - customerId: "<shopifyCustomerId>"
  - profile: "les-aimants" (sentinela para el ítem canónico del perfil)
  - email, shopDomain, firstName, lastName, phone
  - acuityClientId (string)
  - createdAt (epoch ms), updatedAt (epoch ms)

Razón de diseño:
- SK fijo (“profile”) permite colgar más ítems del mismo usuario en el futuro (auditoría, cache, preferencias) sin migrar esquema.


## Endpoints (API Gateway)

Los recursos y métodos se definen en `project/api_gateway.py`. Ejemplo de mapeo:

- POST /                → create-appointment (requiere authorizer)
- PUT /                 → edit-appointment (requiere authorizer)
- GET /                 → get-calendars (requiere authorizer)
- POST /availability    → get-appointments (modo availability o appointments)
- POST /user-appointments → get-user-appointment (citas del usuario)
- POST /cancel          → cancel-appointment (cancelar cita)

Autorización:
- Lambda Authorizer (Token Authorizer) que espera Authorization: Bearer <customerAccessToken>.
- El authorizer valida el token contra Shopify Storefront y adjunta al contexto:
  - shopifyCustomerId, email, firstName, lastName, phone, shopDomain


## Descripción de Lambdas

- authorizer
  - Valida el customerAccessToken contra Shopify Storefront GraphQL (customer(customerAccessToken: ...)).
  - Si es válido, “Allow” y adjunta datos del cliente al context.
- get-calendars
  - GET https://acuityscheduling.com/api/v1/calendars
  - Retorna data: [calendarios], meta: {resource: "calendars"}.
- get-appointments
  - resource="appointments": GET /appointments con minDate, maxDate, etc.
  - resource="availability": GET /availability/times con date, etc.
  - Retorna data con la respuesta original de Acuity.
- get-user-appointment
  - Resuelve el acuityClientId del usuario (Dynamo o lookup por email en Acuity).
  - GET /appointments?clientID=...&minDate=...&maxDate=...
  - 404 si no hay cliente o no hay citas; 200 con data si existen.
- create-appointment
  - Resuelve/crea cliente en Acuity si falta (por email).
  - POST /appointments con datetime, calendarID, appointmentTypeID, clientID.
  - 201 con data al crear.
- edit-appointment
  - Verifica que la cita pertenezca al usuario (GET /appointments/{id} y comparar clientID).
  - action="update": PUT /appointments/{id} (notes, label, fields, admin).
  - action="reschedule": PUT /appointments/{id}/reschedule (datetime, calendarID, timezone).
- cancel-appointment
  - Verifica propiedad (GET /appointments/{id}).
  - PUT /appointments/{id}/cancel (opcional reason/notifyClient).


## Convenciones de manejo de errores

- 200/201: operación exitosa (se retorna la respuesta original de Acuity dentro de “data”).
- 400: parámetros faltantes o inválidos (validación Pydantic o chequeos en handler).
- 401: falta info crítica del authorizer (shopifyCustomerId o email).
- 404: recursos no encontrados o no pertenecen al usuario (citas inexistentes o vacías).
- 502: error de upstream (Acuity) o fallos de red/timeout (incluir upstream.status y body cuando sea posible).
- 500: error interno no controlado.

Notas:
- Nunca se exponen llaves/secretos en respuestas o logs.
- ACUITY_USER_ID y ACUITY_API_KEY se asumen siempre presentes y no se validan en tiempo de ejecución.


## Requisitos

- Python 3.12
- AWS CDK v2 instalado (CLI)
- AWS credenciales configuradas (perfil con permisos suficientes)
- virtualenv (recomendado)

Dependencias:
- requirements.txt: dependencias de CDK.
- requirements_layers.txt (opcional): si agregas dependencias para la Lambda layer (por ejemplo, requests si no está incluida por defecto en el runtime o en tu layer).


## Setup de desarrollo

1) Crear entorno virtual
```
python3.12 -m venv .venv source .venv/bin/activate # Linux/Mac
# .venv\Scripts\activate # Windows (PowerShell)
``` 

2) Instalar dependencias de CDK
```
pip install -r requirements.txt
``` 

3) (Opcional) Empaquetar layer de dependencias
- Colocar librerías puras de Python en `layers/dependencies/python/`.
- Si usas requirements_layers.txt, constrúyela y cópiala ahí.

4) Configurar contexto (cdk.json)
- Define en el contexto (por ejemplo clave “sbx”) los valores requeridos:
  - ACUITY_USER_ID, ACUITY_API_KEY
  - SHOPIFY_STORE_DOMAIN, SHOPIFY_STOREFRONT_ACCESS_TOKEN, SHOPIFY_API_VERSION
- El nombre de la tabla users_links se deriva del stack y se pasa a los Lambdas via `USER_LINKS_TABLE`.


## Despliegue

1) Bootstrap (primera vez por cuenta/region)
```
cdk bootstrap
``` 

2) Synth
```
cdk synth
``` 

3) Deploy
```
cdk deploy
``` 

El stack creará:
- Tabla DynamoDB users_links
- Lambdas (authorizer, get-calendars, get-appointments, get-user-appointment, create-appointment, edit-appointment, cancel-appointment)
- API Gateway con rutas y Lambda Authorizer


## Pruebas

- requests.http contiene ejemplos que puedes adaptar.
- Autorización:
  - Envía el header Authorization: Bearer <customerAccessToken_de_Shopify>.
- Cuerpos típicos:
  - availability (get-appointments):
    ```
    { "resource": "availability", "date": "YYYY-MM-DD", "appointmentTypeId": 123, "timezone": "America/Mexico_City" }
    ```
  - appointments (get-appointments):
    ```
    { "resource": "appointments", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }
    ```
  - create-appointment:
    ```
    { "datetime": "2025-09-20T10:00:00-05:00", "calendarID": 12345, "appointmentTypeID": 6789, "timezone": "America/Mexico_City" }
    ```
  - get-user-appointment:
    ```
    { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }
    ```
  - edit-appointment (reschedule):
    ```
    { "action": "reschedule", "appointmentId": 11111, "datetime": "2025-09-21T10:00:00-05:00", "timezone": "America/Mexico_City" }
    ```
  - cancel-appointment:
    ```
    { "appointmentId": 11111, "reason": "Motivo (opcional)", "notifyClient": true }
    ```


## Buenas prácticas y notas

- Usa el calendarID que viene en los “slots” de availability al crear citas.
- Mantén actualizado el vínculo Shopify↔Acuity (acuityClientId) en Dynamo para evitar lookups frecuentes.
- Maneja las zonas horarias explícitamente (IANA TZ) para evitar errores de horario.
- No hardcodees IDs de calendarios/appointment types si cambian con frecuencia; expón endpoints para descubrirlos (get-calendars).
- Controla la latencia del authorizer (caché de resultados en API Gateway está habilitado por 1 hora).


## Soporte

Para dudas o incidencias:
- Revisa logs en CloudWatch por cada Lambda.
- Verifica configuración del contexto (cdk.json) y variables inyectadas.
- Valida credenciales de Acuity y Storefront de Shopify.

