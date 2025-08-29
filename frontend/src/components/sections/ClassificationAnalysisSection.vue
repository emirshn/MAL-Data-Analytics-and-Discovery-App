<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">📚 Content Classification</h2>

    <!-- First Row: Anime Types, Manga Types, Source Material (3 pie charts) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <AnimeTypesChart :stats="stats" />
      <MangaTypesChart :stats="stats" />
      <SourceMaterialChart :stats="stats" />
    </div>

    <!-- Second Row: Source Performance - Full Width -->
    <SourcePerformanceChart :stats="stats" />

    <!-- Third Row: Demographics and Rating Distribution -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <DemographicsChart :stats="stats" />
      <RatingDistributionChart :stats="stats" />
    </div>
  </section>
</template>

<script>
import AnimeTypesChart from '../charts/AnimeTypesChart.vue'
import MangaTypesChart from '../charts/MangaTypesChart.vue'
import SourceMaterialChart from '../charts/SourceMaterialChart.vue'
import SourcePerformanceChart from '../charts/SourcePerformanceChart.vue'
import DemographicsChart from '../charts/DemographicsChart.vue'
import RatingDistributionChart from '../charts/RatingDistributionChart.vue'

export default {
  name: 'ClassificationAnalysisSection',
  components: {
    AnimeTypesChart,
    MangaTypesChart,
    SourceMaterialChart,
    SourcePerformanceChart,
    DemographicsChart,
    RatingDistributionChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
