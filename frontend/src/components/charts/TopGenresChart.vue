<template>
  <BaseChart title="Top Genres" icon="🎭" canvas-class="max-h-96" @canvas-ready="onCanvasReady" />
</template>

<script>
import BaseChart from './BaseChart.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TopGenresChart',
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

      const data = this.stats.genres?.top_combined || {}

      if (this.chartInstance) {
        this.chartInstance.destroy()
      }

      const ctx = this.canvasElement.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data).slice(0, 10),
          datasets: [
            {
              data: Object.keys(data)
                .slice(0, 10)
                .map((key) => data[key].total),
              backgroundColor: this.chartColors,
              borderWidth: 3,
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
              },
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              callbacks: {
                label: (context) => {
                  const genre = context.label
                  const genreData = data[genre]
                  return `${genre}: ${genreData.total.toLocaleString()} (A:${genreData.anime}, M:${genreData.manga})`
                },
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
