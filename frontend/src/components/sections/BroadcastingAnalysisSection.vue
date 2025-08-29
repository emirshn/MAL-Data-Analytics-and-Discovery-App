<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">📅 Time & Broadcasting</h2>

    <YearTimelineChart :stats="stats" />
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <SeasonChart :stats="stats" />
      <SeasonPerformanceChart :stats="stats" />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <BroadcastDaysChart :stats="stats" />
      <TimeSlotsChart :stats="stats" />
    </div>
  </section>
</template>

<script>
import BroadcastDaysChart from '../charts/BroadcastDaysChart.vue'
import SeasonChart from '../charts/SeasonChart.vue'
import SeasonPerformanceChart from '../charts/SeasonPerformanceChart.vue'
import TimeSlotsChart from '../charts/TimeSlotsChart.vue'
import YearTimelineChart from '../charts/YearTimelineChart.vue'

export default {
  name: 'BroadcastingAnalysisSection',
  components: {
    YearTimelineChart,
    TimeSlotsChart,
    BroadcastDaysChart,
    SeasonPerformanceChart,
    SeasonChart,
  },
  props: {
    stats: { type: Object, required: true },
  },
}
</script>
