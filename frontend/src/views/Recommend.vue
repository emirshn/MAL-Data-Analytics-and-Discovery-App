<template>
  <div class="pt-20 min-h-screen text-white relative bg-container">
    <div class="relative z-10 max-w-6xl mx-auto p-6">
      <div class="mb-8">
        <!-- Header -->
        <div class="text-center mb-12">
          <h1
            class="text-6xl font-extrabold mb-4 bg-gradient-to-r from-blue-500 to-violet-500 bg-clip-text text-transparent"
          >
            Multi-Anime Recommendations
          </h1>
          <p class="text-xl text-slate-400">
            Select multiple anime to get personalized recommendations based on your preferences
          </p>
        </div>
      </div>

      <!-- Anime Selection Section -->
      <div class="bg-gray-800 rounded-xl p-6 mb-8">
        <h2 class="text-2xl font-semibold mb-4">Selected Anime</h2>

        <!-- Search Input -->
        <div class="mb-4">
          <input
            v-model="searchQuery"
            @input="searchAnime"
            type="text"
            placeholder="Search for anime to add..."
            class="w-full p-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length" class="mb-6">
          <h3 class="text-lg mb-2">Search Results:</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
            <div
              v-for="anime in searchResults"
              :key="anime.mal_id"
              @click="addAnime(anime)"
              class="flex items-center p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
            >
              <img
                :src="anime.image_url || '/placeholder-anime.jpg'"
                :alt="anime.title"
                class="w-12 h-16 object-cover rounded mr-3"
                @error="handleImageError"
              />
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate">{{ anime.title }}</div>
                <div class="text-sm text-gray-400">
                  {{ anime.year }} • ★ {{ anime.score || 'N/A' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Anime List -->
        <div v-if="selectedAnime.length">
          <h3 class="text-lg mb-2">Selected Anime ({{ selectedAnime.length }}):</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div
              v-for="anime in selectedAnime"
              :key="anime.mal_id"
              class="flex items-center p-3 bg-gray-700 rounded-lg"
            >
              <img
                :src="anime.image_url || '/placeholder-anime.jpg'"
                :alt="anime.title"
                class="w-12 h-16 object-cover rounded mr-3"
                @error="handleImageError"
              />
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate">{{ anime.title }}</div>
                <div class="text-sm text-gray-400">
                  {{ anime.year }} • ★ {{ anime.score || 'N/A' }}
                </div>
              </div>
              <button
                @click="removeAnime(anime.mal_id)"
                class="text-red-400 hover:text-red-300 ml-2 p-1"
                title="Remove anime"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="mt-6">
          <button
            @click="generateRecommendations"
            :disabled="selectedAnime.length === 0 || loading"
            class="px-6 py-3 bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{
              loading
                ? 'Generating...'
                : selectedAnime.length === 0
                  ? 'Select anime to get recommendations'
                  : `Generate Recommendations (${selectedAnime.length} anime)`
            }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
        <div class="text-red-200">{{ error }}</div>
      </div>

      <!-- Filter Options (only show when we have recommendations) -->
      <div v-if="allRecommendations.length" class="bg-gray-800 rounded-xl p-6 mb-6">
        <h3 class="text-xl font-semibold mb-4">Filter Options</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <label class="flex items-center">
            <input v-model="filters.includeSequels" type="checkbox" class="mr-2" />
            <span>Include sequels</span>
          </label>
          <label class="flex items-center">
            <input v-model="filters.showExplanations" type="checkbox" class="mr-2" />
            <span>Show explanations</span>
          </label>
          <div class="flex items-center">
            <label class="mr-2">Min Score:</label>
            <select v-model="filters.minScore" class="bg-gray-700 text-white px-3 py-2 rounded">
              <option :value="null">Any</option>
              <option :value="6.0">6.0+</option>
              <option :value="7.0">7.0+</option>
              <option :value="8.0">8.0+</option>
              <option :value="9.0">9.0+</option>
            </select>
          </div>
          <div class="flex items-center">
            <label class="mr-2">Show:</label>
            <select v-model="filters.maxResults" class="bg-gray-700 text-white px-3 py-2 rounded">
              <option :value="12">12 results</option>
              <option :value="24">24 results</option>
              <option :value="36">36 results</option>
              <option :value="48">48 results</option>
              <option :value="60">60 results</option>
              <option :value="80">80 results</option>
              <option :value="100">100 results</option>
              <option :value="200">200 results</option>
            </select>
          </div>
        </div>

        <!-- Active filters summary -->
        <div v-if="activeFiltersCount > 0" class="mt-4 p-3 bg-gray-700 rounded-lg">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-300">
              Active filters:
              <span
                v-if="filters.minScore"
                class="inline-block bg-purple-600 px-2 py-1 rounded text-xs mr-2"
              >
                Score ≥ {{ filters.minScore }}
              </span>
              <span
                v-if="!filters.includeSequels"
                class="inline-block bg-purple-600 px-2 py-1 rounded text-xs mr-2"
              >
                No sequels
              </span>
            </div>
            <button @click="clearFilters" class="text-sm text-blue-400 hover:text-blue-300">
              Clear all
            </button>
          </div>
        </div>
      </div>

      <!-- Recommendations Section -->
      <div v-if="filteredRecommendations.length" class="bg-gray-800 rounded-xl p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-semibold">Recommended for You</h2>
          <div class="text-sm text-gray-400">
            Showing {{ filteredRecommendations.length }} of
            {{ allRecommendations.length }} recommendations
            <span v-if="recommendationData?.total_selected">
              (based on {{ recommendationData.total_selected }} selected anime)
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="rec in filteredRecommendations"
            :key="rec.mal_id"
            class="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors"
          >
            <img
              :src="rec.image_url || '/placeholder-anime.jpg'"
              :alt="rec.title"
              class="w-full h-48 object-cover rounded mb-3"
              @error="handleImageError"
            />
            <h3 class="font-semibold mb-2 line-clamp-2">{{ rec.title }}</h3>
            <div class="text-sm text-gray-300 mb-2">
              ★ {{ rec.score || 'N/A' }} • {{ rec.type }} •
              {{ rec.episodes ? `${rec.episodes} episodes` : 'Episodes TBA' }}
            </div>
            <div class="text-xs text-purple-400 mb-2">
              {{ rec.similarity.toFixed(1) }}% match
              <span v-if="rec.recommended_by_count" class="ml-2">
                ({{ rec.recommended_by_count }}/{{ selectedAnime.length }} sources)
              </span>
            </div>
            <p class="text-sm text-gray-400 mb-2 line-clamp-3">{{ rec.synopsis }}</p>

            <!-- Explanation (only show if filter is enabled) -->
            <div
              v-if="filters.showExplanations && rec.explanation"
              class="text-xs text-green-400 mt-2 p-2 bg-gray-800 rounded"
            >
              {{ rec.explanation }}
            </div>

            <!-- Recommended by -->
            <div
              v-if="rec.recommended_by && rec.recommended_by.length"
              class="text-xs text-blue-400 mt-2"
            >
              Similar to: {{ rec.recommended_by.slice(0, 2).join(', ') }}
              <span v-if="rec.recommended_by.length > 2">...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- No results after filtering -->
      <div
        v-else-if="allRecommendations.length && !filteredRecommendations.length"
        class="bg-gray-800 rounded-xl p-6 text-center"
      >
        <div class="text-gray-400 text-lg mb-2">No recommendations match your current filters</div>
        <div class="text-gray-500 text-sm mb-4">
          Try adjusting your filter criteria to see more results
        </div>
        <button @click="clearFilters" class="px-4 py-2 bg-purple-600 rounded hover:bg-purple-700">
          Clear Filters
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && selectedAnime.length === 0" class="text-center py-12">
        <div class="text-gray-400 text-lg mb-4">
          🎯 Select your favorite anime to get personalized recommendations
        </div>
        <div class="text-gray-500 text-sm">
          Search and add anime above to discover similar shows you might enjoy
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import axios from 'axios'

const selectedAnime = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const allRecommendations = ref([]) // Store all recommendations from backend
const recommendationData = ref(null)
const loading = ref(false)
const error = ref('')

// Separate filters from backend options
const filters = reactive({
  includeSequels: true,
  showExplanations: false,
  minScore: null,
  maxResults: 24,
})

// Backend options (sent with API request)
const options = reactive({
  includeSequels: true,
  explain: true, // Always get explanations from backend, filter display on frontend
  minScore: null,
})

// Computed property for filtered recommendations
const filteredRecommendations = computed(() => {
  let filtered = [...allRecommendations.value]

  // Apply min score filter
  if (filters.minScore) {
    filtered = filtered.filter((rec) => rec.score && rec.score >= filters.minScore)
  }

  // Apply sequels filter
  if (!filters.includeSequels) {
    filtered = filtered.filter((rec) => !isSequel(rec))
  }

  // Sort by similarity/score combination
  filtered.sort((a, b) => {
    const similarityDiff = (b.similarity || 0) - (a.similarity || 0)
    if (Math.abs(similarityDiff) > 0.05) return similarityDiff
    return (b.score || 0) - (a.score || 0)
  })

  // Remove duplicates based on title similarity
  filtered = removeSimilarTitles(filtered)

  // Limit results
  return filtered.slice(0, filters.maxResults)
})

// Count active filters
const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.minScore) count++
  if (!filters.includeSequels) count++
  return count
})

// Helper function to detect sequels
const isSequel = (rec) => {
  return selectedAnime.value.some((anime) => {
    const animeTitle = anime.title.toLowerCase()
    const recTitle = rec.title.toLowerCase()

    // More sophisticated sequel detection
    const baseTitleAnime = animeTitle
      .replace(/[:\-\s]*(season|part|ova|movie|special).*$/i, '')
      .trim()
    const baseTitleRec = recTitle.replace(/[:\-\s]*(season|part|ova|movie|special).*$/i, '').trim()

    return (
      baseTitleAnime === baseTitleRec ||
      recTitle.includes(baseTitleAnime) ||
      animeTitle.includes(baseTitleRec) ||
      // Check for common sequel patterns
      /['"]/.test(recTitle) || // Contains apostrophe (like Gintama')
      /°/.test(recTitle) || // Contains degree symbol (like Gintama°)
      /\d+$/.test(recTitle.replace(/\s+/g, '')) || // Ends with number
      recTitle.includes('season') ||
      recTitle.includes('part') ||
      recTitle.includes('continuation')
    )
  })
}

// Helper function to remove similar titles
const removeSimilarTitles = (recommendations) => {
  const seen = new Set()
  return recommendations.filter((rec) => {
    const baseTitle = rec.title
      .toLowerCase()
      .replace(/[:\-\s]*(season|part|ova|movie|special|tv|ona).*$/i, '')
      .replace(/['°\d]/g, '')
      .trim()

    if (seen.has(baseTitle)) {
      return false
    }
    seen.add(baseTitle)
    return true
  })
}

const clearFilters = () => {
  filters.minScore = null
  filters.includeSequels = true
  filters.maxResults = 24
}

// Watch for significant filter changes to regenerate recommendations
watch(
  () => filters.includeSequels,
  (newVal) => {
    options.includeSequels = newVal
    if (selectedAnime.value.length > 0) {
      generateRecommendations()
    }
  },
)

const searchAnime = async () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }

  try {
    const response = await axios.post('http://127.0.0.1:8000/anime/search', {
      q: searchQuery.value,
      limit: 10,
    })

    searchResults.value = response.data.data || []
  } catch (err) {
    console.error('Search error:', err)
    searchResults.value = []
  }
}

const addAnime = (anime) => {
  if (!selectedAnime.value.find((a) => a.mal_id === anime.mal_id)) {
    selectedAnime.value.push(anime)
    searchResults.value = []
    searchQuery.value = ''
  }
}

const removeAnime = (malId) => {
  selectedAnime.value = selectedAnime.value.filter((a) => a.mal_id !== malId)

  if (selectedAnime.value.length === 0) {
    allRecommendations.value = []
    recommendationData.value = null
  }
}

const generateRecommendations = async () => {
  if (selectedAnime.value.length === 0) return

  loading.value = true
  error.value = ''

  try {
    const animeIds = selectedAnime.value.map((anime) => anime.mal_id)

    const response = await axios.post('http://127.0.0.1:8000/anime/multi-recommend', {
      anime_ids: animeIds,
      top_k: 200,
      min_score: options.minScore,
      include_sequels: options.includeSequels,
      explain: options.explain,
      diversity_weight: 0.4,
    })

    if (response.data.error) {
      error.value = response.data.error
      allRecommendations.value = []
      recommendationData.value = null
    } else {
      allRecommendations.value = response.data.recommendations || []
      recommendationData.value = response.data
    }
  } catch (err) {
    console.error('Recommendation error:', err)
    error.value = err.response?.data?.detail || 'Failed to generate recommendations'
    allRecommendations.value = []
    recommendationData.value = null
  } finally {
    loading.value = false
  }
}

const handleImageError = (event) => {
  event.target.src = '/placeholder-anime.jpg'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bg-gray-650 {
  background-color: #374151;
}

.bg-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
