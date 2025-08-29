<template>
  <BaseChart
    title="Members Distribution"
    icon="👥"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'MembersDistributionChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: { cyan: '#06b6d4' },
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.popularity?.members_ranges || {}
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
              backgroundColor: this.colors.cyan + '80',
              borderColor: this.colors.cyan,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#374151' }, ticks: { color: '#94a3b8' } },
            x: { grid: { color: '#374151' }, ticks: { color: '#94a3b8' } },
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
