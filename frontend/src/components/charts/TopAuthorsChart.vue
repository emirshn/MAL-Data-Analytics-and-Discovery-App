<template>
  <BaseChart
    title="Most Prolific Authors"
    icon="✍️"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TopAuthorsChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: { purple: '#8b5cf6' },
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.creators?.top_authors || {}
      const sortedAuthors = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)

      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedAuthors.map(([author]) => author),
          datasets: [
            {
              label: 'Manga Count',
              data: sortedAuthors.map(([, count]) => count),
              backgroundColor: this.colors.purple + '80',
              borderColor: this.colors.purple,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: { legend: { display: false } },
          scales: {
            x: { beginAtZero: true, grid: { color: '#374151' } },
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
          animation: { delay: (ctx) => ctx.dataIndex * 100, duration: 1500 },
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
