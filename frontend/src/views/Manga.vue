<template>
  <div class="p-4 pt-24 bg-gray-900 min-h-screen text-white">
    <!-- Main Filters -->
    <div class="max-w-6xl mx-auto mb-4">
      <div class="flex flex-wrap items-center gap-4 justify-center">
        <input
          v-model="filters.search"
          @input="resetManga"
          placeholder="Search manga..."
          class="px-3 py-2 rounded bg-gray-800 text-white placeholder-gray-400 border border-gray-700 focus:border-blue-500 focus:outline-none w-48"
        />

        <select
          v-model="filters.genre"
          @change="resetManga"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-32"
        >
          <option value="">Any Genre</option>
          <option v-for="g in filterOptions.genres" :key="g" :value="g">{{ g }}</option>
        </select>

        <select
          v-model="filters.year"
          @change="resetManga"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Year</option>
          <option v-for="y in filterOptions.years" :key="y" :value="y">{{ y }}</option>
        </select>

        <select
          v-model="filters.type"
          @change="resetManga"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-28"
        >
          <option value="">Type</option>
          <option v-for="f in filterOptions.types" :key="f" :value="f">{{ f }}</option>
        </select>

        <select
          v-model="filters.status"
          @change="resetManga"
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
          @change="resetManga"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-24"
        >
          <option value="">Score</option>
          <option v-for="sr in filterOptions.score_ranges" :key="sr.min" :value="sr.min">
            {{ sr.label }}
          </option>
        </select>

        <select
          v-model="filters.demographic"
          @change="resetManga"
          class="px-3 py-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-28"
        >
          <option value="">Demographic</option>
          <option v-for="d in filterOptions.demographics" :key="d" :value="d">{{ d }}</option>
        </select>

        <label class="flex items-center space-x-2 text-sm">
          <input
            v-model="filters.completed_only"
            @change="resetManga"
            type="checkbox"
            class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
          />
          <span>Completed</span>
        </label>

        <label class="flex items-center space-x-2 text-sm">
          <input
            v-model="isOriginalTitle"
            @change="resetManga"
            type="checkbox"
            class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
          />
          <span>English Title</span>
        </label>

        <span class="text-sm text-gray-400">{{ totalCount || 0 }} results</span>
      </div>
    </div>

    <div v-if="loading && mangaList.length === 0" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
      <p class="mt-2 text-gray-400">Loading...</p>
    </div>

    <!-- Manga Grid -->
    <div class="max-w-6xl mx-auto">
      <div
        class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-6 gap-3"
      >
        <div
          v-for="(manga, index) in mangaList"
          :key="manga.mal_id"
          class="group rounded-lg shadow-lg overflow-visible bg-gray-800 hover:bg-gray-700 transition-all duration-300 cursor-pointer relative hover:z-50"
          @click="openMangaDetail(manga)"
        >
          <!-- Image -->
          <div class="relative overflow-hidden rounded-lg">
            <img
              :src="
                manga.image_url || 'https://via.placeholder.com/150x215/374151/9CA3AF?text=No+Image'
              "
              :alt="manga.title"
              class="w-full aspect-[2/3] object-cover"
              @error="handleImageError"
            />
          </div>

          <!-- Title -->
          <div class="p-2">
            <h2 v-if="isOriginalTitle" class="font-medium text-xs line-clamp-2 text-center">
              {{ manga.title_english || manga.title }}
            </h2>
            <h2 v-else class="font-medium text-xs line-clamp-2 text-center">
              {{ manga.title }}
            </h2>
          </div>

          <!-- Hover panel -->
          <div
            :class="[
              'absolute top-0 w-80 bg-gray-800 border border-gray-700 shadow-2xl rounded-lg overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 pointer-events-none',
              index % 6 < 3 ? 'left-full ml-2' : 'right-full mr-2',
            ]"
          >
            <div class="p-4 space-y-3">
              <!-- Title + Score -->
              <div class="flex items-start justify-between">
                <h3 class="font-bold text-white text-lg flex-1 pr-4">
                  {{ isOriginalTitle ? manga.title_english || manga.title : manga.title }}
                </h3>
                <div
                  v-if="manga.score"
                  :class="[
                    'text-white px-2 py-1 rounded text-sm font-bold flex items-center gap-1 flex-shrink-0',
                    getScoreBgColor(manga.score),
                  ]"
                >
                  <span>{{ getScoreIcon(manga.score) }}</span>
                  <span>{{ Math.round(manga.score * 10) }}%</span>
                </div>
              </div>

              <!-- Authors -->
              <div v-if="manga.authors?.length" class="text-gray-300 text-sm">
                By: {{ formatAuthors(manga.authors) }}
              </div>

              <!-- Type + Volumes/Chapters -->
              <div class="text-gray-300 text-sm">
                <span v-if="manga.type">{{ manga.type }}</span>
                <span v-if="manga.chapters"> • {{ manga.chapters }} chapters</span>
                <span v-if="manga.volumes"> • {{ manga.volumes }} vols</span>
              </div>

              <!-- Demographic -->
              <div v-if="manga.demographics?.length" class="text-sm text-gray-300">
                {{ manga.demographics.join(', ') }}
              </div>

              <!-- Genres -->
              <div v-if="manga.genres?.length" class="flex flex-wrap gap-1.5 pt-1">
                <span
                  v-for="genre in manga.genres.slice(0, 4)"
                  :key="genre"
                  :style="{
                    backgroundColor: getMangaGenreColor(manga.mal_id),
                    color: getMangaGenreTextColor(manga.mal_id),
                  }"
                  class="px-3 py-1 text-xs rounded-full font-medium border"
                  :class="
                    getMangaGenreTextColor(manga.mal_id) === '#000000'
                      ? 'border-gray-400'
                      : 'border-gray-600'
                  "
                >
                  {{ genre }}
                </span>
              </div>

              <!-- Status -->
              <div class="pt-1">
                <span
                  :class="[
                    'inline-block px-3 py-1.5 rounded text-sm font-medium',
                    getStatusBgColor(manga.status),
                  ]"
                >
                  {{ manga.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center mt-6">
      <div
        v-if="loading && mangaList.length > 0"
        class="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto"
      ></div>
      <p v-else-if="!hasMore && mangaList.length > 0" class="text-gray-400 text-sm">
        End of results
      </p>
      <p v-else-if="mangaList.length === 0 && !loading" class="text-gray-400">No manga found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const mangaList = ref([])
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

const getScoreIcon = (score) => {
  if (score === null || score === undefined) return '❓'
  const s = Math.round(score * 10)
  if (s >= 81) return '🔥'
  if (s >= 71) return '👍'
  if (s >= 51) return '👌'
  if (s >= 0) return '👎'
  return '❓'
}

const getStatusBgColor = (status) => {
  if (!status) return 'bg-gray-700 text-white'
  const s = status.toLowerCase()
  if (s.includes('finished')) return 'bg-red-600 text-white'
  if (s.includes('publishing')) return 'bg-green-600 text-white'
  if (s.includes('on hiatus')) return 'bg-orange-600 text-white'
  return 'bg-gray-700 text-white'
}

const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/150x215/374151/9CA3AF?text=No+Image'
}

const formatAuthors = (authors) => {
  if (!authors || authors.length === 0) return ''

  const cleanAuthors = authors
    .map((author) => {
      if (typeof author === 'string') {
        if (author.includes(',')) {
          const parts = author.split(',').map((part) => part.trim())
          if (parts.length === 2) {
            return `${parts[1]} ${parts[0]}`
          }
        }
        return author.trim()
      }
      return author
    })
    .filter((author) => author && author.length > 0)

  if (cleanAuthors.length === 0) return ''
  if (cleanAuthors.length === 1) return cleanAuthors[0]
  if (cleanAuthors.length === 2) return `${cleanAuthors[0]} and ${cleanAuthors[1]}`

  const lastAuthor = cleanAuthors[cleanAuthors.length - 1]
  const otherAuthors = cleanAuthors.slice(0, -1)
  return `${otherAuthors.join(', ')}, and ${lastAuthor}`
}

const mangaGenreColors = reactive({})
const genreColorPalette = [
  '#EF4444', // red-500
  '#F97316', // orange-500
  '#EAB308', // yellow-500
  '#22C55E', // green-500
  '#06B6D4', // cyan-500
  '#3B82F6', // blue-500
  '#8B5CF6', // violet-500
  '#EC4899', // pink-500
  '#F59E0B', // amber-500
  '#10B981', // emerald-500
  '#6366F1', // indigo-500
  '#8B5A2B', // brown
  '#84CC16', // lime-500
  '#F472B6', // pink-400
  '#A855F7', // purple-500
  '#14B8A6', // teal-500
  '#DC2626', // red-600
  '#EA580C', // orange-600
  '#16A34A', // green-600
  '#2563EB', // blue-600
]

const getMangaGenreColor = (mangaId) => {
  if (!mangaGenreColors[mangaId]) {
    // Assign a random color to this manga (changes on refresh)
    const randomIndex = Math.floor(Math.random() * genreColorPalette.length)
    mangaGenreColors[mangaId] = genreColorPalette[randomIndex]
  }
  return mangaGenreColors[mangaId]
}

const getMangaGenreTextColor = (mangaId) => {
  const bgColor = getMangaGenreColor(mangaId)
  const r = parseInt(bgColor.slice(1, 3), 16)
  const g = parseInt(bgColor.slice(3, 5), 16)
  const b = parseInt(bgColor.slice(5, 7), 16)

  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

  return luminance > 0.6 ? '#000000' : '#FFFFFF'
}

const filters = ref({
  search: '',
  genre: '',
  year: '',
  type: '',
  status: '',
  demographic: '',
  min_score: '',
  completed_only: false,
})

const filterOptions = ref({
  genres: [],
  years: [],
  types: [],
  statuses: [],
  demographics: [],
  score_ranges: [],
})

const fetchFilters = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/manga/filters')
    filterOptions.value = res.data
  } catch (err) {
    console.error('Error fetching filters:', err)
  }
}

const buildParams = () => {
  const params = { limit, offset: (page.value - 1) * limit }
  if (filters.value.search?.trim()) params.search = filters.value.search.trim()
  if (filters.value.genre) params.genre = filters.value.genre
  if (filters.value.type) params.type = filters.value.type
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.demographic) params.demographic = filters.value.demographic
  if (filters.value.year) params.year = parseInt(filters.value.year)
  if (filters.value.min_score) params.min_score = parseFloat(filters.value.min_score)
  if (filters.value.completed_only) params.completed_only = true
  return params
}

const fetchManga = async (reset = false) => {
  if (loading.value || (!hasMore.value && !reset)) return
  loading.value = true
  try {
    const params = buildParams()
    const res = await axios.get('http://127.0.0.1:8000/manga', { params })
    if (reset) {
      mangaList.value = res.data.results
      page.value = 2
    } else {
      mangaList.value.push(...res.data.results)
      page.value += 1
    }
    totalCount.value = res.data.count
    hasMore.value = res.data.pagination?.has_next ?? res.data.results.length === limit
  } catch (err) {
    console.error('Error fetching manga:', err)
  } finally {
    loading.value = false
  }
  assignColors(mangaList.value)
}

const resetManga = async () => {
  page.value = 1
  hasMore.value = true
  mangaList.value = []
  await fetchManga(true)
}

const handleScroll = () => {
  if (loading.value || !hasMore.value) return
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const fullHeight = document.documentElement.scrollHeight
  if (scrollTop + windowHeight + 100 >= fullHeight) {
    fetchManga()
  }
}

const openMangaDetail = (manga) => {
  router.push({ name: 'MangaDetail', params: { id: manga.mal_id } })
}

const mangaColors = reactive({})
const colors = [
  '#F87171',
  '#FBBF24',
  '#34D399',
  '#60A5FA',
  '#A78BFA',
  '#F472B6',
  '#38BDF8',
  '#FB923C',
  '#4ADE80',
  '#22D3EE',
  '#E879F9',
  '#FACC15',
  '#2DD4BF',
  '#FCA5A5',
  '#FDBA74',
  '#86EFAC',
  '#93C5FD',
  '#C4B5FD',
  '#F9A8D4',
  '#67E8F9',
  '#FDE68A',
]

const getRandomColor = () => colors[Math.floor(Math.random() * colors.length)]
const getContrastColor = (hexColor) => {
  const c = hexColor.charAt(0) === '#' ? hexColor.substring(1) : hexColor
  const r = parseInt(c.substr(0, 2), 16)
  const g = parseInt(c.substr(2, 2), 16)
  const b = parseInt(c.substr(4, 2), 16)
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b
  return luminance > 186 ? 'black' : 'white'
}
const assignColors = (mangaArray) => {
  mangaArray.forEach((manga) => {
    if (!mangaColors[manga.mal_id]) {
      const bg = getRandomColor()
      mangaColors[manga.mal_id] = {
        bg,
        text: getContrastColor(bg),
      }
    }
  })
}

watch(
  mangaList,
  (newList) => {
    if (!newList) return
    assignColors(newList)
  },
  { immediate: true },
)

onMounted(async () => {
  await fetchFilters()
  await fetchManga(true)
  assignColors(mangaList.value)
  window.addEventListener('scroll', handleScroll)
})
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
