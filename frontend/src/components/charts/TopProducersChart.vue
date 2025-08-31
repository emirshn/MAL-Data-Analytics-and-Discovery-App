<template>
  <BaseChart
    title="Top Producers"
    icon="🎬"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TopProducersChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      chartColors: [
        '#ff6b6b',
        '#4ecdc4',
        '#45b7d1',
        '#96ceb4',
        '#feca57',
        '#ff9ff3',
        '#54a0ff',
        '#5f27cd',
        '#00d2d3',
        '#ff9f43',
        '#a29bfe',
        '#fd79a8',
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

      const data = this.stats.studios?.top_producers || {}
      const sortedProducers = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: sortedProducers.map(([producer]) => producer),
          datasets: [
            {
              data: sortedProducers.map(([, count]) => count),
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
                generateLabels: function (chart) {
                  const data = chart.data
                  if (data.labels.length && data.datasets.length) {
                    return data.labels.map((label, i) => ({
                      text: label.length > 20 ? label.substring(0, 20) + '...' : label,
                      fillStyle: data.datasets[0].backgroundColor[i],
                      fontColor: 'rgb(148, 163, 184)',
                      index: i,
                    }))
                  }
                  return []
                },
              },
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (context) => `${context.label}: ${context.raw.toLocaleString()}`,
              },
            },
          },
          animation: {
            animateRotate: true,
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
