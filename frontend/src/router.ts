import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import LoginView from './views/LoginView.vue'
import RegistroView from './views/RegistroView.vue'
import NuevaSolicitudView from './views/NuevaSolicitudView.vue'
import MisSolicitudesView from './views/MisSolicitudesView.vue'
import RevisionSolicitudesView from './views/RevisionSolicitudesView.vue'
import CriteriosView from './views/CriteriosView.vue'
import { usuarioSesion } from './sesion'

// Cada ruta indica si necesita iniciar sesión y qué roles pueden usarla.
const rutas: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView, meta: { publica: true } },
  { path: '/registro', component: RegistroView, meta: { publica: true } },
  {
    path: '/nueva-solicitud',
    component: NuevaSolicitudView,
    meta: { roles: ['estudiante'] },
  },
  {
    path: '/mis-solicitudes',
    component: MisSolicitudesView,
    meta: { roles: ['estudiante'] },
  },
  {
    path: '/revision',
    component: RevisionSolicitudesView,
    meta: { roles: ['direccion_academica', 'direccion_carrera'] },
  },
  { path: '/criterios', component: CriteriosView },
  { path: '/:rutaNoEncontrada(.*)', redirect: '/login' },
]

// Elegimos la pantalla principal según el rol guardado en la sesión.
function rutaPrincipal(): string {
  const rol = usuarioSesion.value?.ROLE_ACCESO
  if (rol === 'estudiante') return '/mis-solicitudes'
  if (rol === 'direccion_academica' || rol === 'direccion_carrera') return '/revision'
  return '/login'
}

const router = createRouter({
  history: createWebHistory(),
  routes: rutas,
})

// Protegemos las rutas privadas y evitamos que un rol abra pantallas ajenas.
router.beforeEach((destino) => {
  const usuario = usuarioSesion.value

  if (destino.path === '/') {
    return rutaPrincipal()
  }

  if (destino.meta.publica) {
    if (usuario && rutaPrincipal() !== '/login') return rutaPrincipal()
    return true
  }

  if (!usuario) return '/login'

  const rolesPermitidos = destino.meta.roles as string[] | undefined
  if (rolesPermitidos && !rolesPermitidos.includes(usuario.ROLE_ACCESO)) {
    return rutaPrincipal()
  }

  return true
})

export default router
