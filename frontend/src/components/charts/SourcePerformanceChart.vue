<template>
  <BaseChart
    title="Source Performance"
    icon="📊"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'SourcePerformanceChart',
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

      const data = this.stats.classification?.source_performance || {}
      const sortedSources = Object.entries(data).sort((a, b) => b[1].avg_score - a[1].avg_score)

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Source Performance',
              data: sortedSources.map(([source, data]) => ({
                x: data.count,
                y: data.avg_score,
                label: source,
              })),
              backgroundColor: '#17a2b8' + '80',
              borderColor: '#17a2b8',
              borderWidth: 2,
              pointRadius: 8,
              pointHoverRadius: 12,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (context) => {
                  const point = context.raw
                  return `${point.label}: ${point.y.toFixed(2)} score (${point.x} anime)`
                },
              },
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Number of Anime',
                color: 'rgb(148, 163, 184)',
              },
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
            y: {
              title: {
                display: true,
                text: 'Average Score',
                color: 'rgb(148, 163, 184)',
              },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
          },
          animation: {
            duration: 2000,
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
