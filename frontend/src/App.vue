<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LoginView from './views/LoginView.vue'
import NuevaSolicitudView from './views/NuevaSolicitudView.vue'
import RegistroView from './views/RegistroView.vue'
import { cargarSesion, usuarioSesion } from './sesion'

// Elegimos qué pantalla mostrar y restauramos la sesión al abrir la aplicación.
const pantalla = ref<'login' | 'registro' | 'solicitud'>('login')
onMounted(() => {
  cargarSesion()
  if (usuarioSesion.value) {
    pantalla.value = 'solicitud'
  }
})
</script>

<template>
  <LoginView
    v-if="pantalla === 'login'"
    @ir-registro="pantalla = 'registro'"
    @sesion-iniciada="pantalla = 'solicitud'"
  />
  <RegistroView v-else-if="pantalla === 'registro'" @ir-login="pantalla = 'login'" />
  <NuevaSolicitudView v-else />
</template>
