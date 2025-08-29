<template>
  <BaseChart
    title="Genre Performance"
    icon="🏆"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'GenrePerformanceChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      if (!this.canvasElement) return

      const data = this.stats.genres?.performance || {}
      const sortedGenres = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedGenres.map(([genre]) => genre),
          datasets: [
            {
              label: 'Average Score',
              data: sortedGenres.map(([, score]) => score),
              backgroundColor: '#4ecdc4' + '80',
              borderColor: '#4ecdc4',
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (context) => `Average Score: ${context.raw.toFixed(2)}`,
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
          },
          animation: {
            delay: (ctx) => ctx.dataIndex * 100,
            duration: 1500,
            easing: 'easeOutQuart',
          },
        },
      })
    },
  },
  watch: {
    stats: {
      handler() {
        if (this.canvasElement) {
          this.createChart()
        }
      },
      deep: true,
    },
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy()
    }
  },
}
</script>
