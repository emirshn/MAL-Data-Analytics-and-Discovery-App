<template>
  <BaseChart
    title="Genre Combinations"
    icon="🔗"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'GenreCombinationsChart',
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

      const data = this.stats.genres?.combinations || []

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.slice(0, 10).map((item) => item.pair),
          datasets: [
            {
              label: 'Frequency',
              data: data.slice(0, 10).map((item) => item.count),
              backgroundColor: '#9b59b6' + '80',
              borderColor: '#9b59b6',
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
                label: (context) => `Frequency: ${context.raw.toLocaleString()}`,
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 20 ? label.substring(0, 20) + '...' : label
                },
              },
            },
          },
          animation: {
            delay: (ctx) => ctx.dataIndex * 150,
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
