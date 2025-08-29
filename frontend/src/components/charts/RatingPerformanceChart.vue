<template>
  <BaseChart
    title="Rating Performance"
    icon="🏆"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'RatingPerformanceChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      chartColors: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#FF6384',
        '#C9CBCF',
        '#4BC0C0',
        '#FF6384',
        '#8b5cf6',
        '#06b6d4',
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#ec4899',
        '#14b8a6',
        '#f97316',
        '#3b82f6',
        '#64748b',
      ],
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      if (!this.canvasElement) return

      const data = this.stats.classification?.rating_scores || {}

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      if (Object.keys(data).length === 0) return

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'polarArea',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: this.chartColors.map((color) => color + 'CC'), // More opaque
              borderColor: this.chartColors,
              borderWidth: 3, // Thicker borders
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 20,
              bottom: 20,
              left: 20,
              right: 20,
            },
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: 'rgb(148, 163, 184)',
                padding: 20,
                font: {
                  size: 12,
                },
              },
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
              titleColor: 'white',
              bodyColor: 'white',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              callbacks: {
                label: (context) => {
                  return `${context.label}: ${context.raw.toFixed(2)} avg score`
                },
              },
            },
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 10,
              grid: {
                color: '#374151',
                lineWidth: 1,
              },
              angleLines: {
                color: '#374151',
                lineWidth: 1,
              },
              ticks: {
                color: '#94a3b8',
                stepSize: 2,
                font: {
                  size: 11,
                },
                backdropColor: 'transparent',
              },
              pointLabels: {
                color: '#94a3b8',
                font: {
                  size: 12,
                  weight: 'bold',
                },
              },
            },
          },
          animation: {
            duration: 2000,
            animateScale: true,
            animateRotate: true,
          },
          elements: {
            arc: {
              borderWidth: 3,
            },
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
