<template>
  <div class="pt-20 min-h-screen text-white relative bg-container overflow-hidden">
    <div class="absolute inset-0 grid-container">
      <div class="grid-layer-1"></div>
      <div class="grid-layer-2"></div>
    </div>

    <div class="relative z-10 max-w-6xl mx-auto">
      <div v-if="loading" class="text-center">
        <div class="animate-pulse">
          <div class="text-lg">Loading anime details...</div>
          <div
            class="mt-4 w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"
          ></div>
        </div>
      </div>

      <div v-else-if="error" class="text-center text-red-400">
        <div class="text-lg">{{ error }}</div>
        <button
          @click="retryLoad"
          class="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>

      <div v-else-if="anime" class="space-y-8">
        <!-- Hero Section with Cover + Main Info -->
        <AnimeHero :anime="anime" />

        <!-- Synopsis Section -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h2 class="text-2xl font-semibold mb-4 text-blue-400 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              ></path>
            </svg>
            Synopsis
          </h2>
          <div class="prose prose-invert max-w-none">
            <p class="text-gray-300 leading-relaxed text-base">
              {{ anime.synopsis || anime.background || 'No synopsis available.' }}
            </p>
          </div>
        </div>

        <!-- Air Dates and Production Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Broadcast Information -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-green-400">Broadcast Information</h3>
            <div class="space-y-3 text-sm">
              <div v-if="anime.year" class="flex justify-between">
                <span class="text-gray-400">Year:</span>
                <span class="font-medium">{{ anime.year }}</span>
              </div>
              <div v-if="anime.season" class="flex justify-between">
                <span class="text-gray-400">Season:</span>
                <span class="font-medium capitalize">{{ anime.season }}</span>
              </div>
              <div v-if="anime.aired" class="flex justify-between">
                <span class="text-gray-400">Aired:</span>
                <span class="font-medium">{{ getAiredString() }}</span>
              </div>
              <div v-if="getBroadcastDay()" class="flex justify-between">
                <span class="text-gray-400">Broadcast Day:</span>
                <span class="font-medium">{{ getBroadcastDay() }}</span>
              </div>
              <div v-if="getBroadcastTime()" class="flex justify-between">
                <span class="text-gray-400">Broadcast Time:</span>
                <span class="font-medium">{{ getBroadcastTime() }}</span>
              </div>
              <div v-if="anime.airing !== undefined" class="flex justify-between">
                <span class="text-gray-400">Currently Airing:</span>
                <span class="font-medium" :class="anime.airing ? 'text-green-400' : 'text-red-400'">
                  {{ anime.airing ? 'Yes' : 'No' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Production Information -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-orange-400">Production</h3>
            <div class="space-y-3 text-sm">
              <div v-if="getStudiosList().length" class="space-y-1">
                <span class="text-gray-400 block">Studios:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="studio in getStudiosList()"
                    :key="studio"
                    class="px-2 py-1 bg-orange-600 rounded text-xs"
                  >
                    {{ studio }}
                  </span>
                </div>
              </div>
              <div v-if="getProducersList().length" class="space-y-1">
                <span class="text-gray-400 block">Producers:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="producer in getProducersList()"
                    :key="producer"
                    class="px-2 py-1 bg-gray-600 rounded text-xs"
                  >
                    {{ producer }}
                  </span>
                </div>
              </div>
              <div v-if="getLicensorsList().length" class="space-y-1">
                <span class="text-gray-400 block">Licensors:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="licensor in getLicensorsList()"
                    :key="licensor"
                    class="px-2 py-1 bg-indigo-600 rounded text-xs"
                  >
                    {{ licensor }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Categories Section -->
        <div class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TagSection
              v-if="getGenresList().length"
              label="Genres"
              :items="getGenresList()"
              color="blue"
            />

            <TagSection
              v-if="getThemesList().length"
              label="Themes"
              :items="getThemesList()"
              color="purple"
            />
          </div>

          <div v-if="getDemographicsList().length" class="grid grid-cols-1 gap-6">
            <TagSection label="Demographics" :items="getDemographicsList()" color="green" />
          </div>
        </div>

        <!-- Statistics and Scores -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Detailed Scores -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-yellow-400">Ratings & Statistics</h3>
            <div class="space-y-3">
              <div v-if="anime.scored_by" class="flex justify-between text-sm">
                <span class="text-gray-400">Scored by:</span>
                <span class="font-medium">{{ formatNumber(anime.scored_by) }} users</span>
              </div>
              <div v-if="anime.favorites" class="flex justify-between text-sm">
                <span class="text-gray-400">Favorited by:</span>
                <span class="font-medium">{{ formatNumber(anime.favorites) }} users</span>
              </div>
              <div v-if="anime.members" class="flex justify-between text-sm">
                <span class="text-gray-400">Total Members:</span>
                <span class="font-medium">{{ formatNumber(anime.members) }} users</span>
              </div>
            </div>
          </div>

          <!-- Additional Details -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-cyan-400">Additional Details</h3>
            <div class="space-y-3 text-sm">
              <div v-if="anime.approved !== undefined" class="flex justify-between">
                <span class="text-gray-400">Approved:</span>
                <span
                  class="font-medium"
                  :class="anime.approved ? 'text-green-400' : 'text-red-400'"
                >
                  {{ anime.approved ? 'Yes' : 'No' }}
                </span>
              </div>
              <div v-if="anime.mal_id" class="flex justify-between">
                <span class="text-gray-400">MAL ID:</span>
                <span class="font-medium">{{ anime.mal_id }}</span>
              </div>
            </div>
          </div>
        </div>

        <RelatedInfo
          v-if="anime"
          :anime="anime"
          :relationImages="relationImages"
          @relationImageError="handleRelationImageError"
          @entryClick="openAnimeDetail"
        />

        <AiRecommendation
          v-if="anime"
          :recommendations="aiRecommendations"
          :loading="loadingRecommendations"
          :filters="recommendationFilters"
          content-type="anime"
          @filters-changed="onFiltersChanged"
          @item-click="openAnimeDetail"
          @image-error="handleRecommendationImageError"
          @reset-filters="resetRecommendationFilters"
        />

        <!-- Opening & Ending Themes -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-if="getOpeningThemes().length" class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-emerald-400 flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                ></path>
              </svg>
              Opening Themes
            </h3>
            <div class="space-y-2">
              <div
                v-for="opening in getOpeningThemes()"
                :key="opening"
                class="bg-gray-900 p-3 rounded text-sm"
              >
                {{ opening }}
              </div>
            </div>
          </div>

          <div v-if="getEndingThemes().length" class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-teal-400 flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                ></path>
              </svg>
              Ending Themes
            </h3>
            <div class="space-y-2">
              <div
                v-for="ending in getEndingThemes()"
                :key="ending"
                class="bg-gray-900 p-3 rounded text-sm"
              >
                {{ ending }}
              </div>
            </div>
          </div>
        </div>

        <!-- Trailer Section -->
        <div v-if="anime.trailer && anime.trailer.youtube_id" class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-red-400 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              ></path>
            </svg>
            Official Trailer
          </h3>
          <div class="aspect-video">
            <iframe
              :src="getTrailerUrl(anime.trailer)"
              class="w-full h-full rounded-lg"
              frameborder="0"
              allowfullscreen
            ></iframe>
          </div>
        </div>

        <!-- Streaming Platforms -->
        <div v-if="getStreamingPlatforms().length" class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-red-400 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              ></path>
            </svg>
            Streaming Platforms
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <a
              v-for="platform in getStreamingPlatforms()"
              :key="platform.name"
              :href="platform.url"
              target="_blank"
              class="bg-gray-600 bg-opacity-20 border border-gray-600 rounded-lg p-3 text-center hover:bg-gray-600 hover:bg-opacity-30 transition-colors cursor-pointer"
            >
              <span class="text-white-400 font-medium">{{ platform.name }}</span>
            </a>
          </div>
        </div>

        <!-- External Links -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-indigo-400">External Links</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Main Links -->
            <a
              v-if="anime.url"
              :href="anime.url"
              target="_blank"
              class="flex items-center px-4 py-3 bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                ></path>
              </svg>
              MyAnimeList
            </a>

            <a
              v-if="anime.trailer && anime.trailer.url"
              :href="anime.trailer.url"
              target="_blank"
              class="flex items-center px-4 py-3 bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                ></path>
              </svg>
              Watch Trailer
            </a>

            <!-- External links from the external array -->
            <a
              v-for="link in anime.external || []"
              :key="link.name"
              :href="link.url"
              target="_blank"
              class="flex items-center px-4 py-3 bg-gray-600 rounded-lg hover:bg-gray-500 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                ></path>
              </svg>
              <span class="truncate">{{ link.name }}</span>
            </a>
          </div>
        </div>

        <!-- Debug Section -->
        <div class="bg-gray-800 rounded-xl p-6">
          <button
            @click="showDebug = !showDebug"
            class="flex items-center text-gray-400 hover:text-white transition-colors mb-4"
          >
            <svg
              class="w-5 h-5 mr-2"
              :class="{ 'rotate-90': showDebug }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
            {{ showDebug ? 'Hide' : 'Show' }} Raw Data
          </button>
          <div v-if="showDebug" class="bg-black bg-opacity-50 rounded-lg p-4 overflow-auto">
            <pre class="text-xs text-green-400 whitespace-pre-wrap">{{
              JSON.stringify(anime, null, 2)
            }}</pre>
          </div>
        </div>
      </div>

      <div v-else class="text-center text-gray-400 py-20">
        <svg
          class="w-24 h-24 mx-auto mb-4 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          ></path>
        </svg>
        <div class="text-xl font-semibold mb-2">Anime Not Found</div>
        <p class="text-gray-500">The requested anime could not be found in our database.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import TagSection from '@/components/common/TagSection.vue'
import RelatedInfo from '@/components/common/RelatedInfo.vue'
import AnimeHero from '@/components/anime/AnimeHero.vue'
import AiRecommendation from '@/components/common/AiRecommendation.vue'

const route = useRoute()
const anime = ref(null)
const loading = ref(true)
const error = ref(null)
const showDebug = ref(false)
const relationImages = ref({})

const aiRecommendations = ref([])
const loadingRecommendations = ref(false)
const recommendationFilters = ref({
  includeSequels: false,
  showExplanations: true,
  minScore: '',
})

// Concurrency control for relation images
const MAX_CONCURRENT = 4
const queue = []
let active = 0
let cancelled = false

function enqueueRelationEntry(entry) {
  if (relationImages.value[entry.mal_id]) return
  queue.push(entry)
  runNext()
}

function startRelationImageFetch() {
  if (!anime.value?.relations) return
  for (const relation of anime.value.relations) {
    for (const entry of relation.entry) {
      enqueueRelationEntry(entry)
    }
  }
}

async function runNext() {
  if (cancelled || active >= MAX_CONCURRENT) return
  const entry = queue.shift()
  if (!entry) return

  active++
  try {
    await loadRelationImage(entry)
  } finally {
    active--
    if (queue.length) runNext()
  }
}

const onFiltersChanged = (filterUpdate) => {
  console.log('Filters changed:', filterUpdate)

  Object.assign(recommendationFilters.value, filterUpdate)

  fetchAIRecommendations()
}

const handleRecommendationImageError = (event, recommendation) => {
  console.log('Recommendation image error:', recommendation)
  event.target.src = '/api/placeholder/160/213'
}

const resetRecommendationFilters = () => {
  console.log('Resetting filters')
  recommendationFilters.value = {
    includeSequels: false,
    showExplanations: true,
    minScore: '',
  }
  fetchAIRecommendations()
}

watch(
  () => anime.value?.mal_id,
  (newId) => {
    console.log('Anime mal_id changed:', newId)
    if (newId) {
      fetchAIRecommendations()
    }
  },
  { immediate: true },
)

async function fetchAIRecommendations() {
  if (!anime.value?.mal_id) return

  loadingRecommendations.value = true
  try {
    const params = new URLSearchParams({
      limit: '12',
      include_sequels: recommendationFilters.value.includeSequels.toString(),
      explain: recommendationFilters.value.showExplanations.toString(),
    })

    if (recommendationFilters.value.minScore) {
      params.append('min_score', recommendationFilters.value.minScore)
    }

    const response = await fetch(
      `http://127.0.0.1:8000/anime/${anime.value.mal_id}/recommend?${params}`,
    )
    const data = await response.json()

    if (response.ok) {
      aiRecommendations.value = data.recommendations
    } else {
      console.error('Failed to fetch recommendations:', data)
      aiRecommendations.value = []
    }
  } catch (error) {
    console.error('Error fetching AI recommendations:', error)
    aiRecommendations.value = []
  } finally {
    loadingRecommendations.value = false
  }
}

function openAnimeDetail(item) {
  let id, type

  if (item.entry) {
    id = item.entry.mal_id
    type = item.entry.type
  } else {
    id = item.mal_id || item.id
    type = item.type || 'anime'
  }

  if (!id) {
    console.error('Unable to determine ID from:', item)
    return
  }

  if (type.toLowerCase() === 'manga') {
    window.location.href = `/manga/${id}`
  } else {
    window.location.href = `/anime/${id}`
  }
}

const getAiredString = () => {
  if (!anime.value?.aired) return 'N/A'

  if (anime.value.aired.string) {
    return anime.value.aired.string
  }

  const from = anime.value.aired.from
  const to = anime.value.aired.to

  if (!from && !to) return 'N/A'
  if (!to) return `${formatDate(from)} - ?`
  if (!from) return `? - ${formatDate(to)}`

  const fromDate = formatDate(from)
  const toDate = formatDate(to)

  if (fromDate === toDate) return fromDate
  return `${fromDate} - ${toDate}`
}

// Helper function to get broadcast day
const getBroadcastDay = () => {
  return anime.value?.broadcast?.day || null
}

// Helper function to get broadcast time
const getBroadcastTime = () => {
  if (!anime.value?.broadcast) return null

  const time = anime.value.broadcast.time
  const timezone = anime.value.broadcast.timezone

  if (time && timezone) {
    return `${time} (${timezone})`
  }
  if (time) {
    return time
  }

  return anime.value.broadcast.string || null
}

// Helper function to get studios list
const getStudiosList = () => {
  if (!anime.value?.studios || !Array.isArray(anime.value.studios)) return []
  return anime.value.studios.map((studio) => studio.name).filter((name) => name)
}

// Helper function to get producers list
const getProducersList = () => {
  if (!anime.value?.producers || !Array.isArray(anime.value.producers)) return []
  return anime.value.producers.map((producer) => producer.name).filter((name) => name)
}

// Helper function to get licensors list
const getLicensorsList = () => {
  if (!anime.value?.licensors || !Array.isArray(anime.value.licensors)) return []
  return anime.value.licensors.map((licensor) => licensor.name).filter((name) => name)
}

// Helper function to get genres list
const getGenresList = () => {
  if (!anime.value?.genres || !Array.isArray(anime.value.genres)) return []
  return anime.value.genres.map((genre) => genre.name).filter((name) => name)
}

// Helper function to get themes list
const getThemesList = () => {
  if (!anime.value?.themes || !Array.isArray(anime.value.themes)) return []
  return anime.value.themes.map((theme) => theme.name).filter((name) => name)
}

// Helper function to get demographics list
const getDemographicsList = () => {
  if (!anime.value?.demographics || !Array.isArray(anime.value.demographics)) return []
  return anime.value.demographics.map((demo) => demo.name).filter((name) => name)
}

// Helper function to get opening themes
const getOpeningThemes = () => {
  if (!anime.value?.theme?.openings || !Array.isArray(anime.value.theme.openings)) return []
  return anime.value.theme.openings
}

// Helper function to get ending themes
const getEndingThemes = () => {
  if (!anime.value?.theme?.endings || !Array.isArray(anime.value.theme.endings)) return []
  return anime.value.theme.endings
}

// Helper function to get streaming platforms
const getStreamingPlatforms = () => {
  if (!anime.value?.streaming || !Array.isArray(anime.value.streaming)) return []
  return anime.value.streaming
}

// Handle image error for relation images
const handleRelationImageError = (entry) => {
  if (relationImages.value[entry.mal_id]) {
    delete relationImages.value[entry.mal_id]
  }
}

// Utility: wait
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// Load relation image with retry
const loadRelationImage = async (entry) => {
  try {
    const baseUrl = 'http://127.0.0.1:8000'
    const endpoint =
      entry.type === 'anime'
        ? `${baseUrl}/anime/${entry.mal_id}/image`
        : entry.type === 'manga'
          ? `${baseUrl}/manga/${entry.mal_id}/image`
          : null

    if (!endpoint) return

    const response = await axios.get(endpoint)
    if (response.data?.image_url && !cancelled) {
      relationImages.value[entry.mal_id] = response.data.image_url
    }
  } catch (error) {
    if (error.response?.status === 429) {
      console.warn(`429 for ${entry.type} ${entry.mal_id}, retrying...`)
      await sleep(1200)
      return loadRelationImage(entry)
    }
    console.log(`Failed image for ${entry.type} ${entry.mal_id}:`, error)
  }
}

const formatNumber = (num) => {
  if (!num) return 'N/A'
  return parseInt(num).toLocaleString()
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

const getTrailerUrl = (trailer) => {
  if (!trailer || !trailer.youtube_id) return ''

  return `https://www.youtube.com/embed/${trailer.youtube_id}?enablejsapi=1&wmode=opaque`
}

const loadAnime = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('Fetching anime with ID:', route.params.id)
    const response = await axios.get(`http://127.0.0.1:8000/anime/${route.params.id}`)
    console.log('Full API Response:', response.data)

    if (response.data && response.data.error) {
      error.value = response.data.error
    } else {
      let animeData = null

      if (response.data.anime) {
        console.log('Using response.data.anime')
        animeData = response.data.anime
      } else if (response.data.data) {
        console.log('Using response.data.data')
        animeData = response.data.data
      } else {
        console.log('Using response.data directly')
        animeData = response.data
      }

      if (response.data.recommendations && !animeData.recommendations) {
        console.log('Adding recommendations from top level')
        animeData.recommendations = response.data.recommendations
      }

      console.log('Final anime data recommendations:', animeData.recommendations?.length || 0)

      anime.value = animeData

      nextTick(() => startRelationImageFetch())
    }
  } catch (err) {
    console.error('Error fetching anime detail:', err)

    if (err.response) {
      error.value = `Error ${err.response.status}: ${err.response.data?.detail || 'Failed to load anime'}`
    } else if (err.request) {
      error.value = 'Network error: Could not connect to server'
    } else {
      error.value = 'An unexpected error occurred'
    }
  } finally {
    loading.value = false
  }
}

const retryLoad = () => {
  loadAnime()
}

onMounted(() => {
  loadAnime()
})
onBeforeUnmount(() => {
  cancelled = true
  queue.length = 0
})
</script>

<style scoped>
.bg-container {
  background:
    radial-gradient(ellipse at top, rgba(59, 130, 246, 0.15) 0%, rgba(17, 24, 39, 1) 70%),
    linear-gradient(135deg, #111827 0%, #1f2937 100%);
}

.grid-container {
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.grid-layer-1 {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, rgba(59, 130, 246, 0.3) 1px, transparent 1px),
    linear-gradient(rgba(147, 51, 234, 0.2) 1px, transparent 1px);
  background-size: 15px 15px;
  opacity: 0.2;
  animation: gridTransform1 8s ease-in-out infinite alternate;
  mask: linear-gradient(
    to right,
    transparent 0%,
    rgba(255, 255, 255, 0.4) 25%,
    rgba(255, 255, 255, 0.8) 75%,
    rgba(255, 255, 255, 1) 100%
  );
  width: 120%;
  left: -10%;
}

.grid-layer-2 {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, rgba(59, 130, 246, 0.2) 1px, transparent 1px),
    linear-gradient(rgba(147, 51, 234, 0.2) 1px, transparent 1px);
  background-size: 35px 35px;
  opacity: 0.1;
  animation: gridTransform2 10s ease-in-out infinite alternate-reverse;
  mask: linear-gradient(to right, transparent 30%, white 100%);
  width: 130%;
  left: -15%;
}

@keyframes gridTransform1 {
  0% {
    background-size: 15px 15px;
    background-image:
      linear-gradient(90deg, rgba(59, 130, 246, 0.2) 1px, transparent 1px),
      linear-gradient(rgba(147, 51, 234, 0.15) 1px, transparent 1px);
    transform: translateX(0) scale(0.9);
    opacity: 0.2;
  }
  50% {
    background-size: 25px 20px;
    background-image:
      linear-gradient(90deg, rgba(99, 102, 241, 0.35) 1px, transparent 1px),
      linear-gradient(rgba(168, 85, 247, 0.25) 1px, transparent 1px);
    transform: translateX(5%) scale(1.05);
    opacity: 0.3;
  }
  100% {
    background-size: 45px 35px;
    background-image:
      linear-gradient(90deg, rgba(147, 51, 234, 0.4) 1px, transparent 1px),
      linear-gradient(rgba(236, 72, 153, 0.35) 1px, transparent 1px);
    transform: translateX(8%) scale(1.1);
    opacity: 0.4;
  }
}

@keyframes gridTransform2 {
  0% {
    background-size: 35px 35px;
    background-image:
      linear-gradient(90deg, rgba(59, 130, 246, 0.15) 1px, transparent 1px),
      linear-gradient(rgba(147, 51, 234, 0.1) 1px, transparent 1px);
    transform: translateX(0) scale(1);
    opacity: 0.1;
  }
  50% {
    background-size: 50px 45px;
    background-image:
      linear-gradient(90deg, rgba(79, 70, 229, 0.25) 1px, transparent 1px),
      linear-gradient(rgba(139, 92, 246, 0.2) 1px, transparent 1px);
    transform: translateX(5%) scale(1.1);
    opacity: 0.2;
  }
  100% {
    background-size: 75px 60px;
    background-image:
      linear-gradient(90deg, rgba(168, 85, 247, 0.3) 1px, transparent 1px),
      linear-gradient(rgba(217, 70, 239, 0.25) 1px, transparent 1px);
    transform: translateX(10%) scale(1.2);
    opacity: 0.25;
  }
}
:deep(.scrollbar-hide)::-webkit-scrollbar {
  display: none;
}
:deep(.scrollbar-hide) {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
