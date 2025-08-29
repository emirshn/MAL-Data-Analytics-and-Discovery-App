<template>
  <section class="space-y-8">
    <h2 class="text-3xl font-bold text-center text-indigo-400">🏆 Top Lists</h2>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <BaseList
        title="Most Favorited"
        icon="❤️"
        :items="stats.popularity?.top_favorites?.slice(0, 10)"
        value-key="favorites"
        value-class="text-red-400"
      >
        <template #subtitle="{ item }">Score: {{ item.score }}</template>
      </BaseList>

      <BaseList
        title="Most Members"
        icon="👥"
        :items="stats.popularity?.top_members?.slice(0, 10)"
        value-key="members"
        value-class="text-blue-400"
      >
        <template #subtitle="{ item }">Score: {{ item.score }}</template>
      </BaseList>

      <BaseList
        title="Highest Scored"
        icon="⭐"
        :items="stats.popularity?.top_scored?.slice(0, 10)"
        value-key="score"
        value-class="text-yellow-400"
      >
        <template #subtitle="{ item }">
          {{ (item.members || 0).toLocaleString() }} members
        </template>
      </BaseList>
    </div>
  </section>
</template>

<script>
import BaseList from '../common/BaseList.vue'

export default {
  name: 'TopListsSection',
  components: { BaseList },
  props: { stats: { type: Object, required: true } },
}
</script>
