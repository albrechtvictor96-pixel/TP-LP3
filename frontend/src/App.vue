<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { cerrarSesion, usuarioSesion } from './sesion'

const ruta = useRoute()
const router = useRouter()

// Ocultamos la barra en las dos pantallas públicas.
const mostrarNavegacion = computed(
  () => ruta.path !== '/login' && ruta.path !== '/registro',
)

// Cerramos la sesión local y volvemos a la pantalla de acceso.
function salir(): void {
  cerrarSesion()
  void router.push('/login')
}
</script>

<template>
  <header v-if="mostrarNavegacion && usuarioSesion" class="barra-navegacion">
    <nav class="enlaces-navegacion" aria-label="Navegación principal">
      <template v-if="usuarioSesion.ROLE_ACCESO === 'estudiante'">
        <RouterLink to="/nueva-solicitud">Nueva solicitud</RouterLink>
        <RouterLink to="/mis-solicitudes">Mis solicitudes</RouterLink>
      </template>
      <RouterLink
        v-else-if="['direccion_academica', 'direccion_carrera'].includes(usuarioSesion.ROLE_ACCESO)"
        to="/revision"
      >
        Revisión
      </RouterLink>
      <RouterLink to="/criterios">Criterios de créditos</RouterLink>
    </nav>

    <div class="datos-sesion">
      <span>
        {{ usuarioSesion.NOMBRES }} {{ usuarioSesion.APELLIDOS }}
        <small>({{ usuarioSesion.ROLE_ACCESO }})</small>
      </span>
      <button type="button" @click="salir">Cerrar sesión</button>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
/* La barra separa las secciones y deja visibles los datos de la sesión. */
.barra-navegacion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.enlaces-navegacion,
.datos-sesion {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.enlaces-navegacion a {
  color: #334155;
  text-decoration: none;
  font-weight: 600;
}

.enlaces-navegacion a.router-link-active {
  color: #2563eb;
}

.datos-sesion {
  color: #334155;
  font-size: 0.9rem;
}

.datos-sesion small {
  color: #64748b;
}

.datos-sesion button {
  padding: 8px 12px;
  border: 0;
  border-radius: 7px;
  background: #e2e8f0;
  color: #1e293b;
  cursor: pointer;
  font: inherit;
}

.datos-sesion button:hover {
  background: #cbd5e1;
}

@media (max-width: 700px) {
  .barra-navegacion {
    align-items: flex-start;
    flex-direction: column;
    padding: 14px;
  }
}
</style>
