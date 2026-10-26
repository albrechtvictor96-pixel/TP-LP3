# Documento técnico

## Descripción

El sistema permite que un estudiante presente actividades extraacadémicas, que una persona revisora las apruebe o rechace y que el estudiante consulte cuánto le falta para llegar a 20 créditos. Los créditos se reconocen solamente cuando la solicitud queda aprobada.

## Arquitectura

- **Back-End:** la carpeta `backend/` contiene una API REST en Python y FastAPI. SQLAlchemy conecta los modelos con SQLite y Pydantic describe y valida los datos de entrada y salida. Las funciones son síncronas para mantener simple el flujo.
- **Front-End:** la carpeta `frontend/` está reservada para una interfaz web que puede consumir la API. El backend habilita CORS para `http://localhost` y `http://127.0.0.1`, en cualquier puerto.
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
- Los créditos y las horas actuales son valores provisorios uniformes: 2 créditos y 1 hora por actividad. Deben confirmarse con el docente.
- El login no genera tokens, según el alcance definido para este trabajo.

## Capturas de pantalla

- **[Insertar captura 1: documentación interactiva de Swagger en `/docs`].**
- **[Insertar captura 2: solicitud creada con estado `PENDIENTE`].**
- **[Insertar captura 3: progreso del estudiante].**
