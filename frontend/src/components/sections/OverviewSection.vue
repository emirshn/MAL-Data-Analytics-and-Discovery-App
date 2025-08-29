<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">📈 Overview Dashboard</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-6">
      <div
        v-for="(card, index) in cards"
        :key="index"
        class="flex flex-col items-center gap-4 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 transition transform hover:-translate-y-2 hover:shadow-2xl hover:border-indigo-500/40"
      >
        <div class="text-3xl">{{ card.icon }}</div>
        <div class="text-center">
          <h3 class="text-sm text-slate-400 font-medium mb-1">{{ card.title }}</h3>
          <div class="text-xl font-extrabold mb-1">{{ animatedValues[card.key] || 0 }}</div>
          <p class="text-xs text-slate-500">{{ card.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'OverviewDashboard',
  props: {
    cards: { type: Array, required: true },
    animatedValues: { type: Object, required: true },
  },
}
</script>

<style scoped>
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

.bg-white\/5:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

@media (max-width: 640px) {
  .text-6xl {
    font-size: 2.5rem;
  }

  .text-3xl {
    font-size: 1.5rem;
  }
}

canvas {
  max-width: 100%;
  height: auto !important;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.bg-gradient-to-r {
  background-size: 200% 200%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

* {
  transition: all 0.2s ease;
}

.hover\:shadow-2xl:hover {
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(99, 102, 241, 0.1);
}

.backdrop-blur-lg {
  backdrop-filter: blur(16px) saturate(180%);
}
</style>
