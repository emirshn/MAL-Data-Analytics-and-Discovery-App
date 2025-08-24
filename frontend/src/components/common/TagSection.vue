<template>
  <div class="bg-gray-800 rounded-xl p-6">
    <h3 :class="`text-xl font-semibold mb-4 text-${color}-400`">
      {{ label }}
    </h3>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="item in items"
        :key="item"
        class="px-3 py-1 rounded-full text-white text-sm hover:opacity-90 transition-colors cursor-pointer"
        :class="colorClass"
      >
        {{ item }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  items: { type: Array, default: () => [] },
  color: { type: String, default: 'blue' },
})

const colorClass = computed(() => {
  const map = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    green: 'bg-green-600 hover:bg-green-700',
    orange: 'bg-orange-600 hover:bg-orange-700',
    indigo: 'bg-indigo-600 hover:bg-indigo-700',
    gray: 'bg-gray-600 hover:bg-gray-700',
  }
  return map[props.color] || map.blue
})
</script>
