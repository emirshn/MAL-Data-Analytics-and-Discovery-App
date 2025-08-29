<template>
  <BaseChart
    title="Broadcast Time Slots"
    icon="⏰"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TimeSlotsChart',
  components: { BaseChart },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      chartInstance: null,
      canvasElement: null,
      colors: {
        yellow: '#facc15',
        orange: '#fb923c',
        red: '#f87171',
        purple: '#a78bfa',
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

      const data = this.stats.timing?.broadcast_time_slots || {}

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: [
                this.colors.yellow + '80',
                this.colors.orange + '80',
                this.colors.red + '80',
                this.colors.purple + '80',
              ],
              borderColor: [
                this.colors.yellow,
                this.colors.orange,
                this.colors.red,
                this.colors.purple,
              ],
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: 'rgb(148,163,184)' },
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString()} shows`,
              },
            },
          },
          animation: { animateRotate: true, duration: 2000 },
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
    if (this.chartInstance) this.chartInstance.destroy()
  },
}
</script>
