<template>
  <BaseChart
    title="Release Timeline by Year"
    icon="📈"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'YearTimelineChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: {
        primary: '#4ecdc4',
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

      const data = this.stats.timing?.year_distribution || {}
      const sortedYears = Object.keys(data).sort((a, b) => parseInt(a) - parseInt(b))

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: sortedYears,
          datasets: [
            {
              label: 'Releases',
              data: sortedYears.map((year) => data[year]),
              borderColor: this.colors.primary,
              backgroundColor: this.colors.primary + '20',
              fill: true,
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 8,
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
                label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString()} releases`,
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: { color: 'rgb(148,163,184)' },
            },
            x: {
              grid: { color: '#374151' },
              ticks: {
                maxTicksLimit: 20,
                color: 'rgb(148,163,184)',
              },
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
