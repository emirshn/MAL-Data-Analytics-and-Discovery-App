<template>
  <div class="chart-card">
    <h3 class="text-lg font-semibold text-center mb-6">{{ icon }} {{ title }}</h3>
    <div class="space-y-3 max-h-96 overflow-y-auto">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="flex justify-between items-center p-3 bg-white/5 rounded-lg"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ item.title }}</p>
          <p class="text-xs text-slate-400">
            <slot name="subtitle" :item="item" />
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm font-bold" :class="valueClass">{{ formatValue(item[valueKey]) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseList',
  props: {
    title: { type: String, required: true },
    icon: { type: String, default: '' },
    items: { type: Array, default: () => [] },
    valueKey: { type: String, required: true },
    valueClass: { type: String, default: 'text-indigo-400' },
  },
  methods: {
    formatValue(val) {
      return typeof val === 'number' ? val.toLocaleString() : val
    },
  },
}
</script>

<style scoped>
.chart-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.chart-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.max-h-96::-webkit-scrollbar {
  width: 4px;
}

.max-h-96::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.max-h-96::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.6);
  border-radius: 4px;
}

.max-h-96::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.8);
}
</style>
