<script setup lang="ts">
import { ref } from 'vue'
import LoginView from './views/LoginView.vue'
import RegistroView from './views/RegistroView.vue'

// Elegimos si mostrar el formulario de acceso o el de creación de cuenta.
const pantalla = ref<'login' | 'registro'>('login')
</script>

<template>
  <LoginView
    v-if="pantalla === 'login'"
    @ir-registro="pantalla = 'registro'"
  />
  <RegistroView
    v-else
    @ir-login="pantalla = 'login'"
  />
</template>
