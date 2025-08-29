<template>
  <BaseChart
    title="Highest Rated Authors"
    icon="🌟"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'BestAuthorsChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: { warning: '#facc15' },
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.creators?.best_authors || {}
      const sortedAuthors = Object.entries(data)
        .sort((a, b) => b[1].avg_score - a[1].avg_score)
        .slice(0, 10)

      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedAuthors.map(([author]) => author),
          datasets: [
            {
              label: 'Average Score',
              data: sortedAuthors.map(([, d]) => d.avg_score),
              backgroundColor: this.colors.warning + '80',
              borderColor: this.colors.warning,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const authorData = data[ctx.label]
                  return `Score: ${ctx.raw.toFixed(2)} (${authorData.count} works)`
                },
              },
            },
          },
          scales: {
            x: { beginAtZero: true, max: 10, grid: { color: '#374151' } },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 120, duration: 1500 },
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
