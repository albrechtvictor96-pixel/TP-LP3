# Sistema de Créditos Extraacadémicos

Proyecto práctico de Lenguaje de Programación III para registrar actividades extraacadémicas de estudiantes, revisar solicitudes y calcular el progreso hacia la meta de 20 créditos.

El backend está hecho con Python, FastAPI, SQLAlchemy y SQLite. La base utilizada es `backend/cae_sqlite.db`. El directorio `frontend/` queda preparado para el cliente web.

## Requisitos

- Windows 10 u 11.
- Python 3.10 o superior.
- PowerShell.

## Instalación y ejecución en Windows

1. Abrí PowerShell en la carpeta del proyecto.
2. Creá y activá un entorno virtual:

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, ejecutá `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y repetí el último comando.

3. Instalá las dependencias:

   ```powershell
   python -m pip install -r ..\requirements.txt
   ```

4. Actualizá la base de datos. Este script agrega las columnas necesarias, convierte las contraseñas de texto plano a bcrypt y crea los usuarios revisores de prueba si faltan:

   ```powershell
   python actualizar_db.py
   ```

   Se puede ejecutar más de una vez.

5. Iniciá el servidor:

   ```powershell
   python -m uvicorn main:app --reload
   ```

6. Abrí `http://127.0.0.1:8000/docs` para probar los endpoints desde Swagger. La base de datos se busca junto a los archivos Python, aunque el servidor se inicie desde otra carpeta.

## Usuarios de prueba

| Rol | Cédula | Contraseña |
|---|---:|---|
| Estudiante existente | `2222222` | `666666` |
| Dirección académica | `9990001` | `DireccionCAE123!` |
| Dirección de carrera | `9990002` | `DireccionCAE123!` |

Las contraseñas de la base quedan guardadas como hashes bcrypt. Las cuentas revisoras de prueba se crean al ejecutar `actualizar_db.py` si todavía no hay un usuario con esos roles.

## Endpoints

| Método | Ruta | Quién puede usarlo | Qué hace |
|---|---|---|---|
| GET | `/` | Público | Informa que el backend está activo. |
| GET | `/usuarios/` | Público | Lista usuarios sin incluir sus contraseñas. |
| GET | `/actividades/` | Público | Lista las actividades, su estado, créditos y horas requeridas. |
| POST | `/registro` | Cualquier persona | Registra una cuenta nueva con rol estudiante. |
| POST | `/login` | Cualquier persona | Verifica cédula y contraseña; no genera tokens. |
| POST | `/solicitudes/` | Estudiante | Crea una solicitud pendiente con su detalle. |
| GET | `/solicitudes/` | Público | Lista solicitudes; acepta `id_usuario` y `estado` como filtros opcionales. |
| GET | `/solicitudes/{id_solicitud}` | Público | Consulta una solicitud junto con su detalle. |
| PUT | `/solicitudes/{id_solicitud}/revision?id_usuario={id}` | Dirección académica o de carrera | Cambia una solicitud pendiente a `EN_REVISION`. |
| PUT | `/solicitudes/{id_solicitud}/resolucion?id_usuario={id}` | Dirección académica o de carrera | Aprueba o rechaza una solicitud pendiente o en revisión. |
| GET | `/progreso/{id_usuario}` | Estudiante | Muestra créditos aprobados, meta y cantidad de solicitudes por estado. |

Para revisar o resolver se envía el identificador del usuario revisor en el parámetro `id_usuario`. El servidor comprueba su rol consultando la base de datos.

## Reglas principales

- La meta es de 20 créditos extraacadémicos.
- Solo las solicitudes `APROBADAS` suman créditos.
- Los estados disponibles son `PENDIENTE`, `EN_REVISION`, `APROBADA` y `RECHAZADA`.
- No se acepta dos veces la misma actividad para el mismo estudiante y fecha. Una solicitud rechazada no impide volver a solicitarla.
- La aprobación o el rechazo registra la fecha y el usuario revisor.
- Los valores de créditos y horas de las actividades son provisorios; hay que confirmarlos con el docente.
