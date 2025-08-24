<template>
  <div class="space-y-8">
    <!-- Related Anime -->
    <div v-if="anime.relations && anime.relations.length" class="bg-gray-800 rounded-xl p-6">
      <h3 class="text-xl font-semibold mb-6 text-pink-400 flex items-center">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
        Related Anime
      </h3>

      <div class="flex gap-4 overflow-x-auto pb-4">
        <div v-for="relation in anime.relations" :key="relation.relation" class="flex gap-4">
          <div
            v-for="entry in relation.entry"
            :key="entry.mal_id"
            class="flex-shrink-0 w-32 group cursor-pointer"
            @click="$emit('entryClick', entry)"
          >
            <div class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors">
              <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                <img
                  :src="relationImages[entry.mal_id] || getPlaceholderImage(entry)"
                  :alt="entry.name"
                  class="w-full h-full object-cover"
                  @error="() => handleRelationImageError(entry)"
                />
                <div class="absolute top-2 right-2">
                  <span
                    class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded uppercase"
                  >
                    {{ entry.type }}
                  </span>
                </div>
              </div>
              <div class="p-2">
                <h5
                  class="text-xs font-medium text-white line-clamp-2 group-hover:text-pink-300 transition-colors leading-tight mb-1"
                >
                  {{ entry.name }}
                </h5>
                <span class="text-xs text-pink-300 capitalize">
                  {{ getRelationForEntry(entry.mal_id) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Recommendations -->
    <div
      v-if="anime.recommendations && anime.recommendations.length"
      class="bg-gray-800 rounded-xl p-6"
    >
      <h3 class="text-xl font-semibold mb-6 text-amber-400 flex items-center">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
        Recommended By Users
      </h3>

      <div class="overflow-x-auto overflow-y-hidden">
        <div class="flex gap-4 pb-4 min-w-max">
          <div
            v-for="recommendation in anime.recommendations"
            :key="recommendation.entry.mal_id"
            class="flex-shrink-0 w-40 group cursor-pointer"
            @click="$emit('entryClick', recommendation)"
          >
            <div
              class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors h-full"
            >
              <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                <img
                  :src="getRecommendationImageUrl(recommendation.entry)"
                  :alt="recommendation.entry.title"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div class="absolute top-2 right-2">
                  <span class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded"
                    >ANIME</span
                  >
                </div>
                <div class="absolute bottom-2 left-2">
                  <span
                    class="px-2 py-1 bg-amber-600 bg-opacity-90 text-white text-xs rounded flex items-center"
                  >
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                      />
                    </svg>
                    {{ recommendation.votes }}
                  </span>
                </div>
              </div>
              <div class="p-3">
                <h5
                  class="text-sm font-medium text-white line-clamp-2 group-hover:text-amber-300 transition-colors leading-tight mb-1"
                >
                  {{ recommendation.entry.title }}
                </h5>
                <span class="text-xs text-amber-300">{{ recommendation.votes }} votes</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  anime: { type: Object, required: true },
  relationImages: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['relationImageError'])

function handleRelationImageError(entry) {
  emit('relationImageError', entry)
}

function getPlaceholderImage(entry) {
  return `https://via.placeholder.com/200x280/374151/f3f4f6?text=${encodeURIComponent(
    entry.type || 'anime',
  )}`
}

function getRecommendationImageUrl(entry) {
  return entry.images?.jpg?.image_url || getPlaceholderImage(entry)
}

function getRelationForEntry(malId) {
  return ''
}
</script>
