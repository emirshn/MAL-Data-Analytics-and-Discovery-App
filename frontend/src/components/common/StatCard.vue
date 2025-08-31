<template>
  <div :class="`bg-${color}-600 bg-opacity-20 p-3 rounded-lg text-center`">
    <div :class="`text-${color}-400 text-2xl font-bold`">
      <slot name="icon"></slot>
      {{ value }}
    </div>
    <div class="text-xs text-gray-400">{{ label }}</div>
  </div>
</template>

<script setup>
defineProps({
  value: {
    type: [String, Number],
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    default: 'blue',
  },
})
</script>
