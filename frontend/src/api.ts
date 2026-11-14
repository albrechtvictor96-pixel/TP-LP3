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

// Este tipo describe cada actividad que forma parte de una solicitud.
export interface DetalleSolicitud {
  ID_DETALLE_SOLICITUD_CAE: number
  ID_SOLICITUD_CAE: number
  FECHA_ACTIVIDAD: string
  ACTIVIDAD: string
  CARGA_HORARIA_EN_MINUTOS: number
  SUPERVISADO: string | null
  ID_USUARIO_SUPERVISA: number | null
}

// Estos son los datos de una solicitud que devuelve el backend.
export interface Solicitud {
  ID_SOLICITUD_CAE: number
  FECHA_SOLICITUD: string
  HORA_SOLICITUD: string
  ID_ACTIVIDAD: number
  ID_USUARIO_SOLICITA: number
  ESTADO_SOLICITUD: string
  OBSERVACIONES: string | null
  FECHA_APROBACION_O_RECHAZO: string | null
  ID_USUARIO_APRUEBA_O_RECHAZA: number | null
  CREDITOS_CALCULADOS: number
  detalles: DetalleSolicitud[]
}

// Este tipo describe los créditos acumulados y el máximo de cada categoría.
export interface CreditosPorCategoria {
  ID_ACTIVIDAD: number
  NOMBRE_ACTIVIDAD: string
  CREDITOS_OBTENIDOS: number
  MAXIMO_CREDITOS: number
}

// El backend devuelve el progreso y la cantidad de solicitudes por estado.
export interface Progreso {
  ID_USUARIO: number
  CREDITOS_APROBADOS: number
  META_CREDITOS: number
  CREDITOS_FALTANTES: number
  PORCENTAJE_COMPLETADO: number
  META_CUMPLIDA: boolean
  CANTIDAD_PENDIENTE: number
  CANTIDAD_EN_REVISION: number
  CANTIDAD_APROBADA: number
  CANTIDAD_RECHAZADA: number
  CREDITOS_POR_CATEGORIA: CreditosPorCategoria[]
}

// Solo estos estados se pueden enviar al endpoint de resolución.
export type EstadoResolucion = 'APROBADA' | 'RECHAZADA'

// Estos son los datos que el backend recibe para resolver una solicitud.
export interface DatosResolucion {
  ESTADO_SOLICITUD: EstadoResolucion
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

// Pedimos los usuarios para mostrar nombres en lugar de solo sus identificadores.
export async function listarUsuarios(): Promise<Usuario[]> {
  let respuesta: Response

  try {
    respuesta = await fetch(`${DIRECCION_API}/usuarios/`)
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let mensaje = 'No se pudieron cargar los usuarios.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  try {
    return await respuesta.json() as Usuario[]
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

// Buscamos solicitudes propias o filtramos por estado para la pantalla de revisión.
export async function listarSolicitudes(
  idUsuario?: number,
  estado?: string,
): Promise<Solicitud[]> {
  let respuesta: Response
  const filtros = new URLSearchParams()
  if (idUsuario !== undefined) filtros.set('id_usuario', String(idUsuario))
  if (estado) filtros.set('estado', estado)
  const consulta = filtros.toString()

  try {
    respuesta = await fetch(
      `${DIRECCION_API}/solicitudes/${consulta ? `?${consulta}` : ''}`,
    )
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let mensaje = 'No se pudieron cargar tus solicitudes.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  try {
    return await respuesta.json() as Solicitud[]
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}

// Pasamos una solicitud pendiente al estado EN_REVISION.
export async function iniciarRevision(
  idSolicitud: number,
  idUsuario: number,
): Promise<Solicitud> {
  let respuesta: Response

  try {
    respuesta = await fetch(
      `${DIRECCION_API}/solicitudes/${idSolicitud}/revision?id_usuario=${idUsuario}`,
      { method: 'PUT' },
    )
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let mensaje = 'No se pudo iniciar la revisión.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  try {
    return await respuesta.json() as Solicitud
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}

// Enviamos la aprobación o el rechazo junto con el usuario de dirección.
export async function resolverSolicitud(
  idSolicitud: number,
  idUsuario: number,
  datos: DatosResolucion,
): Promise<Solicitud> {
  let respuesta: Response

  try {
    respuesta = await fetch(
      `${DIRECCION_API}/solicitudes/${idSolicitud}/resolucion?id_usuario=${idUsuario}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      },
    )
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let mensaje = 'No se pudo resolver la solicitud.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  try {
    return await respuesta.json() as Solicitud
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}

// Consultamos créditos aprobados y cantidades por estado para el estudiante.
export async function obtenerProgreso(idUsuario: number): Promise<Progreso> {
  let respuesta: Response

  try {
    respuesta = await fetch(`${DIRECCION_API}/progreso/${idUsuario}`)
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let mensaje = 'No se pudo cargar tu progreso.'
    try {
      const resultado: { detail?: string } = await respuesta.json()
      mensaje = resultado.detail || mensaje
    } catch {
      throw new Error('El servidor devolvió una respuesta inválida.')
    }
    throw new Error(mensaje)
  }

  try {
    return await respuesta.json() as Progreso
  } catch {
    throw new Error('El servidor devolvió una respuesta inválida.')
  }
}
