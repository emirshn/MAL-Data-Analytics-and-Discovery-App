<template>
  <div class="p-6 pt-20 bg-gray-900 min-h-screen text-white">
    <!-- Filters -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-4">
      <input
        v-model="filters.search"
        @input="fetchAnime"
        placeholder="Search"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white placeholder-gray-400"
      />

      <select
        v-model="filters.genre"
        @change="fetchAnime"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white"
      >
        <option value="">Any Genre</option>
        <option v-for="g in filterOptions.genres" :key="g" :value="g">{{ g }}</option>
      </select>

      <select
        v-model="filters.year"
        @change="fetchAnime"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white"
      >
        <option value="">Any Year</option>
        <option v-for="y in filterOptions.years" :key="y" :value="y">{{ y }}</option>
      </select>

      <select
        v-model="filters.season"
        @change="fetchAnime"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white"
      >
        <option value="">Any Season</option>
        <option v-for="s in filterOptions.seasons" :key="s" :value="s">{{ s }}</option>
      </select>

      <select
        v-model="filters.format"
        @change="fetchAnime"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white"
      >
        <option value="">Any Format</option>
        <option v-for="f in filterOptions.formats" :key="f" :value="f">{{ f }}</option>
      </select>

      <select
        v-model="filters.status"
        @change="fetchAnime"
        class="w-full max-w-[185px] px-3 py-2 rounded bg-gray-800 text-white"
      >
        <option value="">Any Status</option>
        <option v-for="st in filterOptions.statuses" :key="st" :value="st">{{ st }}</option>
      </select>
    </div>

    <!-- Anime Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-1">
      <div
        v-for="anime in animeList"
        :key="anime.mal_id"
        class="rounded-lg shadow-lg overflow-hidden w-full max-w-[185px]"
      >
        <img
          :src="anime.image_url || 'https://via.placeholder.com/185x265?text=No+Image'"
          alt=""
          class="w-full h-[265px] object-cover"
        />
        <div class="p-2 text-left">
          <h2 class="font-semibold text-sm">{{ anime.title }}</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const animeList = ref([])
const page = ref(1)
const limit = 20
const loading = ref(false)
const hasMore = ref(true)

const filters = ref({
  search: '',
  genre: '',
  year: '',
  season: '',
  format: '',
  status: '',
})

const filterOptions = ref({
  genres: [],
  years: [],
  seasons: [],
  formats: [],
  statuses: [],
})

const fetchFilters = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/anime/filters')
    filterOptions.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const fetchAnime = async (reset = false) => {
  if (loading.value || !hasMore.value) return
  loading.value = true

  const offset = (page.value - 1) * limit

  try {
    const res = await axios.get('http://127.0.0.1:8000/anime', {
      params: { ...filters.value, limit, offset },
    })

    if (reset) {
      animeList.value = res.data.results
    } else {
      animeList.value.push(...res.data.results)
    }

    if (res.data.results.length < limit) hasMore.value = false
    else page.value += 1
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Reset anime list when filters change
const resetAnime = async () => {
  page.value = 1
  hasMore.value = true
  await fetchAnime(true)
}

// Infinite scroll handler
const handleScroll = () => {
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const fullHeight = document.documentElement.scrollHeight

  if (scrollTop + windowHeight + 100 >= fullHeight) {
    fetchAnime()
  }
}

onMounted(async () => {
  await fetchFilters()
  await fetchAnime()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
