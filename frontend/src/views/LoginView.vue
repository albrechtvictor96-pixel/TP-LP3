<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { iniciarSesion } from '../api'
import { cargarSesion, guardarSesion, usuarioSesion } from '../sesion'

// Avisamos a la aplicación cuando la persona quiere abrir el registro.
const emitir = defineEmits<{ (evento: 'ir-registro'): void }>()

// Estas referencias controlan los campos y los mensajes del formulario.
const cedula = ref<number | null>(null)
const contrasenha = ref('')
const cargando = ref(false)
const mensajeError = ref('')

// Al abrir la página, recuperamos el usuario que inició sesión anteriormente.
onMounted(() => {
  cargarSesion()
})

// Enviamos la cédula y contraseña al endpoint real del backend.
async function ingresar(): Promise<void> {
  mensajeError.value = ''

  if (!cedula.value || cedula.value <= 0 || !contrasenha.value) {
    mensajeError.value = 'Ingresá una cédula y una contraseña válidas.'
    return
  }

  cargando.value = true
  try {
    const usuario = await iniciarSesion({
      NRO_CEDULA: cedula.value,
      CONTRASENHA: contrasenha.value,
    })
    guardarSesion(usuario)
    contrasenha.value = ''
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudo iniciar sesión.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <main class="pagina-login">
    <section class="tarjeta-login">
      <p class="etiqueta">Sistema CAE</p>
      <h1>Iniciar sesión</h1>
      <p class="descripcion">
        Ingresá con tu cédula y contraseña para continuar.
      </p>

      <div v-if="usuarioSesion" class="sesion-activa" role="status">
        <h2>Sesión iniciada</h2>
        <p>{{ usuarioSesion.NOMBRES }} {{ usuarioSesion.APELLIDOS }}</p>
        <p class="rol">{{ usuarioSesion.ROLE_ACCESO }}</p>
      </div>

      <form v-else class="formulario-login" @submit.prevent="ingresar">
        <label for="cedula">Cédula</label>
        <input
          id="cedula"
          v-model.number="cedula"
          type="number"
          min="1"
          autocomplete="username"
          placeholder="Ej.: 2222222"
          required
        />

        <label for="contrasenha">Contraseña</label>
        <input
          id="contrasenha"
          v-model="contrasenha"
          type="password"
          autocomplete="current-password"
          placeholder="Ingresá tu contraseña"
          required
        />

        <p v-if="mensajeError" class="mensaje-error" role="alert">
          {{ mensajeError }}
        </p>

        <button type="submit" :disabled="cargando">
          {{ cargando ? 'Cargando...' : 'Ingresar' }}
        </button>
        <button
          type="button"
          class="boton-secundario"
          @click="emitir('ir-registro')"
        >
          Crear una cuenta
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
/* Estos estilos ordenan el formulario y muestran claramente sus estados. */
.pagina-login {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: #f1f5f9;
}

.tarjeta-login {
  width: min(100%, 420px);
  padding: 36px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 16px 40px rgb(15 23 42 / 8%);
}

.etiqueta {
  margin-bottom: 8px;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  color: #0f172a;
  font-size: 1.8rem;
  font-weight: 700;
}

.descripcion {
  margin: 8px 0 28px;
  color: #64748b;
}

.formulario-login {
  display: grid;
  gap: 12px;
}

label {
  color: #334155;
  font-size: 0.9rem;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #0f172a;
  font: inherit;
}

input:focus {
  border-color: #2563eb;
  outline: 3px solid rgb(37 99 235 / 14%);
}

button {
  margin-top: 8px;
  padding: 12px;
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

button:hover:enabled {
  background: #1d4ed8;
}

.boton-secundario {
  margin-top: 0;
  background: #ffffff;
  color: #2563eb;
  box-shadow: inset 0 0 0 1px #bfdbfe;
}

.boton-secundario:hover:enabled {
  background: #eff6ff;
}

button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.mensaje-error {
  color: #b91c1c;
  font-size: 0.9rem;
}

.sesion-activa {
  padding: 18px;
  border-radius: 10px;
  background: #eff6ff;
  color: #1e3a8a;
}

.sesion-activa h2 {
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.rol {
  margin-top: 4px;
  color: #475569;
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .tarjeta-login {
    padding: 28px 22px;
  }
}
</style>
