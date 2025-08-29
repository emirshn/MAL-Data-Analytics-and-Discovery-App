<template>
  <BaseChart
    title="Seasonal Distribution"
    icon="🌸"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'SeasonChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: {
        pink: '#ff6bcb',
        yellow: '#feca57',
        orange: '#ff9f43',
        blue: '#54a0ff',
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

      const data = this.stats.timing?.season_distribution || {}
      const seasons = ['spring', 'summer', 'fall', 'winter']

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'polarArea',
        data: {
          labels: seasons.map((s) => s.charAt(0).toUpperCase() + s.slice(1)),
          datasets: [
            {
              data: seasons.map((s) => data[s] || 0),
              backgroundColor: [
                this.colors.pink + '80',
                this.colors.yellow + '80',
                this.colors.orange + '80',
                this.colors.blue + '80',
              ],
              borderColor: [
                this.colors.pink,
                this.colors.yellow,
                this.colors.orange,
                this.colors.blue,
              ],
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString()} releases`,
              },
            },
          },
          scales: {
            r: {
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: { color: 'rgb(148,163,184)' },
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
