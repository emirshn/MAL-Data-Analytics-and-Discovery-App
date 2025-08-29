<template>
  <BaseChart
    title="Score Distribution (Logarithmic)"
    icon="📊"
    canvas-class="max-h-96"
    @canvas-ready="onCanvasReady"
  />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'ScoreDistributionChart',
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

      const animeData = this.stats.scores?.anime_distribution || {}
      const mangaData = this.stats.scores?.manga_distribution || {}

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(animeData),
          datasets: [
            {
              label: 'Anime',
              data: Object.values(animeData),
              backgroundColor: '#ff6b6b' + '80',
              borderColor: '#ff6b6b',
              borderWidth: 2,
            },
            {
              label: 'Manga',
              data: Object.values(mangaData),
              backgroundColor: '#4ecdc4' + '80',
              borderColor: '#4ecdc4',
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                color: 'rgb(148, 163, 184)',
              },
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (context) => `${context.dataset.label}: ${context.raw.toLocaleString()}`,
              },
            },
          },
          scales: {
            y: {
              type: 'logarithmic',
              beginAtZero: false,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
                callback: (value) => Number(value.toString()),
              },
            },
            x: {
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
          },
          animation: { duration: 2000, easing: 'easeOutQuart' },
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
