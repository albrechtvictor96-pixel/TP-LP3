// Esta dirección es la URL local del backend FastAPI.
const DIRECCION_API = 'http://127.0.0.1:8000'

// Este tipo contiene los datos que el backend devuelve al iniciar sesión.
export interface Usuario {
  ID_USUARIO: number
  NRO_CEDULA: number
  NOMBRES: string
  APELLIDOS: string
  CARRERA: string
  ROLE_ACCESO: string
}

// Estos son los dos campos que el endpoint de login espera recibir.
export interface DatosLogin {
  NRO_CEDULA: number
  CONTRASENHA: string
}

// Este tipo contiene todos los campos que el backend pide para registrar estudiante.
export interface DatosRegistro {
  NRO_CEDULA: number
  NOMBRES: string
  APELLIDOS: string
  CODIGO_MATRICULA: string
  EMAIL: string
  TELEFONO_CELULAR: string
  CONTRASENHA: string
  CARRERA: string
}

// Este tipo describe las actividades que devuelve el catálogo del backend.
export interface Actividad {
  ID_ACTIVIDAD: number
  NOMBRE_ACTIVIDAD: string
  ACTIVO: number
  OBSERVACIONES: string | null
  CREDITOS: number
  HORAS_REQUERIDAS: number
}

// Estos son los campos que recibe el endpoint para crear una solicitud.
export interface DatosSolicitud {
  ID_ACTIVIDAD: number
  ID_USUARIO_SOLICITA: number
  FECHA_ACTIVIDAD: string
  CARGA_HORARIA_EN_MINUTOS: number
  SUPERVISADO: string | null
  OBSERVACIONES: string | null
}

// Enviamos las credenciales y devolvemos los datos seguros del usuario.
export async function iniciarSesion(datos: DatosLogin): Promise<Usuario> {
  let respuesta: Response

  // Capturamos el error de conexión para mostrar un mensaje entendible.
  try {
    respuesta = await fetch(`${DIRECCION_API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  // Leemos la respuesta JSON que devuelve FastAPI.
  let resultado: { detail?: string } | Usuario
  try {
    resultado = await respuesta.json()
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }

  // Explicamos los errores de acceso y los demás errores del backend.
  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error('Usuario o contraseña incorrectos.')
    }

    throw new Error(
      'detail' in resultado && resultado.detail
        ? resultado.detail
        : 'No se pudo iniciar sesión.',
    )
  }

  // El endpoint devuelve el usuario sin incluir la contraseña.
  return resultado as Usuario
}

// Enviamos los datos del formulario al endpoint de registro de estudiantes.
export async function registrarUsuario(datos: DatosRegistro): Promise<Usuario> {
  let respuesta: Response

  // Capturamos los problemas de conexión antes de procesar la respuesta.
  try {
    respuesta = await fetch(`${DIRECCION_API}/registro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  // Leemos los datos que devuelve FastAPI, incluso cuando informa un error.
  let resultado: { detail?: string } | Usuario
  try {
    resultado = await respuesta.json()
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }

  // Informamos si la cédula ya existe o si ocurrió otro error.
  if (!respuesta.ok) {
    if (respuesta.status === 409) {
      throw new Error('La cédula ya está registrada.')
    }

    throw new Error(
      'detail' in resultado && resultado.detail
        ? resultado.detail
        : 'No se pudo crear la cuenta.',
    )
  }

  // Devolvemos los datos seguros de la cuenta recién creada.
  return resultado as Usuario
}

// Pedimos el catálogo para llenar el selector de actividades.
export async function listarActividades(): Promise<Actividad[]> {
  let respuesta: Response

  try {
    respuesta = await fetch(`${DIRECCION_API}/actividades/`)
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  // Convertimos los errores del catálogo en mensajes entendibles.
  if (!respuesta.ok) {
    let mensaje = 'No se pudieron cargar las actividades.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  // El endpoint devuelve una lista de actividades.
  try {
    return await respuesta.json() as Actividad[]
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}

// Enviamos la solicitud nueva al backend y recibimos el registro creado.
export async function crearSolicitud(datos: DatosSolicitud): Promise<void> {
  let respuesta: Response

  try {
    respuesta = await fetch(`${DIRECCION_API}/solicitudes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  // Mostramos el mensaje del backend cuando no pudo crear la solicitud.
  if (!respuesta.ok) {
    let mensaje = 'No se pudo guardar la solicitud.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  // Leemos el JSON de confirmación para verificar que la respuesta sea válida.
  try {
    await respuesta.json()
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}
