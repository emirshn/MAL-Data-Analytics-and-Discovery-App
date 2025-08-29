<template>
  <BaseChart
    title="Popularity vs Score"
    icon="📊"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'PopularityScoreChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return { chartInstance: null, canvasElement: null, colors: { pink: '#ec4899' } }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.popularity?.correlations?.popularity_score || []
      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Popularity vs Score',
              data: data.map((d) => ({ x: d.popularity, y: d.score, title: d.title })),
              backgroundColor: this.colors.pink + '60',
              borderColor: this.colors.pink,
              borderWidth: 1,
              pointRadius: 4,
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
              callbacks: {
                label: (ctx) => `${ctx.raw.title}: Score ${ctx.raw.y}, Popularity #${ctx.raw.x}`,
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Popularity Rank (lower = more popular)' },
              reverse: true,
              grid: { color: '#374151' },
            },
            y: {
              title: { display: true, text: 'Score' },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    },
  },
  watch: {
    stats: {
      deep: true,
      handler() {
        this.createChart()
      },
    },
  },
  beforeUnmount() {
    if (this.chartInstance) this.chartInstance.destroy()
  },
}
</script>
