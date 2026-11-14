# Documento técnico

## Descripción

El sistema permite que un estudiante presente actividades extraacadémicas, que una persona revisora las apruebe o rechace y que el estudiante consulte cuánto le falta para llegar a 20 créditos. Los créditos se reconocen solamente cuando la solicitud queda aprobada.

## Arquitectura

- **Back-End:** la carpeta `backend/` contiene una API REST en Python y FastAPI. SQLAlchemy conecta los modelos con SQLite y Pydantic describe y valida los datos de entrada y salida. Las funciones son síncronas para mantener simple el flujo.
- **Front-End:** `frontend/` contiene la interfaz Vue 3 y TypeScript, servida por Vite y conectada a la API mediante `fetch`. Vue Router gestiona las pantallas y la navegación por rol. El backend habilita CORS para `http://localhost` y `http://127.0.0.1`, en cualquier puerto.
- **Base de datos:** `backend/cae_sqlite.db` guarda usuarios, actividades, solicitudes y sus detalles. La ruta se calcula desde la ubicación del backend.

## Tablas

| Tabla | Uso |
|---|---|
| `USUARIOS` | Datos de estudiantes y revisores, rol, estado y hash de contraseña. |
| `ACTIVIDADES` | Catálogo de actividades, créditos y horas requeridas. |
| `SOLICITUDES_CAES` | Fecha de solicitud, estudiante, actividad, estado y resolución. |
| `DETALLE_SOLICITUDES_CAES` | Fecha de realización, carga horaria, actividad y supervisión informadas. |
| `DETALLE_DOCUMENT_SOLICITUD_CAES` | Tabla existente para documentos adjuntos; no se utiliza en los endpoints actuales. |

## Endpoints principales

| Método y ruta | Función |
|---|---|
| `POST /registro` | Crea siempre una cuenta estudiante y guarda la contraseña como hash bcrypt. |
| `POST /login` | Busca por cédula y compara la contraseña con el hash; devuelve datos sin la contraseña. |
| `GET /actividades/` | Muestra el catálogo activo e inactivo con sus créditos y horas. |
| `POST /solicitudes/` | Valida estudiante, actividad, fecha, carga horaria y duplicados; guarda solicitud y detalle juntos. |
| `GET /solicitudes/` y `GET /solicitudes/{id_solicitud}` | Lista con filtros o consulta una solicitud con su detalle. |
| `PUT /solicitudes/{id_solicitud}/revision` | Un revisor cambia una solicitud pendiente a `EN_REVISION`. |
| `PUT /solicitudes/{id_solicitud}/resolucion` | Un revisor aprueba o rechaza y registra fecha e identificador del revisor. |
| `GET /progreso/{id_usuario}` | Calcula créditos aprobados, faltantes, porcentaje y conteos de estados. |

Las rutas que necesitan un rol reciben el ID de usuario y comprueban el rol guardado en la base. Para la resolución, `id_usuario` va en la URL como parámetro de consulta.

### Ejemplo de solicitud y respuesta

Solicitud `POST /solicitudes/`:

```json
{
  "ID_ACTIVIDAD": 1,
  "ID_USUARIO_SOLICITA": 2,
  "FECHA_ACTIVIDAD": "2026-10-20",
  "CARGA_HORARIA_EN_MINUTOS": 60,
  "SUPERVISADO": "Docente"
}
```

Respuesta resumida:

```json
{
  "ID_SOLICITUD_CAE": 1,
  "ESTADO_SOLICITUD": "PENDIENTE",
  "ID_ACTIVIDAD": 1,
  "ID_USUARIO_SOLICITA": 2,
  "detalles": [
    {
      "FECHA_ACTIVIDAD": "2026-10-20",
      "ACTIVIDAD": "Asignaturas Electivas",
      "CARGA_HORARIA_EN_MINUTOS": 60
    }
  ]
}
```

Ejemplo de respuesta `GET /progreso/2`:

```json
{
  "ID_USUARIO": 2,
  "CREDITOS_APROBADOS": 2,
  "META_CREDITOS": 20,
  "CREDITOS_FALTANTES": 18,
  "PORCENTAJE_COMPLETADO": 10.0,
  "META_CUMPLIDA": false,
  "CANTIDAD_PENDIENTE": 1,
  "CANTIDAD_EN_REVISION": 0,
  "CANTIDAD_APROBADA": 1,
  "CANTIDAD_RECHAZADA": 0
}
```

## Elección de tecnologías

- **Python:** su sintaxis clara facilita leer y explicar el flujo en una exposición.
- **FastAPI:** aprovecha los type hints, genera documentación interactiva y permite expresar errores HTTP con `HTTPException`.
- **SQLAlchemy:** representa las tablas como clases y permite consultar SQLite desde Python.
- **Pydantic:** deja explícita la forma de los datos recibidos y de las respuestas.

## Dificultades y decisiones

- Se corrigió el nombre `SOLICITUDES_CAESS` para que coincida con la tabla real `SOLICITUDES_CAES`.
- La base tenía contraseñas sin hash; `actualizar_db.py` las convierte a bcrypt y se puede ejecutar varias veces.
- La solicitud y el detalle se guardan en una misma transacción para evitar que quede uno sin el otro.
- La regla de duplicados permite presentar de nuevo la misma actividad y fecha cuando la solicitud anterior fue rechazada.
- El progreso se calcula con consultas; no se agregó una tabla de resumen.
- Las reglas actuales de créditos siguen la Resolución 33/2020 de la UC, Campus Guairá; se detallan en la sección **Reglas de negocio actuales**.
- El login no genera tokens, según el alcance definido para este trabajo.

## Capturas de pantalla

- **[Insertar captura 1: documentación interactiva de Swagger en `/docs`].**
- **[Insertar captura 2: solicitud creada con estado `PENDIENTE`].**
- **[Insertar captura 3: progreso del estudiante].**

## Arquitectura actual

> Esta sección describe la versión actual del sistema y actualiza las referencias
> anteriores que indicaban que el frontend estaba reservado o que los créditos
> eran provisorios.

- **Frontend:** Vue 3 con TypeScript y Composition API. Vite sirve la aplicación y
  Vue Router gestiona las rutas y la navegación según el rol.
- **Backend:** API REST sincrónica en FastAPI. Pydantic valida los datos de las
  solicitudes y respuestas; SQLAlchemy consulta y modifica la base.
- **Base de datos:** SQLite en `backend/cae_sqlite.db`. Las reglas y los créditos
  se calculan desde el código; no se agregó una tabla para el progreso.

## Pantallas y rutas del frontend

| Ruta | Pantalla | Quién puede acceder | Función |
|---|---|---|---|
| `/login` | Iniciar sesión | Público | Inicia sesión con cédula y contraseña. |
| `/registro` | Crear cuenta | Público | Registra una cuenta con rol estudiante. |
| `/nueva-solicitud` | Nueva solicitud | Estudiante | Presenta una actividad con fecha, carga horaria, supervisor y observaciones. |
| `/mis-solicitudes` | Mis solicitudes | Estudiante | Muestra historial, estados, créditos y progreso por categoría. |
| `/revision` | Revisión de solicitudes | Dirección académica y dirección de carrera | Inicia revisión, aprueba o rechaza solicitudes. |
| `/criterios` | Criterios de créditos | Todos los roles con sesión | Consulta las horas por crédito y los topes de cada categoría. |

La barra de navegación muestra las opciones del rol, los datos de la sesión y el
botón para cerrar sesión. Login y registro no muestran la barra. La sesión se
guarda en `localStorage` para conservarla al recargar la página.

## Endpoints actuales del backend

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/` | Informa que el backend está activo. |
| `POST` | `/registro` | Crea una cuenta estudiante; exige una contraseña de al menos seis caracteres. |
| `POST` | `/login` | Comprueba cédula y contraseña y devuelve los datos del usuario sin la contraseña. |
| `GET` | `/usuarios/` | Lista usuarios con nombre, cédula, carrera y rol, sin incluir contraseñas. |
| `GET` | `/actividades/` | Devuelve el catálogo de actividades. |
| `GET` | `/criterios` | Devuelve las horas por crédito y el máximo para cada categoría reglamentada. |
| `POST` | `/solicitudes/` | Crea una solicitud pendiente y su detalle. |
| `GET` | `/solicitudes/?id_usuario=&estado=` | Lista solicitudes; ambos filtros son opcionales. |
| `GET` | `/solicitudes/{id_solicitud}` | Consulta una solicitud junto con sus detalles. |
| `PUT` | `/solicitudes/{id_solicitud}/revision?id_usuario=` | Pasa una solicitud pendiente a `EN_REVISION`. |
| `PUT` | `/solicitudes/{id_solicitud}/resolucion?id_usuario=` | Aprueba o rechaza una solicitud; al rechazar exige `OBSERVACIONES` en el cuerpo JSON. |
| `GET` | `/progreso/{id_usuario}` | Devuelve créditos aprobados, progreso, conteos por estado y créditos por categoría. |

## Reglas de negocio actuales

Los estados de las solicitudes son `PENDIENTE`, `EN_REVISION`, `APROBADA` y
`RECHAZADA`. Los estudiantes crean sus propias solicitudes. Solo los roles
`direccion_academica` y `direccion_carrera` pueden iniciar la revisión y
resolverlas. Solo las solicitudes aprobadas aportan créditos al progreso.

Según la Resolución 33/2020 de la UC, Campus Guairá, las categorías implementadas
son:

| ID de actividad | Categoría | Horas por crédito | Máximo de créditos |
|---:|---|---:|---:|
| 1 | Asignaturas electivas | 16 | 5 |
| 2 | Cursos o talleres | 16 | 5 |
| 3 | Conferencias, congresos y seminarios | 16 | 4 |
| 4 | Ayudantías de cátedra o de laboratorio | 16 | 4 |
| 5 | Pasantías extracurriculares | 48 | 4 |
| 6 | Investigación | 32 | 8 |
| 7 | Extensión universitaria | 32 | 4 |
| 8 | Compromiso social | 32 | 2 |

La actividad 9 no está incluida en las reglas y, por ahora, no otorga créditos.
La meta total es de 20 créditos.

El cálculo sigue el Art. 5: se suman los minutos de los detalles de una
solicitud, se convierten a horas y se dividen por las horas requeridas por
crédito. El resultado de cada solicitud se trunca a un decimal. Luego se suman
los créditos de las solicitudes aprobadas de cada categoría y se aplica el
máximo correspondiente. Finalmente se trunca a entero la suma de las categorías.
El porcentaje de progreso no supera el 100%.

Para mantener simple el alcance del trabajo se asumieron estos criterios:

- Las conferencias se calculan usando el caso FCYT.
- Para electivas y ayudantías se toma un semestre de 16 semanas.
- No se implementan los requisitos académicos específicos de las ayudantías.
- No se implementa el Art. 7.

## Seguridad y limitaciones conocidas

- Las contraseñas se guardan como hashes bcrypt y no se devuelven en las
  respuestas de usuarios.
- El backend valida los roles consultando la base de datos en las operaciones
  que requieren permisos. Las protecciones de Vue Router son además de esa
  comprobación, no la reemplazan.
- CORS permite solicitudes desde `localhost` y `127.0.0.1` en cualquier puerto,
  para facilitar el desarrollo local.
- El login no genera tokens JWT. La sesión del frontend se conserva en
  `localStorage`.
- La autorización del backend recibe `id_usuario` enviado por el cliente y
  comprueba su rol en la base. No hay un token firmado que vincule esa identidad
  con cada solicitud HTTP.
- `GET /usuarios/` no requiere sesión y devuelve datos personales básicos
  (cédula, nombres, apellidos y carrera), aunque excluye las contraseñas.
