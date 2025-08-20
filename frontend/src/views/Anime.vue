<template>
  <div class="p-4 pt-25 bg-gray-900 min-h-screen text-white">
    <!-- Main Filters -->
    <div class="max-w-6xl mx-auto mb-4">
      <div class="flex flex-wrap items-center gap-4 justify-center">
        <input
          v-model="filters.search"
          @input="resetAnime"
          placeholder="Search anime..."
          class="px-3 py-2 rounded bg-gray-800 text-white placeholder-gray-400 border border-gray-700 focus:border-blue-500 focus:outline-none w-48"
        />

        <select
          v-model="filters.genre"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-32"
        >
          <option value="">Any Genre</option>
          <option v-for="g in filterOptions.genres" :key="g" :value="g">{{ g }}</option>
        </select>

        <select
          v-model="filters.year"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Year</option>
          <option v-for="y in filterOptions.years" :key="y" :value="y">{{ y }}</option>
        </select>

        <select
          v-model="filters.season"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-28"
        >
          <option value="">Season</option>
          <option v-for="s in filterOptions.seasons" :key="s" :value="s">
            {{ capitalize(s) }}
          </option>
        </select>

        <select
          v-model="filters.format"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Type</option>
          <option v-for="f in filterOptions.formats" :key="f" :value="f">{{ f }}</option>
        </select>

        <select
          v-model="filters.status"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-32"
        >
          <option value="">Status</option>
          <option v-for="st in filterOptions.statuses" :key="st" :value="st">{{ st }}</option>
        </select>

        <button
          @click="showAdvanced = !showAdvanced"
          class="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        >
          Advanced
        </button>
      </div>

      <!-- Advanced Filters -->
      <div
        v-if="showAdvanced"
        class="flex flex-wrap items-center gap-2 justify-center mt-2 pt-2 border-t border-gray-700"
      >
        <select
          v-model="filters.min_score"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Score</option>
          <option v-for="sr in filterOptions.score_ranges" :key="sr.min" :value="sr.min">
            {{ sr.label }}
          </option>
        </select>

        <select
          v-model="filters.episode_type"
          @change="resetAnime"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Length</option>
          <option v-for="et in filterOptions.episode_types" :key="et" :value="et">
            {{ capitalize(et) }}
          </option>
        </select>

        <label class="flex items-center space-x-2 text-sm">
          <input
            v-model="filters.completed_only"
            @change="resetAnime"
            type="checkbox"
            class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
          />
          <span>Completed</span>
        </label>

        <span class="text-sm text-gray-400">{{ totalCount || 0 }} results</span>
      </div>
    </div>

    <div v-if="loading && animeList.length === 0" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
      <p class="mt-2 text-gray-400">Loading...</p>
    </div>

    <!-- Anime Grid -->
    <div class="max-w-6xl mx-auto">
      <div
        class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-6 gap-3"
      >
        <div
          v-for="anime in animeList"
          :key="anime.id"
          class="rounded-lg shadow-lg overflow-hidden bg-gray-800 hover:bg-gray-700 transition-colors cursor-pointer"
          @click="openAnimeDetail(anime)"
        >
          <div class="relative">
            <img
              :src="
                anime.image_url || 'https://via.placeholder.com/150x215/374151/9CA3AF?text=No+Image'
              "
              :alt="anime.title"
              class="w-full aspect-[2/3] object-cover"
              @error="handleImageError"
            />

            <div
              v-if="anime.score"
              class="absolute top-1 right-1 bg-blue-600 text-white px-1.5 py-0.5 rounded text-xs font-bold"
            >
              {{ anime.score.toFixed(1) }}
            </div>

            <div
              v-if="anime.episodes"
              class="absolute top-1 left-1 bg-black bg-opacity-70 text-white px-1.5 py-0.5 rounded text-xs"
            >
              {{ anime.episodes }}
            </div>
          </div>

          <div class="p-2">
            <div class="flex items-center justify-between mb-1">
              <span
                :class="['w-2 h-2 rounded-full', getStatusColor(anime.status)]"
                :title="anime.status"
              ></span>
              <span v-if="anime.year" class="text-xs text-gray-400">{{ anime.year }}</span>
            </div>

            <h2 class="font-medium text-xs line-clamp-2 mb-1" :title="anime.title">
              {{ anime.title }}
            </h2>

            <div v-if="anime.genres && anime.genres.length > 0" class="flex flex-wrap gap-1">
              <span
                v-for="genre in anime.genres.slice(0, 2)"
                :key="genre"
                class="text-xs bg-gray-700 px-1.5 py-0.5 rounded"
              >
                {{ genre }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center mt-6">
      <div
        v-if="loading && animeList.length > 0"
        class="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto"
      ></div>
      <p v-else-if="!hasMore && animeList.length > 0" class="text-gray-400 text-sm">
        End of results
      </p>
      <p v-else-if="animeList.length === 0 && !loading" class="text-gray-400">No anime found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const animeList = ref([])
const page = ref(1)
const limit = 30
const loading = ref(false)
const hasMore = ref(true)
const totalCount = ref(0)
const showAdvanced = ref(false)

const getStatusColor = (status) => {
  if (!status) return 'bg-gray-400'
  const s = status.toLowerCase()
  if (s.includes('finished')) return 'bg-red-500'
  if (s.includes('airing') && !s.includes('not yet')) return 'bg-green-500'
  if (s.includes('not yet aired')) return 'bg-orange-500'
  return 'bg-gray-400'
}

const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/150x215/374151/9CA3AF?text=No+Image'
}

const filters = ref({
  search: '',
  genre: '',
  year: '',
  season: '',
  format: '',
  status: '',
  episode_type: '',
  min_score: '',
  completed_only: false,
})

const filterOptions = ref({
  genres: [],
  years: [],
  seasons: [],
  formats: [],
  statuses: [],
  episode_types: [],
  score_ranges: [],
})

const fetchFilters = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/anime/filters')
    filterOptions.value = res.data
  } catch (err) {
    console.error('Error fetching filters:', err)
  }
}

const buildParams = () => {
  const params = { limit, offset: (page.value - 1) * limit }

  if (filters.value.search?.trim()) params.search = filters.value.search.trim()
  if (filters.value.genre) params.genre = filters.value.genre
  if (filters.value.season) params.season = filters.value.season
  if (filters.value.format) params.format = filters.value.format
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.episode_type) params.episode_type = filters.value.episode_type

  if (filters.value.year && filters.value.year !== '') params.year = parseInt(filters.value.year)
  if (filters.value.min_score && filters.value.min_score !== '')
    params.min_score = parseFloat(filters.value.min_score)

  if (filters.value.completed_only) params.completed_only = true

  return params
}

const fetchAnime = async (reset = false) => {
  if (loading.value || (!hasMore.value && !reset)) return
  loading.value = true

  try {
    const params = buildParams()
    const res = await axios.get('http://127.0.0.1:8000/anime', { params })

    if (reset) {
      animeList.value = res.data.results
      page.value = 2
    } else {
      animeList.value.push(...res.data.results)
      page.value += 1
    }

    totalCount.value = res.data.count
    hasMore.value = res.data.pagination?.has_next ?? res.data.results.length === limit
  } catch (err) {
    console.error('Error fetching anime:', err)
  } finally {
    loading.value = false
  }
}

const resetAnime = async () => {
  page.value = 1
  hasMore.value = true
  animeList.value = []
  await fetchAnime(true)
}

const handleScroll = () => {
  if (loading.value || !hasMore.value) return

  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const fullHeight = document.documentElement.scrollHeight

  if (scrollTop + windowHeight + 100 >= fullHeight) {
    fetchAnime()
  }
}

const openAnimeDetail = (anime) => {
  console.log('Selected anime:', anime)
}

onMounted(async () => {
  await fetchFilters()
  await fetchAnime(true)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
