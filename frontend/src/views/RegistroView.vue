<script setup lang="ts">
import { ref } from 'vue'
import { registrarUsuario } from '../api'

// Avisamos a la aplicación cuando se elige volver a Login.
const emitir = defineEmits<{ (evento: 'ir-login'): void }>()

// Estos campos corresponden a los datos que requiere el endpoint de registro.
const cedula = ref<number | null>(null)
const nombres = ref('')
const apellidos = ref('')
const matricula = ref('')
const email = ref('')
const telefono = ref('')
const contrasenha = ref('')
const repetirContrasenha = ref('')
const mostrarContrasenha = ref(false)
const carrera = ref('')
const cargando = ref(false)
const mensajeError = ref('')
const cuentaCreada = ref(false)

// Enviamos la nueva cuenta y mostramos el resultado del backend.
async function registrar(): Promise<void> {
  mensajeError.value = ''

  if (!cedula.value || cedula.value <= 0) {
    mensajeError.value = 'Ingresá una cédula válida.'
    return
  }

  // Comprobamos la contraseña antes de enviar el registro al servidor.
  if (contrasenha.value.length < 6) {
    mensajeError.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }
  if (contrasenha.value !== repetirContrasenha.value) {
    mensajeError.value = 'Las contraseñas no coinciden.'
    return
  }

  cargando.value = true
  try {
    await registrarUsuario({
      NRO_CEDULA: cedula.value,
      NOMBRES: nombres.value,
      APELLIDOS: apellidos.value,
      CODIGO_MATRICULA: matricula.value,
      EMAIL: email.value,
      TELEFONO_CELULAR: telefono.value,
      CONTRASENHA: contrasenha.value,
      CARRERA: carrera.value,
    })
    contrasenha.value = ''
    cuentaCreada.value = true
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudo crear la cuenta.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <main class="pagina-registro">
    <section class="tarjeta-registro">
      <p class="etiqueta">Sistema CAE</p>
      <h1>Crear cuenta de estudiante</h1>
      <p class="descripcion">
        Completá tus datos para registrarte en el sistema.
      </p>

      <div v-if="cuentaCreada" class="mensaje-exito" role="status">
        <h2>Cuenta creada</h2>
        <p>Ya podés iniciar sesión con tu cédula y contraseña.</p>
        <button type="button" @click="emitir('ir-login')">
          Volver al inicio de sesión
        </button>
      </div>

      <form v-else class="formulario-registro" @submit.prevent="registrar">
        <label for="registro-cedula">Cédula</label>
        <input
          id="registro-cedula"
          v-model.number="cedula"
          type="number"
          min="1"
          autocomplete="off"
          required
        />

        <label for="nombres">Nombres</label>
        <input id="nombres" v-model.trim="nombres" autocomplete="given-name" required />

        <label for="apellidos">Apellidos</label>
        <input id="apellidos" v-model.trim="apellidos" autocomplete="family-name" required />

        <label for="matricula">Código de matrícula</label>
        <input id="matricula" v-model.trim="matricula" required />

        <label for="email">Correo electrónico</label>
        <input id="email" v-model.trim="email" type="email" autocomplete="email" required />

        <label for="telefono">Teléfono celular</label>
        <input id="telefono" v-model.trim="telefono" type="tel" autocomplete="tel" required />

        <label for="registro-contrasenha">Contraseña</label>
        <input
          id="registro-contrasenha"
          v-model="contrasenha"
          :type="mostrarContrasenha ? 'text' : 'password'"
          autocomplete="off"
          required
        />

        <label for="repetir-contrasenha">Repetir contraseña</label>
        <input
          id="repetir-contrasenha"
          v-model="repetirContrasenha"
          :type="mostrarContrasenha ? 'text' : 'password'"
          autocomplete="off"
          required
        />
        <button
          type="button"
          class="boton-secundario"
          @click="mostrarContrasenha = !mostrarContrasenha"
        >
          {{ mostrarContrasenha ? 'Ocultar contraseña' : 'Mostrar contraseña' }}
        </button>

        <label for="carrera">Carrera</label>
        <input id="carrera" v-model.trim="carrera" required />

        <p v-if="mensajeError" class="mensaje-error" role="alert">
          {{ mensajeError }}
        </p>

        <button type="submit" :disabled="cargando">
          {{ cargando ? 'Cargando...' : 'Registrarme' }}
        </button>
        <button
          type="button"
          class="boton-secundario"
          @click="emitir('ir-login')"
        >
          Volver al inicio de sesión
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
/* Ordenamos los campos para que el registro sea fácil de completar. */
.pagina-registro {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: #f1f5f9;
}

.tarjeta-registro {
  width: min(100%, 520px);
  margin: 24px 0;
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
  font-size: 1.7rem;
  font-weight: 700;
}

.descripcion {
  margin: 8px 0 24px;
  color: #64748b;
}

.formulario-registro {
  display: grid;
  gap: 10px;
}

label {
  color: #334155;
  font-size: 0.9rem;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 11px 14px;
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

.mensaje-exito {
  padding: 18px;
  border-radius: 10px;
  background: #f0fdf4;
  color: #166534;
}

.mensaje-exito h2 {
  margin-bottom: 6px;
  font-size: 1.1rem;
}

@media (max-width: 480px) {
  .tarjeta-registro {
    padding: 28px 22px;
  }
}
</style>
