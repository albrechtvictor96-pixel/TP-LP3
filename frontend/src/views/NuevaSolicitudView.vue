<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { crearSolicitud, listarActividades, type Actividad } from '../api'
import { usuarioSesion } from '../sesion'

// Avisamos a la aplicación cuando la persona quiere ver sus solicitudes.
const emitir = defineEmits<{
  (evento: 'ir-mis-solicitudes'): void
}>()

// Estas referencias guardan las actividades y lo que se escribe en el formulario.
const actividades = ref<Actividad[]>([])
const idActividad = ref<number | null>(null)
const fechaActividad = ref('')
const cargaHoraria = ref<number | null>(null)
const supervisor = ref('')
const observaciones = ref('')
const cargandoActividades = ref(true)
const enviando = ref(false)
const mensajeError = ref('')
const mensajeExito = ref('')

// Las horas por crédito siguen las categorías definidas en el reglamento.
const HORAS_POR_CREDITO: Record<number, number> = {
  1: 16,
  2: 16,
  3: 16,
  4: 16,
  5: 48,
  6: 32,
  7: 32,
  8: 32,
}

// Evitamos que el formulario permita elegir una fecha futura.
const fechaMaxima = computed(() => new Date().toISOString().slice(0, 10))
const horasPorCredito = computed(() =>
  idActividad.value === null ? null : HORAS_POR_CREDITO[idActividad.value] ?? null,
)
const creditosEstimados = computed(() => {
  if (horasPorCredito.value === null || cargaHoraria.value === null) return 0
  const decimos = Math.trunc(
    (cargaHoraria.value * 10) / (60 * horasPorCredito.value),
  )
  return decimos / 10
})

// Cargamos del backend las actividades que pueden elegirse.
onMounted(async () => {
  try {
    actividades.value = (await listarActividades()).filter(
      (actividad) => actividad.ACTIVO === 1,
    )
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudieron cargar las actividades.'
  } finally {
    cargandoActividades.value = false
  }
})

// Validamos los datos obligatorios y enviamos la solicitud para el usuario conectado.
async function enviarSolicitud(): Promise<void> {
  mensajeError.value = ''
  mensajeExito.value = ''

  if (!usuarioSesion.value) {
    mensajeError.value = 'Iniciá sesión antes de enviar una solicitud.'
    return
  }
  if (!idActividad.value || !fechaActividad.value || !cargaHoraria.value) {
    mensajeError.value = 'Completá la actividad, la fecha y la carga horaria.'
    return
  }
  if (cargaHoraria.value <= 0) {
    mensajeError.value = 'La carga horaria debe ser mayor a cero.'
    return
  }
  if (fechaActividad.value > fechaMaxima.value) {
    mensajeError.value = 'La fecha de la actividad no puede ser futura.'
    return
  }

  enviando.value = true
  try {
    await crearSolicitud({
      ID_ACTIVIDAD: idActividad.value,
      ID_USUARIO_SOLICITA: usuarioSesion.value.ID_USUARIO,
      FECHA_ACTIVIDAD: fechaActividad.value,
      CARGA_HORARIA_EN_MINUTOS: cargaHoraria.value,
      SUPERVISADO: supervisor.value.trim() || null,
      OBSERVACIONES: observaciones.value.trim() || null,
    })
    mensajeExito.value = 'La solicitud se guardó correctamente y quedó pendiente.'
    idActividad.value = null
    fechaActividad.value = ''
    cargaHoraria.value = null
    supervisor.value = ''
    observaciones.value = ''
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudo guardar la solicitud.'
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main class="pagina-solicitud">
    <section class="tarjeta-solicitud">
      <p class="etiqueta">Sistema CAE</p>
      <h1>Nueva solicitud</h1>
      <p class="descripcion">
        Completá los datos de la actividad que realizaste.
      </p>

      <p v-if="usuarioSesion" class="estudiante">
        Estudiante: {{ usuarioSesion.NOMBRES }} {{ usuarioSesion.APELLIDOS }}
      </p>

      <button
        v-if="usuarioSesion?.ROLE_ACCESO === 'estudiante'"
        class="boton-secundario"
        type="button"
        @click="emitir('ir-mis-solicitudes')"
      >
        Ver mis solicitudes
      </button>

      <p v-if="cargandoActividades" class="estado" role="status">Cargando actividades...</p>

      <form v-else class="formulario-solicitud" @submit.prevent="enviarSolicitud">
        <label for="actividad">Actividad</label>
        <select id="actividad" v-model.number="idActividad" required>
          <option :value="null" disabled>Seleccioná una actividad</option>
          <option
            v-for="actividad in actividades"
            :key="actividad.ID_ACTIVIDAD"
            :value="actividad.ID_ACTIVIDAD"
          >
            {{ actividad.NOMBRE_ACTIVIDAD }}
          </option>
        </select>

        <label for="fecha-actividad">Fecha de la actividad</label>
        <input
          id="fecha-actividad"
          v-model="fechaActividad"
          type="date"
          :max="fechaMaxima"
          required
        />

        <label for="carga-horaria">Carga horaria en minutos</label>
        <input
          id="carga-horaria"
          v-model.number="cargaHoraria"
          type="number"
          min="1"
          placeholder="Ej.: 60"
          required
        />

        <p
          v-if="horasPorCredito && cargaHoraria"
          class="estimacion-creditos"
          role="status"
        >
          Equivale a {{ creditosEstimados.toFixed(1) }} créditos
          (1 crédito = {{ horasPorCredito }} horas).
        </p>
        <p
          v-else-if="idActividad === 9 && cargaHoraria"
          class="estimacion-creditos"
          role="status"
        >
          Esta actividad todavía no tiene una regla de créditos.
        </p>

        <label for="supervisor">Supervisor (opcional)</label>
        <input
          id="supervisor"
          v-model.trim="supervisor"
          type="text"
          placeholder="Nombre del supervisor"
        />

        <label for="observaciones">Observaciones (opcional)</label>
        <textarea
          id="observaciones"
          v-model.trim="observaciones"
          rows="3"
          placeholder="Agregá información adicional"
        />

        <p v-if="mensajeError" class="mensaje-error" role="alert">
          {{ mensajeError }}
        </p>
        <p v-if="mensajeExito" class="mensaje-exito" role="status">
          {{ mensajeExito }}
        </p>

        <button type="submit" :disabled="enviando || actividades.length === 0">
          {{ enviando ? 'Cargando...' : 'Enviar solicitud' }}
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
/* Presentamos el formulario en una tarjeta simple y fácil de recorrer. */
.pagina-solicitud {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: #f1f5f9;
}

.tarjeta-solicitud {
  width: min(100%, 520px);
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
  margin: 8px 0 20px;
  color: #64748b;
}

.estudiante {
  margin-bottom: 18px;
  color: #334155;
  font-weight: 600;
}

.estimacion-creditos {
  color: #1e3a8a;
  font-size: 0.9rem;
  font-weight: 600;
}

.formulario-solicitud {
  display: grid;
  gap: 10px;
}

label {
  color: #334155;
  font-size: 0.9rem;
  font-weight: 600;
}

input,
select,
textarea {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #0f172a;
  font: inherit;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #2563eb;
  outline: 3px solid rgb(37 99 235 / 14%);
}

textarea {
  resize: vertical;
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
  margin: 0 0 18px;
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
  color: #166534;
  font-size: 0.95rem;
}

.estado {
  color: #475569;
}

@media (max-width: 480px) {
  .tarjeta-solicitud {
    padding: 28px 22px;
  }
}
</style>
