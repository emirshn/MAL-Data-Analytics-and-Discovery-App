<template>
  <BaseChart title="Demographics" icon="👥" canvas-class="max-h-96" @canvas-ready="onCanvasReady" />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'DemographicsChart',
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

      const animeDemo = this.stats.classification?.anime_demographics || {}
      const mangaDemo = this.stats.classification?.manga_demographics || {}

      // Combine demographics
      const allDemographics = new Set([...Object.keys(animeDemo), ...Object.keys(mangaDemo)])

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Array.from(allDemographics),
          datasets: [
            {
              label: 'Anime',
              data: Array.from(allDemographics).map((demo) => animeDemo[demo] || 0),
              backgroundColor: '#ff6b6b' + '80',
              borderColor: '#ff6b6b',
              borderWidth: 2,
            },
            {
              label: 'Manga',
              data: Array.from(allDemographics).map((demo) => mangaDemo[demo] || 0),
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
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
            x: {
              grid: { color: '#374151' },
              ticks: {
                color: '#94a3b8',
              },
            },
          },
          animation: {
            delay: (ctx) => ctx.dataIndex * 200,
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
