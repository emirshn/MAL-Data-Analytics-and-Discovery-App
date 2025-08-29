<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">✍️ Creators & Publications</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <TopAuthorsChart :stats="stats" />
      <BestAuthorsChart :stats="stats" />
      <TopSerializationsChart :stats="stats" />
    </div>
  </section>
</template>

<script>
import BestAuthorsChart from '../charts/BestAuthorsChart.vue'
import TopAuthorsChart from '../charts/TopAuthorsChart.vue'
import TopSerializationsChart from '../charts/TopSerializationsChart.vue'

export default {
  name: 'ClassificationAnalysisSection',
  components: {
    TopAuthorsChart,
    BestAuthorsChart,
    TopSerializationsChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
