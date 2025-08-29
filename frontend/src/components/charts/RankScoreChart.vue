<template>
  <BaseChart
    title="Rank vs Score"
    icon="🏆"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'RankScoreChart',
  components: { BaseChart },
  props: { stats: { type: Object, required: true } },
  data() {
    return { chartInstance: null, canvasElement: null, colors: { warning: '#f59e0b' } }
  },
  methods: {
    onCanvasReady(canvas) {
      this.canvasElement = canvas
      this.createChart()
    },
    createChart() {
      const data = this.stats.popularity?.correlations?.rank_score || []
      if (!this.canvasElement) return
      if (this.chartInstance) this.chartInstance.destroy()

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Rank vs Score',
              data: data.map((d) => ({ x: d.rank, y: d.score, title: d.title })),
              backgroundColor: this.colors.warning + '60',
              borderColor: this.colors.warning,
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
                label: (ctx) => `${ctx.raw.title}: Score ${ctx.raw.y}, Rank #${ctx.raw.x}`,
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Rank (lower = better)' },
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
