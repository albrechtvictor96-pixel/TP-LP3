import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { cargarSesion } from './sesion'

// Recuperamos la sesión antes de que el router compruebe los permisos.
cargarSesion()

createApp(App).use(router).mount('#app')
