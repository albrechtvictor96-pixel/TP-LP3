<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  iniciarRevision,
  listarSolicitudes,
  listarUsuarios,
  resolverSolicitud,
  type Solicitud,
  type Usuario,
} from '../api'
import { usuarioSesion } from '../sesion'

// Guardamos la lista y los mensajes que se muestran en la revisión.
const solicitudes = ref<Solicitud[]>([])
const usuariosPorId = ref(new Map<number, Usuario>())
const cargando = ref(true)
const idProcesando = ref<number | null>(null)
const mensajeError = ref('')
const mensajeExito = ref('')
const idRechazoAbierto = ref<number | null>(null)
const motivoRechazo = ref('')
const mensajeErrorRechazo = ref('')

// Cargamos solicitudes abiertas de todos los estudiantes.
async function actualizarSolicitudes(): Promise<void> {
  const [pendientes, enRevision] = await Promise.all([
    listarSolicitudes(undefined, 'PENDIENTE'),
    listarSolicitudes(undefined, 'EN_REVISION'),
  ])
  solicitudes.value = [...pendientes, ...enRevision].sort((a, b) =>
    b.FECHA_SOLICITUD.localeCompare(a.FECHA_SOLICITUD),
  )
}

// Permitimos el acceso únicamente a los dos roles de dirección.
onMounted(async () => {
  const rol = usuarioSesion.value?.ROLE_ACCESO
  if (rol !== 'direccion_academica' && rol !== 'direccion_carrera') {
    mensajeError.value = 'Esta pantalla es solo para los roles de dirección.'
    cargando.value = false
    return
  }

  try {
    const [usuarios] = await Promise.all([
      listarUsuarios(),
      actualizarSolicitudes(),
    ])
    usuariosPorId.value = new Map(
      usuarios.map((usuario) => [usuario.ID_USUARIO, usuario]),
    )
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudieron cargar las solicitudes.'
  } finally {
    cargando.value = false
  }
})

// Mostramos las fechas como día, mes y año.
function mostrarFecha(fecha: string | undefined): string {
  if (!fecha) return '—'
  const [anio, mes, dia] = fecha.split('-')
  return `${dia}/${mes}/${anio}`
}

// Buscamos el nombre completo del estudiante que envió la solicitud.
function obtenerEstudiante(idUsuario: number): Usuario | undefined {
  return usuariosPorId.value.get(idUsuario)
}

// Ejecutamos una acción, recargamos la lista y explicamos el resultado.
async function ejecutarAccion(
  idSolicitud: number,
  accion: () => Promise<unknown>,
  mensaje: string,
): Promise<boolean> {
  mensajeError.value = ''
  mensajeExito.value = ''
  idProcesando.value = idSolicitud

  try {
    await accion()
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudo completar la acción.'
    idProcesando.value = null
    return false
  }

  try {
    await actualizarSolicitudes()
    mensajeExito.value = mensaje
  } catch (error) {
    const detalle =
      error instanceof Error ? error.message : 'No se pudo actualizar la lista.'
    mensajeError.value = `La acción se completó, pero ${detalle.toLowerCase()}`
  } finally {
    idProcesando.value = null
  }
  return true
}

// Iniciamos la revisión usando el identificador de quien tiene la sesión.
function revisar(solicitud: Solicitud): void {
  if (!usuarioSesion.value) return
  const idUsuario = usuarioSesion.value.ID_USUARIO
  void ejecutarAccion(
    solicitud.ID_SOLICITUD_CAE,
    () => iniciarRevision(
      solicitud.ID_SOLICITUD_CAE,
      idUsuario,
    ),
    'La solicitud pasó a revisión.',
  )
}

// Abrimos el formulario y dejamos vacío el motivo de esta solicitud.
function rechazar(solicitud: Solicitud): void {
  idRechazoAbierto.value = solicitud.ID_SOLICITUD_CAE
  motivoRechazo.value = ''
  mensajeErrorRechazo.value = ''
  mensajeError.value = ''
  mensajeExito.value = ''
}

// Cerramos el formulario sin enviar nada al backend.
function cancelarRechazo(): void {
  idRechazoAbierto.value = null
  motivoRechazo.value = ''
  mensajeErrorRechazo.value = ''
}

// Validamos el motivo y lo enviamos en OBSERVACIONES al rechazar.
async function confirmarRechazo(solicitud: Solicitud): Promise<void> {
  const motivo = motivoRechazo.value.trim()
  mensajeErrorRechazo.value = ''
  if (motivo.length < 5) {
    mensajeErrorRechazo.value = 'Escribí un motivo de al menos 5 caracteres.'
    return
  }
  if (!usuarioSesion.value) {
    mensajeErrorRechazo.value = 'Iniciá sesión nuevamente para rechazar la solicitud.'
    return
  }
  const idUsuario = usuarioSesion.value.ID_USUARIO

  const completada = await ejecutarAccion(
    solicitud.ID_SOLICITUD_CAE,
    () => resolverSolicitud(
      solicitud.ID_SOLICITUD_CAE,
      idUsuario,
      { ESTADO_SOLICITUD: 'RECHAZADA', OBSERVACIONES: motivo },
    ),
    'La solicitud fue rechazada.',
  )
  if (completada) cancelarRechazo()
}

// Aprobar no requiere un motivo y conserva las observaciones que ya tenía.
function aprobar(solicitud: Solicitud): void {
  if (!usuarioSesion.value) return
  const idUsuario = usuarioSesion.value.ID_USUARIO
  void ejecutarAccion(
    solicitud.ID_SOLICITUD_CAE,
    () => resolverSolicitud(
      solicitud.ID_SOLICITUD_CAE,
      idUsuario,
      {
        ESTADO_SOLICITUD: 'APROBADA',
        OBSERVACIONES: solicitud.OBSERVACIONES,
      },
    ),
    'La solicitud fue aprobada.',
  )
}
</script>

<template>
  <main class="pagina-revision">
    <section class="contenido-revision">
      <header class="encabezado">
        <div>
          <p class="etiqueta">Sistema CAE</p>
          <h1>Revisión de solicitudes</h1>
          <p class="descripcion">
            Revisá las solicitudes pendientes y las que están en revisión.
          </p>
        </div>
      </header>

      <p v-if="cargando" class="aviso" role="status">Cargando...</p>
      <p v-if="mensajeError" class="mensaje-error" role="alert">
        {{ mensajeError }}
      </p>
      <p v-if="mensajeExito" class="mensaje-exito" role="status">
        {{ mensajeExito }}
      </p>

      <p v-if="!cargando && !mensajeError && solicitudes.length === 0" class="aviso">
        No hay solicitudes pendientes de revisión.
      </p>

      <section
        v-for="solicitud in solicitudes"
        :key="solicitud.ID_SOLICITUD_CAE"
        class="tarjeta-solicitud"
      >
        <div class="encabezado-tarjeta">
          <h2>{{ solicitud.detalles[0]?.ACTIVIDAD || 'Actividad sin detalle' }}</h2>
          <span class="estado" :class="solicitud.ESTADO_SOLICITUD.toLowerCase()">
            {{ solicitud.ESTADO_SOLICITUD === 'EN_REVISION' ? 'En revisión' : 'Pendiente' }}
          </span>
        </div>

        <p class="identificador">
          Solicitud #{{ solicitud.ID_SOLICITUD_CAE }}
        </p>
        <p class="identificador">
          <template v-if="obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)">
            Estudiante:
            {{ obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)?.NOMBRES }}
            {{ obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)?.APELLIDOS }}
          </template>
          <template v-else>
            Estudiante #{{ solicitud.ID_USUARIO_SOLICITA }} (no encontrado)
          </template>
        </p>
        <p
          v-if="obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)"
          class="datos-estudiante"
        >
          Cédula: {{ obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)?.NRO_CEDULA }}
          · Carrera: {{ obtenerEstudiante(solicitud.ID_USUARIO_SOLICITA)?.CARRERA }}
        </p>

        <dl class="datos-solicitud">
          <div>
            <dt>Fecha de solicitud</dt>
            <dd>{{ mostrarFecha(solicitud.FECHA_SOLICITUD) }}</dd>
          </div>
          <div>
            <dt>Fecha de actividad</dt>
            <dd>{{ mostrarFecha(solicitud.detalles[0]?.FECHA_ACTIVIDAD) }}</dd>
          </div>
          <div>
            <dt>Carga horaria</dt>
            <dd>
              {{ solicitud.detalles[0]?.CARGA_HORARIA_EN_MINUTOS ?? '—' }}
              <span v-if="solicitud.detalles[0]">minutos</span>
            </dd>
          </div>
          <div>
            <dt>Créditos estimados</dt>
            <dd>{{ solicitud.CREDITOS_CALCULADOS.toFixed(1) }}</dd>
          </div>
          <div>
            <dt>Supervisor</dt>
            <dd>{{ solicitud.detalles[0]?.SUPERVISADO || '—' }}</dd>
          </div>
        </dl>

        <p class="observaciones">
          <strong>Observaciones:</strong>
          {{ solicitud.OBSERVACIONES || 'Sin observaciones.' }}
        </p>

        <div class="acciones">
          <button
            v-if="solicitud.ESTADO_SOLICITUD === 'PENDIENTE'"
            class="boton-secundario"
            type="button"
            :disabled="idProcesando !== null"
            @click="revisar(solicitud)"
          >
            {{ idProcesando === solicitud.ID_SOLICITUD_CAE ? 'Procesando...' : 'Iniciar revisión' }}
          </button>
          <button
            class="boton-aprobar"
            type="button"
            :disabled="idProcesando !== null"
            @click="aprobar(solicitud)"
          >
            Aprobar
          </button>
          <button
            class="boton-rechazar"
            type="button"
            :disabled="idProcesando !== null"
            @click="rechazar(solicitud)"
          >
            Rechazar
          </button>
        </div>

        <form
          v-if="idRechazoAbierto === solicitud.ID_SOLICITUD_CAE"
          class="formulario-rechazo"
          @submit.prevent="confirmarRechazo(solicitud)"
        >
          <label :for="`motivo-${solicitud.ID_SOLICITUD_CAE}`">
            Motivo del rechazo
          </label>
          <textarea
            :id="`motivo-${solicitud.ID_SOLICITUD_CAE}`"
            v-model="motivoRechazo"
            rows="3"
            :disabled="idProcesando !== null"
            placeholder="Explicá por qué se rechaza la solicitud"
          />
          <p v-if="mensajeErrorRechazo" class="error-formulario" role="alert">
            {{ mensajeErrorRechazo }}
          </p>
          <div class="acciones">
            <button
              class="boton-rechazar"
              type="submit"
              :disabled="idProcesando !== null"
            >
              {{ idProcesando === solicitud.ID_SOLICITUD_CAE ? 'Enviando...' : 'Confirmar rechazo' }}
            </button>
            <button
              class="boton-cancelar"
              type="button"
              :disabled="idProcesando !== null"
              @click="cancelarRechazo"
            >
              Cancelar
            </button>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

<style scoped>
/* Mantenemos el mismo fondo y las tarjetas simples del resto del frontend. */
.pagina-revision {
  min-height: 100vh;
  padding: 40px 24px;
  background: #f1f5f9;
}

.contenido-revision {
  width: min(100%, 900px);
  margin: 0 auto;
}

.encabezado {
  margin-bottom: 24px;
}

.etiqueta {
  margin-bottom: 6px;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1,
h2 {
  color: #0f172a;
}

h1 {
  font-size: 1.8rem;
}

h2 {
  font-size: 1.2rem;
}

.descripcion,
.identificador {
  color: #64748b;
}

.datos-estudiante {
  color: #64748b;
  font-size: 0.85rem;
}

.tarjeta-solicitud {
  margin-bottom: 16px;
  padding: 22px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgb(15 23 42 / 5%);
}

.encabezado-tarjeta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.identificador {
  margin-top: 5px;
  font-size: 0.9rem;
}

.datos-solicitud {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 14px;
  margin: 20px 0;
}

dt {
  color: #64748b;
  font-size: 0.82rem;
}

dd {
  color: #334155;
  font-weight: 600;
}

.observaciones {
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
}

.acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.formulario-rechazo {
  display: grid;
  gap: 10px;
  margin-top: 18px;
  padding: 16px;
  border-radius: 8px;
  background: #fff7ed;
}

.formulario-rechazo label {
  color: #334155;
  font-weight: 600;
}

.formulario-rechazo textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #0f172a;
  font: inherit;
  resize: vertical;
}

.formulario-rechazo textarea:focus {
  border-color: #ea580c;
  outline: 3px solid rgb(234 88 12 / 14%);
}

.error-formulario {
  color: #b91c1c;
  font-size: 0.9rem;
}

.estado {
  display: inline-block;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.estado.pendiente {
  background: #fef3c7;
  color: #92400e;
}

.estado.en_revision {
  background: #dbeafe;
  color: #1e40af;
}

button {
  padding: 10px 14px;
  border: 0;
  border-radius: 8px;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.boton-secundario {
  background: #475569;
}

.boton-aprobar {
  background: #16a34a;
}

.boton-rechazar {
  background: #dc2626;
}

.boton-cancelar {
  background: #64748b;
}

.aviso,
.mensaje-error,
.mensaje-exito {
  margin-bottom: 16px;
  padding: 14px;
  border-radius: 8px;
}

.aviso {
  background: #ffffff;
  color: #475569;
}

.mensaje-error {
  background: #fee2e2;
  color: #991b1b;
}

.mensaje-exito {
  background: #dcfce7;
  color: #166534;
}

@media (max-width: 600px) {
  .pagina-revision {
    padding: 24px 14px;
  }
}
</style>
