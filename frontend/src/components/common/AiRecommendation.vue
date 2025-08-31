<template>
  <div class="bg-gray-800 rounded-xl p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-xl font-semibold text-amber-400 flex items-center">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        AI-Powered Recommendations
      </h3>

      <!-- Filter Controls -->
      <div class="flex items-center gap-3 text-sm">
        <label class="flex items-center text-gray-300">
          <input
            :checked="filters.includeSequels"
            type="checkbox"
            class="mr-2 rounded bg-gray-700 border-gray-600 text-amber-500 focus:ring-amber-500"
            @change="handleFilterChange('includeSequels', $event.target.checked)"
          />
          Include Sequels
        </label>
        <label class="flex items-center text-gray-300">
          <input
            :checked="filters.showExplanations"
            type="checkbox"
            class="mr-2 rounded bg-gray-700 border-gray-600 text-amber-500 focus:ring-amber-500"
            @change="handleFilterChange('showExplanations', $event.target.checked)"
          />
          Show Explanations
        </label>
        <select
          :value="filters.minScore"
          class="bg-gray-700 border-gray-600 text-white rounded px-2 py-1 text-sm"
          @change="handleFilterChange('minScore', $event.target.value)"
        >
          <option value="">Any Score</option>
          <option value="6.0">6.0+ Rating</option>
          <option value="7.0">7.0+ Rating</option>
          <option value="8.0">8.0+ Rating</option>
          <option value="8.5">8.5+ Rating</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400"></div>
      <p class="mt-2 text-gray-400">Finding similar {{ contentType }}...</p>
    </div>

    <!-- Recommendations Grid -->
    <div
      v-else-if="recommendations && recommendations.length > 0"
      class="overflow-x-auto overflow-y-hidden"
    >
      <div class="flex gap-4 pb-4 min-w-max">
        <div
          v-for="recommendation in recommendations"
          :key="recommendation.id || recommendation.mal_id"
          class="flex-shrink-0 w-48 group cursor-pointer"
          @click="handleItemClick(recommendation)"
        >
          <div
            class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-all duration-300 h-full hover:shadow-lg hover:shadow-amber-500/20"
          >
            <!-- Image -->
            <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
              <img
                :src="getImageUrl(recommendation)"
                :alt="recommendation.title"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                @error="handleImageError($event, recommendation)"
              />

              <!-- Type Badge -->
              <div class="absolute top-2 right-2">
                <span class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded">
                  {{ recommendation.type || contentType.toUpperCase() }}
                </span>
              </div>

              <!-- Score and Similarity -->
              <div class="absolute bottom-2 left-2 flex flex-col gap-1">
                <span
                  v-if="recommendation.score"
                  class="px-2 py-1 bg-amber-600 bg-opacity-90 text-white text-xs rounded flex items-center"
                >
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    />
                  </svg>
                  {{ formatScore(recommendation.score) }}
                </span>

                <span
                  v-if="recommendation.similarity"
                  class="px-2 py-1 bg-blue-600 bg-opacity-90 text-white text-xs rounded"
                >
                  {{ Math.round(recommendation.similarity * 100) }}% match
                </span>
              </div>
            </div>

            <!-- Content -->
            <div class="p-3">
              <h5
                class="text-sm font-medium text-white line-clamp-2 group-hover:text-amber-300 transition-colors leading-tight mb-2"
              >
                {{ recommendation.title }}
              </h5>

              <!-- English Title -->
              <p
                v-if="
                  recommendation.title_english &&
                  recommendation.title_english !== recommendation.title
                "
                class="text-xs text-gray-400 mb-2 line-clamp-1"
              >
                {{ recommendation.title_english }}
              </p>

              <!-- Meta Info -->
              <div class="flex items-center justify-between text-xs text-gray-400 mb-2">
                <span v-if="recommendation.year">{{ recommendation.year }}</span>
                <span v-if="recommendation.episodes">{{ recommendation.episodes }} eps</span>
                <span v-if="recommendation.chapters">{{ recommendation.chapters }} ch</span>
                <span v-if="recommendation.volumes">{{ recommendation.volumes }} vol</span>
              </div>

              <!-- Explanation (if enabled) -->
              <div
                v-if="filters.showExplanations && recommendation.explanation"
                class="bg-gray-800 rounded p-2 mt-2"
              >
                <p class="text-xs text-amber-200 leading-relaxed">
                  {{ recommendation.explanation }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results Message -->
    <div v-else-if="!loading" class="text-center py-8 text-gray-400">
      <svg
        class="w-12 h-12 mx-auto mb-4 opacity-50"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"
        />
      </svg>
      <p>No recommendations found with current filters</p>
      <button
        @click="handleResetFilters()"
        class="mt-2 text-amber-400 hover:text-amber-300 text-sm underline"
      >
        Reset Filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  recommendations: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  filters: {
    type: Object,
    required: true,
    default: () => ({
      includeSequels: false,
      showExplanations: true,
      minScore: '',
    }),
  },
  contentType: {
    type: String,
    default: 'anime',
  },
})

const emit = defineEmits(['filters-changed', 'item-click', 'image-error', 'reset-filters'])

const getImageUrl = (recommendation) => {
  return recommendation.image_url || recommendation.thumbnail_url || '/api/placeholder/160/213'
}

const formatScore = (score) => {
  if (!score) return 'N/A'
  return parseFloat(score).toFixed(1)
}

const handleFilterChange = (filterName, value) => {
  console.log('Filter changed:', filterName, value)
  emit('filters-changed', { [filterName]: value })
}

const handleItemClick = (recommendation) => {
  console.log('Item clicked:', recommendation)
  emit('item-click', recommendation)
}

const handleImageError = (event, recommendation) => {
  console.log('Image error for:', recommendation)
  event.target.src = '/api/placeholder/160/213'
  emit('image-error', event, recommendation)
}

const handleResetFilters = () => {
  console.log('Reset filters clicked')
  emit('reset-filters')
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
