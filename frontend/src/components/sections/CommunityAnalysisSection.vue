<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">🌟 Popularity & Community</h2>

    <MembersDistributionChart :stats="stats" />

    <!-- Tabs -->
    <div class="flex justify-center space-x-4 border-b border-slate-700">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="[
          'px-4 py-2 font-semibold',
          activeTab === tab
            ? 'text-indigo-400 border-b-2 border-indigo-400'
            : 'text-slate-400 hover:text-slate-200',
        ]"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Active Chart -->
    <div class="p-4 bg-slate-900 rounded-2xl shadow-lg">
      <MembersScoreChart v-if="activeTab === 'Members Score'" :stats="stats" />
      <PopularityScoreChart v-if="activeTab === 'Popularity Score'" :stats="stats" />
      <RankScoreChart v-if="activeTab === 'Rank Score'" :stats="stats" />
    </div>
  </section>
</template>

<script>
import MembersDistributionChart from '../charts/MembersDistributionChart.vue'
import MembersScoreChart from '../charts/MembersScoreChart.vue'
import PopularityScoreChart from '../charts/PopularityScoreChart.vue'
import RankScoreChart from '../charts/RankScoreChart.vue'

export default {
  name: 'BroadcastingAnalysisSection',
  components: {
    MembersDistributionChart,
    MembersScoreChart,
    PopularityScoreChart,
    RankScoreChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
  data() {
    return {
      tabs: ['Members Score', 'Popularity Score', 'Rank Score'],
      activeTab: 'Members Score',
    }
  },
}
</script>
