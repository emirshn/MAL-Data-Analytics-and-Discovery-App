<template>
  <BaseChart
    title="Season Performance"
    icon="🏆"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'SeasonPerformanceChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: {
        success: '#4ade80', // Tailwind green-400
      },
    }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      if (!this.canvasElement) return

      const data = this.stats.timing?.season_performance || {}
      const seasons = Object.keys(data)

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: seasons.map((s) => s.charAt(0).toUpperCase() + s.slice(1)),
          datasets: [
            {
              label: 'Average Score',
              data: seasons.map((season) => data[season]?.avg_score || 0),
              backgroundColor: this.colors.success + '30',
              borderColor: this.colors.success,
              borderWidth: 2,
              pointBackgroundColor: this.colors.success,
              pointBorderColor: this.colors.success,
              pointRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (ctx) => `${ctx.label}: ${ctx.raw.toFixed(2)}/10`,
              },
            },
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
              pointLabels: { color: '#94a3b8', font: { size: 14 } },
              ticks: { color: '#94a3b8' },
            },
          },
          animation: { duration: 2000, easing: 'easeOutCubic' },
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
