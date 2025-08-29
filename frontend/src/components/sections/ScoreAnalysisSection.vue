<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">⭐ Score Analysis</h2>

    <ScoreDistributionChart :stats="stats" />
    <RatingPerformanceChart :stats="stats" />
  </section>
</template>

<script>
import ScoreDistributionChart from '../charts/ScoreDistributionChart.vue'
import RatingPerformanceChart from '../charts/RatingPerformanceChart.vue'

export default {
  name: 'ScoreAnalysisSection',
  components: {
    ScoreDistributionChart,
    RatingPerformanceChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
