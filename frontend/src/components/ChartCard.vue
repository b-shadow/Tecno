<script setup>
defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'total' },
})
</script>

<template>
  <section class="table-surface">
    <div class="table-header">
      <div>
        <p class="eyebrow">Grafico</p>
        <h2>{{ title }}</h2>
      </div>
    </div>
    <div class="bar-list">
      <article v-for="item in items" :key="item[labelKey] || item.id" class="bar-item">
        <div>
          <strong>{{ item[labelKey] }}</strong>
          <span>{{ item[valueKey] }}</span>
        </div>
        <meter min="0" :max="Math.max(...items.map((entry) => Number(entry[valueKey] || 0)), 1)" :value="Number(item[valueKey] || 0)" />
      </article>
      <p v-if="items.length === 0" class="muted">Sin datos registrados.</p>
    </div>
  </section>
</template>
