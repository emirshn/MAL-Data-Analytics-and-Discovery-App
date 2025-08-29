<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">📏 Content Length</h2>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <EpisodeDistributionChart :stats="stats" />
      <ChapterDistributionChart :stats="stats" />
    </div>
  </section>
</template>

<script>
import ChapterDistributionChart from '../charts/ChapterDistributionChart.vue'
import EpisodeDistributionChart from '../charts/EpisodeDistributionChart.vue'

export default {
  name: 'BroadcastingAnalysisSection',
  components: {
    EpisodeDistributionChart,
    ChapterDistributionChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
