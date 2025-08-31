<template>
  <div
    class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    :class="containerClass"
  >
    <h3 class="text-lg font-semibold text-center mb-6">{{ icon }} {{ title }}</h3>
    <canvas ref="chartCanvas" :class="canvasClass"></canvas>
  </div>
</template>

<script>
export default {
  name: 'BaseChart',
  props: {
    title: String,
    icon: String,
    containerClass: { type: String, default: '' },
    canvasClass: { type: String, default: 'max-h-80' },
  },
  mounted() {
    this.$emit('canvas-ready', this.$refs.chartCanvas)
  },
}
</script>
<style scoped>
.bg-white\/5:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

canvas {
  max-width: 100%;
  height: auto !important;
}

.backdrop-blur-lg {
  backdrop-filter: blur(16px) saturate(180%);
}
</style>
