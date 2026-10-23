# Spec Delta

## Purpose

Registro y autenticación de usuarios con JWT, con roles diferenciados (teacher/student) que determinan qué operaciones puede realizar cada usuario en el sistema.

## ADDED Requirements

### Requirement: User registration
El sistema SHALL permitir registrar usuarios proporcionando name, email, password y role (teacher o student). El email SHALL ser único en el sistema.

#### Scenario: Registro exitoso
- **WHEN** un usuario envía POST /auth/register con name, email, password y role válidos
- **THEN** el sistema crea el usuario con password_hash (nunca almacena la contraseña en texto plano) y responde 201 con id, email y role

#### Scenario: Email duplicado
- **WHEN** un usuario envía POST /auth/register con un email que ya existe en el sistema
- **THEN** el sistema responde 409 sin crear un usuario nuevo

#### Scenario: Campos obligatorios faltantes
- **WHEN** un usuario envía POST /auth/register sin alguno de los campos requeridos (name, email, password, role)
- **THEN** el sistema responde 422 con detalle de validación

### Requirement: User login
El sistema SHALL autenticar usuarios mediante email y password, devolviendo un token JWT válido para acceder a los endpoints protegidos.

#### Scenario: Login exitoso
- **WHEN** un usuario envía POST /auth/login con email y password correctos
- **THEN** el sistema responde 200 con access_token (JWT) y token_type "bearer"

#### Scenario: Credenciales inválidas
- **WHEN** un usuario envía POST /auth/login con email inexistente o password incorrecto
- **THEN** el sistema responde 401 sin revelar cuál de los dos datos es incorrecto

### Requirement: JWT-protected endpoints
Todos los endpoints excepto /auth/register y /auth/login SHALL requerir un header Authorization con un Bearer token JWT válido. El token MUST contener el user_id y el role del usuario.

#### Scenario: Acceso sin token
- **WHEN** un usuario llama a cualquier endpoint protegido sin header Authorization
- **THEN** el sistema responde 401

#### Scenario: Token expirado o inválido
- **WHEN** un usuario llama a un endpoint protegido con un token JWT expirado o malformado
- **THEN** el sistema responde 401

### Requirement: Role-based access
El sistema SHALL diferenciar entre roles teacher y student. Un teacher puede gestionar asignaturas y subir material. Un student puede consultar asignaturas y usar el chat.

#### Scenario: Docente accede a funcionalidad de docente
- **WHEN** un usuario con role teacher llama a un endpoint exclusivo de docente (crear asignatura, subir documento)
- **THEN** el sistema permite la operación

#### Scenario: Estudiante intenta operación de docente
- **WHEN** un usuario con role student intenta crear una asignatura o subir un documento
- **THEN** el sistema responde 403
