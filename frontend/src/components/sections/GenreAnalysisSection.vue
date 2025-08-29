<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">🎭 Genre Analysis</h2>

    <!-- Pie Charts Row - Top Genres and Genre Combinations -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <TopGenresChart :stats="stats" />
      <GenreCombinationsChart :stats="stats" />
    </div>

    <!-- Genre Performance - Full Width -->
    <GenrePerformanceChart :stats="stats" />
  </section>
</template>

<script>
import TopGenresChart from '../charts/TopGenresChart.vue'
import GenreCombinationsChart from '../charts/GenreCombinationsChart.vue'
import GenrePerformanceChart from '../charts/GenrePerformanceChart.vue'

export default {
  name: 'GenreAnalysisSection',
  components: {
    TopGenresChart,
    GenreCombinationsChart,
    GenrePerformanceChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
