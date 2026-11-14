# Sistema de Gestión de Créditos Extraacadémicos

Trabajo práctico de Lenguaje de Programación III para registrar y revisar
actividades extraacadémicas y consultar los créditos de cada estudiante.

## Tecnologías

- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, bcrypt y SQLite.
- **Frontend:** Vue 3, TypeScript, Vite y Vue Router.
- **Base de datos:** SQLite. La aplicación usa el archivo existente
  `backend/cae_sqlite.db`.

## Requisitos

- Python 3.10 o superior.
- Node.js y npm.
- PowerShell en Windows.

## Instalar y ejecutar el backend

Desde la carpeta principal del proyecto, abrí PowerShell y ejecutá:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```

La documentación interactiva de la API está en
<http://127.0.0.1:8000/docs>.

## Instalar y ejecutar el frontend

En una segunda ventana de PowerShell:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Abrí <http://localhost:5173> en el navegador. El backend debe estar activo para
que el frontend pueda consultar y guardar información.

## Roles del sistema

- **Estudiante:** registra solicitudes, consulta su historial y su progreso, y
  puede ver los criterios de créditos.
- **Dirección académica:** revisa, aprueba o rechaza solicitudes y puede ver los
  criterios de créditos.
- **Dirección de carrera:** revisa, aprueba o rechaza solicitudes y puede ver los
  criterios de créditos.

El sistema registra nuevas cuentas con el rol de estudiante. Las cuentas de
dirección deben existir previamente en la base de datos. No se incluyen
credenciales en este documento.
