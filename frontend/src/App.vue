<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LoginView from './views/LoginView.vue'
import NuevaSolicitudView from './views/NuevaSolicitudView.vue'
import MisSolicitudesView from './views/MisSolicitudesView.vue'
import RevisionSolicitudesView from './views/RevisionSolicitudesView.vue'
import RegistroView from './views/RegistroView.vue'
import { cargarSesion, usuarioSesion } from './sesion'

// Elegimos qué pantalla mostrar y restauramos la sesión al abrir la aplicación.
const pantalla = ref<'login' | 'registro' | 'solicitud' | 'mis-solicitudes' | 'revision'>('login')

// Enviamos a cada rol a la pantalla temporal que le corresponde.
function irAPantallaPrincipal(): void {
  const rol = usuarioSesion.value?.ROLE_ACCESO
  pantalla.value =
    rol === 'estudiante'
      ? 'solicitud'
      : rol === 'direccion_academica' || rol === 'direccion_carrera'
        ? 'revision'
        : 'login'
}

onMounted(() => {
  cargarSesion()
  if (usuarioSesion.value) {
    irAPantallaPrincipal()
  }
})
</script>

<template>
  <LoginView
    v-if="pantalla === 'login'"
    @ir-registro="pantalla = 'registro'"
    @sesion-iniciada="irAPantallaPrincipal"
  />
  <RegistroView v-else-if="pantalla === 'registro'" @ir-login="pantalla = 'login'" />
  <NuevaSolicitudView
    v-else-if="pantalla === 'solicitud'"
    @ir-mis-solicitudes="pantalla = 'mis-solicitudes'"
  />
  <MisSolicitudesView
    v-else-if="pantalla === 'mis-solicitudes'"
    @ir-nueva-solicitud="pantalla = 'solicitud'"
  />
  <RevisionSolicitudesView v-else />
</template>
