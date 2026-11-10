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
