import { ref } from 'vue'
import type { Usuario } from './api'

// Esta referencia comparte en la aplicación los datos del usuario conectado.
export const usuarioSesion = ref<Usuario | null>(null)

// Recuperamos la sesión guardada para conservarla al recargar la página.
export function cargarSesion(): void {
  const usuarioGuardado = localStorage.getItem('usuarioCAE')
  if (!usuarioGuardado) {
    return
  }

  try {
    usuarioSesion.value = JSON.parse(usuarioGuardado) as Usuario
  } catch {
    localStorage.removeItem('usuarioCAE')
    usuarioSesion.value = null
  }
}

// Guardamos solo los datos del usuario que devolvió el backend.
export function guardarSesion(usuario: Usuario): void {
  usuarioSesion.value = usuario
  localStorage.setItem('usuarioCAE', JSON.stringify(usuario))
}

// Quitamos la sesión del navegador y limpiamos la referencia compartida.
export function cerrarSesion(): void {
  usuarioSesion.value = null
  localStorage.removeItem('usuarioCAE')
}
