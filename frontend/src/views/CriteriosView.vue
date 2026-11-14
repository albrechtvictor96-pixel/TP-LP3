<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listarCriterios, type CriterioCAE } from '../api'

// Guardamos las reglas recibidas y los mensajes de la carga.
const criterios = ref<CriterioCAE[]>([])
const cargando = ref(true)
const mensajeError = ref('')

// Cargamos los criterios vigentes desde el backend.
onMounted(async () => {
  try {
    criterios.value = await listarCriterios()
  } catch (error) {
    mensajeError.value =
      error instanceof Error ? error.message : 'No se pudieron cargar los criterios.'
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="pagina-criterios">
    <section class="contenido-criterios">
      <p class="etiqueta">Sistema CAE</p>
      <h1>Criterios de créditos</h1>
      <p class="descripcion">
        Las horas se convierten en créditos según la categoría de cada actividad.
      </p>

      <p class="meta">Meta total: 20 créditos.</p>
      <p class="referencia">Resolución 33/2020 de la UC, Campus Guairá.</p>

      <p v-if="cargando" class="aviso" role="status">Cargando criterios...</p>
      <p v-else-if="mensajeError" class="mensaje-error" role="alert">
        {{ mensajeError }}
      </p>
      <div v-else class="tabla-contenedor">
        <table>
          <thead>
            <tr>
              <th>Categoría</th>
              <th>Horas por crédito</th>
              <th>Máximo de créditos</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="criterio in criterios" :key="criterio.ID_ACTIVIDAD">
              <td>{{ criterio.NOMBRE_ACTIVIDAD }}</td>
              <td>{{ criterio.HORAS_POR_CREDITO }} horas</td>
              <td>{{ criterio.MAXIMO_CREDITOS }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* Usamos el fondo y las tarjetas simples del resto de las pantallas. */
.pagina-criterios {
  min-height: 100vh;
  padding: 40px 24px;
  background: #f1f5f9;
}

.contenido-criterios {
  width: min(100%, 900px);
  margin: 0 auto;
  padding: 28px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgb(15 23 42 / 5%);
}

.etiqueta {
  margin-bottom: 6px;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  color: #0f172a;
  font-size: 1.8rem;
}

.descripcion {
  margin: 8px 0 18px;
  color: #64748b;
}

.meta {
  color: #1e3a8a;
  font-weight: 700;
}

.referencia {
  margin-bottom: 20px;
  color: #475569;
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
}

th {
  color: #475569;
  font-size: 0.9rem;
}

td {
  color: #334155;
}

.aviso,
.mensaje-error {
  padding: 14px;
  border-radius: 8px;
}

.aviso {
  background: #f8fafc;
  color: #475569;
}

.mensaje-error {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 600px) {
  .pagina-criterios {
    padding: 24px 14px;
  }

  .contenido-criterios {
    padding: 18px;
  }
}
</style>
