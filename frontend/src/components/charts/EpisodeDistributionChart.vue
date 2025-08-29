<template>
  <BaseChart
    title="Episode Distribution"
    icon="⏱️"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'EpisodeDistributionChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: { accent: '#3b82f6' },
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.content_length?.episode_distribution || {}
      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Anime Count',
              data: Object.values(data),
              backgroundColor: this.colors.accent + '80',
              borderColor: this.colors.accent,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#374151' } },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
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
