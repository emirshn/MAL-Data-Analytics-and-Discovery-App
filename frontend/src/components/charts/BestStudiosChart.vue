<template>
  <BaseChart
    title="Best Studios by Score"
    icon="⭐"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'BestStudiosChart',
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

      const data = this.stats.studios?.best_by_score || {}
      const sortedStudios = Object.entries(data)
        .sort((a, b) => b[1].avg_score - a[1].avg_score)
        .slice(0, 10)

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
              label: 'Average Score',
              data: sortedStudios.map(([, data]) => data.avg_score),
              backgroundColor: '#f39c12' + '80',
              borderColor: '#f39c12',
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
                label: (context) => {
                  const studioData = data[context.label]
                  return `Score: ${context.raw.toFixed(2)} (${studioData.count} anime)`
                },
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
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: {
            delay: (ctx) => ctx.dataIndex * 120,
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
