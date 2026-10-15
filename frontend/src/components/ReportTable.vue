<script setup>
defineProps({
  title: { type: String, required: true },
  eyebrow: { type: String, default: 'Reporte' },
  rows: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
})
</script>

<template>
  <section class="table-surface">
    <div class="table-header">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in rows" :key="row.id || index">
            <td v-for="column in columns" :key="column.key">
              {{ column.format ? column.format(row) : row[column.key] }}
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td :colspan="columns.length">Sin datos registrados.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
