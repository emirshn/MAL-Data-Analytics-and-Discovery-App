<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">🏭 Studio & Production</h2>

    <TopStudiosChart :stats="stats" />

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <BestStudiosChart :stats="stats" />
      <TopProducersChart :stats="stats" />
    </div>
  </section>
</template>

<script>
import TopStudiosChart from '../charts/TopStudiosChart.vue'
import BestStudiosChart from '../charts/BestStudiosChart.vue'
import TopProducersChart from '../charts/TopProducersChart.vue'

export default {
  name: 'StudioAnalysisSection',
  components: {
    TopStudiosChart,
    BestStudiosChart,
    TopProducersChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
