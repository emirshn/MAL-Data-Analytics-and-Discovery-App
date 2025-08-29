<template>
  <BaseChart
    title="Top Serializations"
    icon="📚"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TopSerializationsChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      chartColors: [
        '#3b82f6',
        '#22c55e',
        '#f97316',
        '#eab308',
        '#ec4899',
        '#06b6d4',
        '#a855f7',
        '#ef4444',
        '#10b981',
        '#f59e0b',
      ], // bright palette
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.creators?.top_serializations || {}
      const sortedSeries = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)

      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: sortedSeries.map(([series]) => series),
          datasets: [
            {
              data: sortedSeries.map(([, count]) => count),
              backgroundColor: this.chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: 'rgb(148, 163, 184)',
              },
            },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    },
  },
  watch: {
    stats: {
      deep: true,
      handler() {
        this.createChart()
      },
    },
  },
  beforeUnmount() {
    if (this.chartInstance) this.chartInstance.destroy()
  },
}
</script>
