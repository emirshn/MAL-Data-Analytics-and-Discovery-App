<template>
  <div class="p-4 pt-24 bg-gray-900 min-h-screen text-white">
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

        <label class="flex items-center space-x-2 text-sm">
          <input
            v-model="isOriginalTitle"
            @change="resetAnime"
            type="checkbox"
            class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
          />
          <span>English Title</span>
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
          v-for="(anime, index) in animeList"
          :key="anime.id"
          class="group rounded-lg shadow-lg overflow-visible bg-gray-800 hover:bg-gray-700 transition-all duration-300 cursor-pointer relative hover:z-50"
          @click="openAnimeDetail(anime)"
        >
          <!-- Original card - always visible -->
          <div class="relative overflow-hidden rounded-lg">
            <img
              :src="
                anime.image_url || 'https://via.placeholder.com/150x215/374151/9CA3AF?text=No+Image'
              "
              :alt="anime.title"
              class="w-full aspect-[2/3] object-cover"
              @error="handleImageError"
            />
          </div>

          <!-- Title section -->
          <div class="p-2">
            <h2
              v-if="isOriginalTitle"
              class="font-medium text-xs line-clamp-2 text-center"
              :title="anime.title_english || anime.title"
            >
              {{ anime.title_english || anime.title }}
            </h2>
            <h2 v-else class="font-medium text-xs line-clamp-2 text-center" :title="anime.title">
              {{ anime.title }}
            </h2>
          </div>

          <!-- Hover details panel - Text only Netflix style -->
          <div
            :class="[
              'absolute top-0 w-80 bg-gray-800 border border-gray-700 shadow-2xl rounded-lg overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 pointer-events-none',
              index % 6 < 3 ? 'left-full ml-2' : 'right-full mr-2',
            ]"
          >
            <!-- Content -->
            <div class="p-4 space-y-3">
              <!-- Title and Score -->
              <div class="flex items-start justify-between">
                <h3
                  v-if="isOriginalTitle"
                  class="font-bold text-white text-lg flex-1 pr-4"
                  :title="anime.title_english || anime.title"
                >
                  {{ anime.title_english || anime.title }}
                </h3>
                <h3 v-else class="font-bold text-white text-lg flex-1 pr-4" :title="anime.title">
                  {{ anime.title }}
                </h3>
                <div
                  v-if="anime.score"
                  :class="[
                    'text-white px-2 py-1 rounded text-sm font-bold flex items-center gap-1 flex-shrink-0',
                    getScoreBgColor(anime.score),
                  ]"
                >
                  <span>{{ getScoreIcon(anime.score) }}</span>
                  <span>{{ Math.round(anime.score * 10) }}%</span>
                </div>
              </div>

              <!-- Studio -->
              <div
                v-if="anime.studio"
                :style="{ color: animeColors[anime.id]?.bg || '#374151' }"
                class="filter brightness-125"
              >
                {{ anime.studio }}
              </div>
              <!-- Year and Season -->
              <div v-if="anime.year || anime.season" class="text-gray-300 text-sm">
                <span v-if="anime.season" class="capitalize">{{ anime.season }} - </span>
                <span v-if="anime.year"> {{ anime.year }}</span>
              </div>

              <!-- Format and Episodes -->
              <div class="text-gray-300 text-sm">
                <span v-if="anime.type">{{ anime.type }}</span>
                <span v-if="anime.episodes"> • {{ anime.episodes }} episodes</span>
              </div>

              <!-- Genres as tags -->
              <div
                v-if="anime.genres && anime.genres.length > 0"
                class="flex flex-wrap gap-1.5 pt-1"
              >
                <span
                  v-for="genre in anime.genres.slice(0, 4)"
                  :key="genre"
                  class="px-3 py-1 text-xs rounded-full border border-gray-600 transition-colors"
                  :style="{
                    backgroundColor: animeColors[anime.id]?.bg || '#374151',
                    color: animeColors[anime.id]?.text || 'white',
                  }"
                >
                  {{ genre }}
                </span>
              </div>

              <!-- Status -->
              <div class="pt-1">
                <span
                  :class="[
                    'inline-block px-3 py-1.5 rounded text-sm font-medium',
                    getStatusBgColor(anime.status),
                  ]"
                >
                  {{ anime.status || 'Unknown Status' }}
                </span>
              </div>
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
import { ref, onMounted, onUnmounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const animeList = ref([])
const page = ref(1)
const limit = 30
const loading = ref(false)
const hasMore = ref(true)
const totalCount = ref(0)
const showAdvanced = ref(false)
const isOriginalTitle = ref(false)

const getScoreBgColor = (score) => {
  if (score === null || score === undefined) return 'bg-gray-700 text-white'

  const s = Math.round(score * 10)
  if (s >= 81) return 'bg-green-600'
  if (s >= 71) return 'bg-lime-500'
  if (s >= 51) return 'bg-yellow-600'
  if (s >= 0) return 'bg-red-600'

  return 'bg-gray-700 text-white'
}

const getStatusBgColor = (status) => {
  if (!status) return 'bg-gray-700 text-white'
  const s = status.toLowerCase()
  if (s.includes('finished')) return 'bg-red-600 text-white'
  if (s.includes('airing') && !s.includes('not yet')) return 'bg-green-600 text-white'
  if (s.includes('not yet aired')) return 'bg-orange-600 text-white'
  return 'bg-gray-700 text-white'
}
const getScoreIcon = (score) => {
  if (score === null || score === undefined) return '❓'
  const s = Math.round(score * 10)
  if (s >= 81) return '🔥'
  if (s >= 71) return '👍'
  if (s >= 51) return '👌'
  if (s >= 0) return '👎'
  return '❓'
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
  assignColors(animeList.value)
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
  router.push({ name: 'AnimeDetail', params: { id: anime.id } })
}

const animeColors = reactive({})

const colors = [
  '#F87171', // red-400
  '#FBBF24', // amber-400
  '#34D399', // green-400
  '#60A5FA', // blue-400
  '#A78BFA', // purple-400
  '#F472B6', // pink-400
  '#38BDF8', // sky-400
  '#FB923C', // orange-400
  '#4ADE80', // emerald-400
  '#22D3EE', // cyan-400
  '#E879F9', // fuchsia-400
  '#FACC15', // yellow-400
  '#2DD4BF', // teal-400
  '#FCA5A5', // red-300
  '#FDBA74', // orange-300
  '#86EFAC', // green-300
  '#93C5FD', // blue-300
  '#C4B5FD', // violet-300
  '#F9A8D4', // pink-300
  '#67E8F9', // cyan-300
  '#FDE68A', // yellow-300
]

const getRandomColor = () => {
  return colors[Math.floor(Math.random() * colors.length)]
}

const getContrastColor = (hexColor) => {
  const c = hexColor.charAt(0) === '#' ? hexColor.substring(1) : hexColor
  const r = parseInt(c.substr(0, 2), 16)
  const g = parseInt(c.substr(2, 2), 16)
  const b = parseInt(c.substr(4, 2), 16)
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b
  return luminance > 186 ? 'black' : 'white'
}

const assignColors = (animeArray) => {
  animeArray.forEach((anime) => {
    if (!animeColors[anime.id]) {
      const bg = getRandomColor()
      animeColors[anime.id] = {
        bg,
        text: getContrastColor(bg),
      }
    }
  })
}

watch(
  animeList,
  (newList) => {
    if (!newList) return
    assignColors(newList)
  },
  { immediate: true },
)

onMounted(async () => {
  await fetchFilters()
  await fetchAnime(true)
  assignColors(animeList.value)
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
