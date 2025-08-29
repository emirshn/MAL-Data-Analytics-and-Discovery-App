<template>
  <BaseChart
    title="Top Studios by Count"
    icon="🏢"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TopStudiosChart',
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

      const data = this.stats.studios?.top_by_count || {}
      const sortedStudios = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedStudios.map(([studio]) => studio),
          datasets: [
            {
              label: 'Anime Count',
              data: sortedStudios.map(([, count]) => count),
              backgroundColor: '#45b7d1' + '80',
              borderColor: '#45b7d1',
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
                label: (context) => `Anime Count: ${context.raw.toLocaleString()}`,
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
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
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
