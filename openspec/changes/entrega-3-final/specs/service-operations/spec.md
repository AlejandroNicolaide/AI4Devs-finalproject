## ADDED Requirements

### Requirement: Health check
El backend SHALL exponer `GET /health` sin autenticación, que responde 200 con un cuerpo JSON `{"status": "ok"}` cuando la aplicación está en marcha, para que la plataforma de despliegue pueda comprobar su disponibilidad.

#### Scenario: Backend disponible
- **WHEN** un cliente sin credenciales llama a GET /health
- **THEN** el sistema responde 200 con `{"status": "ok"}`

### Requirement: Configurable CORS origins
Los orígenes permitidos por CORS MUST poder definirse por entorno mediante `CORS_ORIGINS` (lista separada por comas). Si no se define, el sistema SHALL permitir únicamente los orígenes de desarrollo local (`http://localhost:5173` y `http://127.0.0.1:5173`). Nunca se permiten orígenes comodín junto con credenciales.

#### Scenario: Origen permitido
- **WHEN** el navegador envía una petición con `Origin` incluido en `CORS_ORIGINS`
- **THEN** la respuesta incluye `Access-Control-Allow-Origin` con ese origen

#### Scenario: Origen no permitido
- **WHEN** el navegador envía una petición con un `Origin` que no está en la lista
- **THEN** la respuesta no incluye `Access-Control-Allow-Origin`

#### Scenario: Sin configuración
- **WHEN** `CORS_ORIGINS` no está definido
- **THEN** solo se permiten los orígenes de desarrollo local
