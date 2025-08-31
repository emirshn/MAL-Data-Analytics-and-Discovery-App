<template>
  <div class="pt-20 min-h-screen text-white relative bg-container">
    <div class="relative z-10 max-w-7xl mx-auto p-6">
      <div class="mb-8">
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
      <div
        class="bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 mb-8 shadow-2xl border border-gray-700"
      >
        <h2 class="text-2xl font-semibold mb-4">Selected Anime</h2>

        <!-- Search Input -->
        <div class="mb-4">
          <div class="relative">
            <input
              v-model="searchQuery"
              @input="searchAnime"
              type="text"
              placeholder="Search for anime to add..."
              class="w-full p-4 bg-gray-700/80 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-gray-700 transition-all"
            />
            <svg
              class="absolute right-3 top-4 w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              ></path>
            </svg>
          </div>
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length" class="mb-6">
          <h3 class="text-lg mb-3 text-gray-300">Search Results:</h3>
          <div
            class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-80 overflow-y-auto custom-scrollbar"
          >
            <div
              v-for="anime in searchResults"
              :key="anime.mal_id"
              @click="addAnime(anime)"
              class="flex items-center p-4 bg-gray-700/60 rounded-xl cursor-pointer hover:bg-gray-600/80 transition-all duration-200 backdrop-blur-sm border border-gray-600/50 hover:border-purple-500/50"
            >
              <img
                :src="anime.image_url || '/placeholder-anime.jpg'"
                :alt="anime.title"
                class="w-14 h-20 object-cover rounded-lg mr-4 shadow-lg"
                @error="handleImageError"
              />
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate text-white">{{ anime.title }}</div>
                <div class="text-sm text-gray-400 mt-1">
                  {{ anime.year }} • ★ {{ anime.score || 'N/A' }}
                </div>
              </div>
              <div class="text-purple-400 opacity-60 hover:opacity-100 transition-opacity">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                  ></path>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Anime List -->
        <div v-if="selectedAnime.length">
          <h3 class="text-lg mb-3 text-gray-300">Selected Anime ({{ selectedAnime.length }}):</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div
              v-for="anime in selectedAnime"
              :key="anime.mal_id"
              class="flex items-center p-4 bg-gradient-to-r from-gray-700/80 to-gray-600/80 rounded-xl backdrop-blur-sm border border-gray-600/50 shadow-lg"
            >
              <img
                :src="anime.image_url || '/placeholder-anime.jpg'"
                :alt="anime.title"
                class="w-14 h-20 object-cover rounded-lg mr-4 shadow-lg"
                @error="handleImageError"
              />
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate text-white">{{ anime.title }}</div>
                <div class="text-sm text-gray-400 mt-1">
                  {{ anime.year }} • ★ {{ anime.score || 'N/A' }}
                </div>
              </div>
              <button
                @click="removeAnime(anime.mal_id)"
                class="text-red-400 hover:text-red-300 ml-3 p-2 rounded-full hover:bg-red-500/20 transition-all duration-200"
                title="Remove anime"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  ></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="mt-6">
          <button
            @click="generateRecommendations"
            :disabled="selectedAnime.length === 0 || loading"
            class="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
          >
            {{
              loading
                ? 'Generating Recommendations...'
                : selectedAnime.length === 0
                  ? 'Select anime to get recommendations'
                  : `Generate Recommendations (${selectedAnime.length} anime selected)`
            }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div
        v-if="error"
        class="bg-red-900/50 border border-red-500/50 rounded-xl p-4 mb-6 backdrop-blur-sm"
      >
        <div class="text-red-200 flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          {{ error }}
        </div>
      </div>

      <!-- Filter -->
      <div
        v-if="filteredRecommendations.length"
        class="bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 mb-6 shadow-2xl border border-gray-700"
      >
        <h3 class="text-xl font-semibold mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            ></path>
          </svg>
          Filter Options
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <label
            class="flex items-center p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700/70 transition-colors cursor-pointer"
          >
            <input
              v-model="filters.includeSequels"
              type="checkbox"
              class="mr-3 w-4 h-4 rounded bg-gray-600 border-gray-500 text-purple-500 focus:ring-purple-500"
            />
            <span class="text-gray-300">Include Sequels</span>
          </label>
          <label
            class="flex items-center p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700/70 transition-colors cursor-pointer"
          >
            <input
              v-model="filters.showExplanations"
              type="checkbox"
              class="mr-3 w-4 h-4 rounded bg-gray-600 border-gray-500 text-purple-500 focus:ring-purple-500"
            />
            <span class="text-gray-300">Show Explanations</span>
          </label>
          <div class="flex items-center p-3 rounded-lg bg-gray-700/50">
            <label class="mr-3 text-gray-300 font-medium">Min Score:</label>
            <select
              v-model="filters.minScore"
              class="flex-1 bg-gray-600 border-gray-500 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option :value="null">Any</option>
              <option :value="6.0">6.0+</option>
              <option :value="7.0">7.0+</option>
              <option :value="8.0">8.0+</option>
              <option :value="9.0">9.0+</option>
            </select>
          </div>
          <div class="flex items-center p-3 rounded-lg bg-gray-700/50">
            <label class="mr-3 text-gray-300 font-medium">Show:</label>
            <select
              v-model="filters.maxResults"
              class="flex-1 bg-gray-600 border-gray-500 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option :value="12">12 results</option>
              <option :value="24">24 results</option>
              <option :value="36">36 results</option>
              <option :value="48">48 results</option>
              <option :value="60">60 results</option>
              <option :value="100">100 results</option>
              <option :value="150">150 results</option>
              <option :value="200">200 results</option>
            </select>
          </div>
        </div>

        <!-- Active filters summary -->
        <div
          v-if="activeFiltersCount > 0"
          class="mt-4 p-3 bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg border border-purple-500/30"
        >
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-300">
              Active filters:
              <span
                v-if="filters.minScore"
                class="inline-block bg-purple-600/80 px-3 py-1 rounded-full text-xs mr-2 ml-2"
              >
                Score ≥ {{ filters.minScore }}
              </span>
              <span
                v-if="!filters.includeSequels"
                class="inline-block bg-purple-600/80 px-3 py-1 rounded-full text-xs mr-2"
              >
                No sequels
              </span>
            </div>
            <button
              @click="clearFilters"
              class="text-sm text-blue-400 hover:text-blue-300 px-3 py-1 rounded-lg hover:bg-blue-500/20 transition-all"
            >
              Clear all
            </button>
          </div>
        </div>
      </div>

      <!-- Recommendations Section -->
      <div
        v-if="filteredRecommendations.length"
        class="bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 shadow-2xl border border-gray-700"
      >
        <div class="flex justify-between items-center mb-6">
          <h2
            class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400"
          >
            Recommended for You
          </h2>
          <div class="text-sm text-gray-400 bg-gray-700/50 px-4 py-2 rounded-lg">
            Showing {{ filteredRecommendations.length }} recommendations
          </div>
        </div>

        <div
          class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
        >
          <div
            v-for="rec in filteredRecommendations"
            :key="rec.mal_id"
            class="group cursor-pointer transform transition-all duration-300 hover:scale-105"
            @click="handleItemClick(rec)"
          >
            <div
              class="bg-gradient-to-b from-gray-800/80 to-gray-900/80 rounded-xl overflow-hidden backdrop-blur-sm border border-gray-700/50 hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300"
            >
              <!-- Image Container -->
              <div class="relative aspect-[3/4] overflow-hidden">
                <img
                  :src="rec.image_url || '/placeholder-anime.jpg'"
                  :alt="rec.title"
                  class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  @error="handleImageError"
                />

                <div
                  class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                ></div>

                <!-- Type Badge -->
                <div class="absolute top-3 right-3">
                  <span
                    class="px-3 py-1 bg-black/80 backdrop-blur-sm text-white text-xs font-medium rounded-full border border-white/20"
                  >
                    {{ rec.type || 'ANIME' }}
                  </span>
                </div>

                <!-- Score and Similarity -->
                <div class="absolute bottom-3 left-3 flex flex-col gap-2">
                  <span
                    v-if="rec.score"
                    class="px-3 py-1 bg-amber-600/90 backdrop-blur-sm text-white text-xs font-medium rounded-full flex items-center shadow-lg"
                  >
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                      />
                    </svg>
                    {{ formatScore(rec.score) }}
                  </span>

                  <span
                    v-if="rec.similarity"
                    class="px-3 py-1 bg-blue-600/90 backdrop-blur-sm text-white text-xs font-medium rounded-full shadow-lg"
                  >
                    {{ Math.round(rec.similarity) }}% match
                  </span>
                </div>
              </div>

              <!-- Content -->
              <div class="p-4">
                <h3
                  class="font-bold text-white line-clamp-2 mb-2 group-hover:text-purple-300 transition-colors leading-tight"
                >
                  {{ rec.title }}
                </h3>

                <!-- English Title -->
                <p
                  v-if="rec.title_english && rec.title_english !== rec.title"
                  class="text-xs text-gray-400 mb-3 line-clamp-1 opacity-80"
                >
                  {{ rec.title_english }}
                </p>

                <!-- Meta Info -->
                <div class="flex items-center justify-between text-xs text-gray-400 mb-3">
                  <span v-if="rec.year" class="bg-gray-700/50 px-2 py-1 rounded">{{
                    rec.year
                  }}</span>
                  <span v-if="rec.episodes" class="bg-gray-700/50 px-2 py-1 rounded"
                    >{{ rec.episodes }} eps</span
                  >
                </div>

                <!-- Synopsis -->
                <p class="text-sm text-gray-300 mb-3 line-clamp-3 leading-relaxed opacity-90">
                  {{ rec.synopsis || 'No synopsis available.' }}
                </p>

                <!-- Explanation (if enabled) -->
                <div
                  v-if="filters.showExplanations && rec.explanation"
                  class="bg-gradient-to-r from-green-900/30 to-blue-900/30 rounded-lg p-3 mt-3 border border-green-500/30"
                >
                  <p class="text-xs text-green-200 leading-relaxed">
                    {{ rec.explanation }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No results -->
      <div
        v-else-if="allRecommendations.length && !filteredRecommendations.length"
        class="bg-gray-800/90 backdrop-blur-sm rounded-xl p-8 text-center shadow-2xl border border-gray-700"
      >
        <svg
          class="w-16 h-16 mx-auto mb-4 text-gray-500"
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
        <div class="text-gray-300 text-xl mb-2">No recommendations match your current filters</div>
        <div class="text-gray-500 text-sm mb-6">
          Try adjusting your filter criteria to see more results
        </div>
        <button
          @click="clearFilters"
          class="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105"
        >
          Clear Filters
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedAnime = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const allRecommendations = ref([])
const filteredRecommendations = ref([])
const recommendationData = ref(null)
const loading = ref(false)
const error = ref('')

const filters = reactive({
  includeSequels: true,
  showExplanations: true,
  minScore: null,
  maxResults: 24,
})

const formatScore = (score) => {
  if (!score) return 'N/A'
  return parseFloat(score).toFixed(1)
}

const handleItemClick = (rec) => {
  router.push({ name: 'AnimeDetail', params: { id: rec.mal_id } })
}

const updateFilteredRecommendations = () => {
  let filtered = [...allRecommendations.value]

  if (filters.minScore) {
    filtered = filtered.filter((rec) => rec.score && rec.score >= parseFloat(filters.minScore))
  }

  filtered = filtered.slice(0, filters.maxResults)

  filteredRecommendations.value = filtered
}

watch(
  () => [filters.includeSequels, filters.minScore, filters.maxResults],
  () => {
    if (selectedAnime.value.length > 0) {
      generateRecommendations()
    }
  },
)

const activeFiltersCount = ref(0)

const clearFilters = () => {
  filters.minScore = null
  filters.includeSequels = true
  filters.maxResults = 24
  if (selectedAnime.value.length > 0) {
    generateRecommendations()
  }
}

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
    filteredRecommendations.value = []
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
      min_score: filters.minScore ? parseFloat(filters.minScore) : null,
      include_sequels: filters.includeSequels,
      explain: filters.showExplanations,
      diversity_weight: filters.includeSequels ? 0.0 : 0.4,
    })

    if (response.data.erroar) {
      error.value = response.data.error
      allRecommendations.value = []
      filteredRecommendations.value = []
      recommendationData.value = null
    } else {
      allRecommendations.value = response.data.recommendations || []
      updateFilteredRecommendations()
      recommendationData.value = response.data
    }
  } catch (err) {
    console.error('Recommendation error:', err)
    error.value = err.response?.data?.detail || 'Failed to generate recommendations'
    allRecommendations.value = []
    filteredRecommendations.value = []
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

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bg-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  min-height: 100vh;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(55, 65, 81, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(147, 51, 234, 0.5);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 51, 234, 0.7);
}
</style>
