<template>
  <div class="space-y-8">
    <!-- Related Anime/Manga -->
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
        Related
      </h3>

      <div class="flex gap-4 overflow-x-auto pb-4">
        <div v-for="relation in anime.relations" :key="relation.relation" class="flex gap-4">
          <div
            v-for="entry in relation.entry"
            :key="entry.mal_id"
            class="flex-shrink-0 w-32 group cursor-pointer"
            @click="$emit('entryClick', entry)"
          >
            <!-- Fixed height card with flex layout -->
            <div
              class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors h-full flex flex-col"
            >
              <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative flex-shrink-0">
                <img
                  :src="relationImages[entry.mal_id] || getPlaceholderImage(entry)"
                  :alt="entry.name"
                  class="w-full h-full object-cover"
                  @error="() => handleRelationImageError(entry)"
                  loading="lazy"
                />
                <div class="absolute top-2 right-2">
                  <span
                    class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded uppercase"
                  >
                    {{ entry.type }}
                  </span>
                </div>
              </div>
              <!-- Fixed height content area -->
              <div class="p-2 flex-1 flex flex-col justify-between min-h-[60px]">
                <h5
                  class="text-xs font-medium text-white line-clamp-2 group-hover:text-pink-300 transition-colors leading-tight mb-1 flex-1"
                >
                  {{ entry.name }}
                </h5>
                <span class="text-xs text-pink-300 capitalize flex-shrink-0">
                  {{ relation.relation }}
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
            <!-- Fixed height card -->
            <div
              class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors h-full flex flex-col"
            >
              <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative flex-shrink-0">
                <img
                  :src="getRecommendationImageUrl(recommendation.entry)"
                  :alt="recommendation.entry.title"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div class="absolute top-2 right-2">
                  <span
                    class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded uppercase"
                  >
                    {{ getRecommendationType(recommendation.entry) }}
                  </span>
                </div>
              </div>
              <!-- Fixed height content area -->
              <div class="p-3 flex-1 flex flex-col justify-between min-h-[70px]">
                <h5
                  class="text-sm font-medium text-white line-clamp-2 group-hover:text-amber-300 transition-colors leading-tight mb-1 flex-1"
                >
                  {{ recommendation.entry.title }}
                </h5>
                <span class="text-xs text-amber-300 flex-shrink-0"
                  >{{ recommendation.votes }} votes</span
                >
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

function getRecommendationType(entry) {
  // Check the URL to determine if it's anime or manga
  if (entry.url) {
    if (entry.url.includes('/manga/')) {
      return 'MANGA'
    } else if (entry.url.includes('/anime/')) {
      return 'ANIME'
    }
  }

  // Fallback to entry type if available
  if (entry.type) {
    return entry.type.toUpperCase()
  }

  // Default fallback
  return 'ANIME'
}
</script>
