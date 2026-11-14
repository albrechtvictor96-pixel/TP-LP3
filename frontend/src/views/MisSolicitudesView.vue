<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  listarSolicitudes,
  obtenerProgreso,
  type Progreso,
  type Solicitud,
} from '../api'
import { usuarioSesion } from '../sesion'

// Guardamos la lista, el progreso y los mensajes que se muestran en pantalla.
const solicitudes = ref<Solicitud[]>([])
const progreso = ref<Progreso | null>(null)
const cargando = ref(true)
const mensajeError = ref('')

// Cargamos las solicitudes y el progreso usando el identificador de la sesión.
onMounted(async () => {
  if (!usuarioSesion.value || usuarioSesion.value.ROLE_ACCESO !== 'estudiante') {
    mensajeError.value = 'Esta pantalla es solo para estudiantes con sesión iniciada.'
    cargando.value = false
    return
  }

  try {
    const idUsuario = usuarioSesion.value.ID_USUARIO
    const [lista, resumen] = await Promise.all([
      listarSolicitudes(idUsuario),
      obtenerProgreso(idUsuario),
    ])
    solicitudes.value = lista
    progreso.value = resumen
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudieron cargar tus datos.'
  } finally {
    cargando.value = false
  }
})

// Mostramos las fechas como día, mes y año sin cambiar el valor recibido.
function mostrarFecha(fecha: string | undefined): string {
  if (!fecha) return '—'
  const [anio, mes, dia] = fecha.split('-')
  return `${dia}/${mes}/${anio}`
}

// Reemplazamos los nombres técnicos por etiquetas fáciles de leer.
function nombreEstado(estado: string): string {
  const nombres: Record<string, string> = {
    PENDIENTE: 'Pendiente',
    EN_REVISION: 'En revisión',
    APROBADA: 'Aprobada',
    RECHAZADA: 'Rechazada',
  }
  return nombres[estado] || estado
}
</script>

<template>
  <main class="pagina-solicitudes">
    <section class="contenido-solicitudes">
      <header class="encabezado">
        <div>
          <p class="etiqueta">Sistema CAE</p>
          <h1>Mis solicitudes</h1>
          <p class="descripcion">
            Consultá el estado de tus actividades y tu progreso de créditos.
          </p>
        </div>
        <RouterLink class="boton-volver" to="/nueva-solicitud">
          Nueva solicitud
        </RouterLink>
      </header>

      <p v-if="cargando" class="aviso" role="status">Cargando...</p>
      <p v-else-if="mensajeError" class="mensaje-error" role="alert">
        {{ mensajeError }}
      </p>

      <template v-else-if="progreso">
        <section class="tarjeta-progreso" aria-labelledby="titulo-progreso">
          <div class="resumen-progreso">
            <div>
              <h2 id="titulo-progreso">Tu progreso</h2>
              <p class="creditos">
                {{ progreso.CREDITOS_APROBADOS }} de {{ progreso.META_CREDITOS }} créditos aprobados
              </p>
            </div>
            <strong>{{ Math.round(progreso.PORCENTAJE_COMPLETADO) }}%</strong>
          </div>

          <div
            class="barra-progreso"
            role="progressbar"
            :aria-valuenow="Math.round(progreso.PORCENTAJE_COMPLETADO)"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-label="Porcentaje de créditos completados"
          >
            <span :style="{ width: `${progreso.PORCENTAJE_COMPLETADO}%` }" />
          </div>

          <p v-if="progreso.META_CUMPLIDA" class="felicitacion">
            ¡Felicitaciones! Ya cumpliste la meta de créditos.
          </p>
          <p v-else class="faltantes">
            Te faltan {{ progreso.CREDITOS_FALTANTES }} créditos para cumplir la meta.
          </p>

          <ul class="conteo-estados" aria-label="Solicitudes por estado">
            <li><span class="punto pendiente" />Pendientes: {{ progreso.CANTIDAD_PENDIENTE }}</li>
            <li><span class="punto revision" />En revisión: {{ progreso.CANTIDAD_EN_REVISION }}</li>
            <li><span class="punto aprobada" />Aprobadas: {{ progreso.CANTIDAD_APROBADA }}</li>
            <li><span class="punto rechazada" />Rechazadas: {{ progreso.CANTIDAD_RECHAZADA }}</li>
          </ul>
        </section>

        <section class="tarjeta-lista" aria-labelledby="titulo-categorias">
          <h2 id="titulo-categorias">Créditos por categoría</h2>
          <div class="tabla-contenedor">
            <table>
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Créditos obtenidos</th>
                  <th>Máximo permitido</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="categoria in progreso.CREDITOS_POR_CATEGORIA"
                  :key="categoria.ID_ACTIVIDAD"
                >
                  <td>{{ categoria.NOMBRE_ACTIVIDAD }}</td>
                  <td>{{ categoria.CREDITOS_OBTENIDOS.toFixed(1) }}</td>
                  <td>{{ categoria.MAXIMO_CREDITOS }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="tarjeta-lista" aria-labelledby="titulo-lista">
          <h2 id="titulo-lista">Historial de solicitudes</h2>
          <p v-if="solicitudes.length === 0" class="sin-solicitudes">
            Todavía no tenés solicitudes.
          </p>
          <div v-else class="tabla-contenedor">
            <table>
              <thead>
                <tr>
                  <th>Fecha de solicitud</th>
                  <th>Actividad</th>
                  <th>Fecha de actividad</th>
                  <th>Carga horaria</th>
                  <th>Créditos</th>
                  <th>Estado</th>
                  <th>Observaciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="solicitud in solicitudes" :key="solicitud.ID_SOLICITUD_CAE">
                  <td>{{ mostrarFecha(solicitud.FECHA_SOLICITUD) }}</td>
                  <td>{{ solicitud.detalles[0]?.ACTIVIDAD || '—' }}</td>
                  <td>{{ mostrarFecha(solicitud.detalles[0]?.FECHA_ACTIVIDAD) }}</td>
                  <td>
                    {{ solicitud.detalles[0]?.CARGA_HORARIA_EN_MINUTOS ?? '—' }}
                    <span v-if="solicitud.detalles[0]">minutos</span>
                  </td>
                  <td>{{ solicitud.CREDITOS_CALCULADOS.toFixed(1) }}</td>
                  <td>
                    <span class="estado" :class="solicitud.ESTADO_SOLICITUD.toLowerCase()">
                      {{ nombreEstado(solicitud.ESTADO_SOLICITUD) }}
                    </span>
                  </td>
                  <td>{{ solicitud.OBSERVACIONES || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </section>
  </main>
</template>

<style scoped>
/* Usamos tarjetas y colores simples para separar el resumen del historial. */
.pagina-solicitudes {
  min-height: 100vh;
  padding: 40px 24px;
  background: #f1f5f9;
}

.contenido-solicitudes {
  width: min(100%, 1100px);
  margin: 0 auto;
}

.encabezado,
.resumen-progreso {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
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
.faltantes {
  color: #64748b;
}

.tarjeta-progreso,
.tarjeta-lista {
  margin-bottom: 20px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgb(15 23 42 / 5%);
}

.creditos {
  margin-top: 4px;
  color: #475569;
}

.resumen-progreso strong {
  color: #2563eb;
  font-size: 1.5rem;
}

.barra-progreso {
  height: 12px;
  margin: 18px 0 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.barra-progreso span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #2563eb;
  transition: width 0.3s ease;
}

.felicitacion {
  color: #166534;
  font-weight: 700;
}

.conteo-estados {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  margin-top: 18px;
  padding: 0;
  color: #334155;
  list-style: none;
}

.conteo-estados li {
  display: flex;
  align-items: center;
  gap: 7px;
}

.punto {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.punto.pendiente { background: #d97706; }
.punto.revision { background: #2563eb; }
.punto.aprobada { background: #16a34a; }
.punto.rechazada { background: #dc2626; }

.tarjeta-lista h2 {
  margin-bottom: 16px;
}

.sin-solicitudes,
.aviso {
  padding: 18px;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  text-align: center;
}

.tabla-contenedor {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

th {
  color: #475569;
  font-size: 0.85rem;
}

td {
  color: #334155;
}

.estado {
  display: inline-block;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.estado.pendiente { background: #fef3c7; color: #92400e; }
.estado.en_revision { background: #dbeafe; color: #1e40af; }
.estado.aprobada { background: #dcfce7; color: #166534; }
.estado.rechazada { background: #fee2e2; color: #991b1b; }

.boton-volver {
  display: inline-block;
  padding: 10px 14px;
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
}

.boton-volver:hover {
  background: #1d4ed8;
}

.mensaje-error {
  color: #b91c1c;
}

@media (max-width: 600px) {
  .pagina-solicitudes {
    padding: 24px 14px;
  }

  .encabezado {
    align-items: flex-start;
    flex-direction: column;
  }

  .tarjeta-progreso,
  .tarjeta-lista {
    padding: 18px;
  }
}
</style>
