<template>
  <div class="p-6 pt-20 bg-gray-900 min-h-screen text-white max-w-6xl mx-auto">
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
      <div class="relative bg-gradient-to-r from-gray-800 via-gray-900 to-black rounded-xl p-6">
        <div class="flex flex-col lg:flex-row gap-8">
          <div class="flex-shrink-0">
            <img
              :src="anime.image_url || anime.thumbnail_url || '/placeholder-anime.jpg'"
              :alt="anime.title || 'Anime Cover'"
              class="w-64 h-80 rounded-lg shadow-2xl object-cover mx-auto lg:mx-0"
              @error="handleImageError"
            />
          </div>

          <div class="flex-1 space-y-4">
            <div>
              <h1 class="text-4xl font-bold mb-2">{{ anime.title || 'Unknown Title' }}</h1>
              <p
                v-if="anime.title_english && anime.title_english !== anime.title"
                class="text-gray-300 text-xl"
              >
                {{ anime.title_english }}
              </p>
              <p v-if="anime.title_japanese" class="text-gray-400 text-lg">
                {{ anime.title_japanese }}
              </p>
              <p v-if="anime.title_synonyms" class="text-gray-500 text-sm">
                <strong>Also known as:</strong> {{ anime.title_synonyms }}
              </p>
            </div>

            <!-- Key Stats Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div
                v-if="anime.score"
                class="bg-yellow-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-yellow-400 text-2xl font-bold">
                  ★ {{ formatScore(anime.score) }}
                </div>
                <div class="text-xs text-white-400">Score</div>
              </div>
              <div v-if="anime.rank" class="bg-purple-600 bg-opacity-20 p-3 rounded-lg text-center">
                <div class="text-purple-400 text-2xl font-bold">#{{ anime.rank }}</div>
                <div class="text-xs text-white-400">Rank</div>
              </div>
              <div
                v-if="anime.popularity"
                class="bg-green-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-green-400 text-2xl font-bold">#{{ anime.popularity }}</div>
                <div class="text-xs text-white-700">Popularity</div>
              </div>
              <div
                v-if="anime.members"
                class="bg-blue-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-blue-400 text-2xl font-bold">
                  {{ formatNumber(anime.members) }}
                </div>
                <div class="text-xs text-white-400">Members</div>
              </div>
            </div>

            <!-- Basic Info Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div v-if="anime.type" class="flex justify-between">
                <span class="text-gray-400">Type:</span>
                <span class="font-medium">{{ anime.type }}</span>
              </div>
              <div v-if="anime.episodes" class="flex justify-between">
                <span class="text-gray-400">Episodes:</span>
                <span class="font-medium">{{ anime.episodes }}</span>
              </div>
              <div v-if="anime.status" class="flex justify-between">
                <span class="text-gray-400">Status:</span>
                <span class="font-medium" :class="getStatusColor(anime.status)">{{
                  anime.status
                }}</span>
              </div>
              <div v-if="anime.duration" class="flex justify-between">
                <span class="text-gray-400">Duration:</span>
                <span class="font-medium">{{ anime.duration }}</span>
              </div>
              <div v-if="anime.rating" class="flex justify-between">
                <span class="text-gray-400">Rating:</span>
                <span class="font-medium">{{ anime.rating }}</span>
              </div>
              <div v-if="anime.source" class="flex justify-between">
                <span class="text-gray-400">Source:</span>
                <span class="font-medium">{{ anime.source }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

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
            {{
              anime.synopsis || anime.synopsis_short || anime.background || 'No synopsis available.'
            }}
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
            <div v-if="anime.aired_from || anime.aired_to" class="flex justify-between">
              <span class="text-gray-400">Aired:</span>
              <span class="font-medium">
                {{ formatDateRange(anime.aired_from, anime.aired_to) }}
              </span>
            </div>
            <div v-if="anime.broadcast_day" class="flex justify-between">
              <span class="text-gray-400">Broadcast Day:</span>
              <span class="font-medium">{{ anime.broadcast_day }}</span>
            </div>
            <div v-if="anime.broadcast_time" class="flex justify-between">
              <span class="text-gray-400">Broadcast Time:</span>
              <span class="font-medium">{{ anime.broadcast_time }}</span>
            </div>
          </div>
        </div>

        <!-- Production Information -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-orange-400">Production</h3>
          <div class="space-y-3 text-sm">
            <div v-if="anime.studios && anime.studios.length" class="space-y-1">
              <span class="text-gray-400 block">Studios:</span>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="studio in anime.studios"
                  :key="studio"
                  class="px-2 py-1 bg-orange-600 rounded text-xs"
                >
                  {{ studio }}
                </span>
              </div>
            </div>
            <div v-if="anime.producers && anime.producers.length" class="space-y-1">
              <span class="text-gray-400 block">Producers:</span>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="producer in anime.producers"
                  :key="producer"
                  class="px-2 py-1 bg-gray-600 rounded text-xs"
                >
                  {{ producer }}
                </span>
              </div>
            </div>
            <div v-if="anime.licensors && anime.licensors.length" class="space-y-1">
              <span class="text-gray-400 block">Licensors:</span>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="licensor in anime.licensors"
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Genres -->
        <div v-if="anime.genres && anime.genres.length" class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-blue-400">Genres</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="genre in anime.genres"
              :key="genre"
              class="px-3 py-1 rounded-full bg-blue-600 text-white text-sm hover:bg-blue-700 transition-colors cursor-pointer"
            >
              {{ genre }}
            </span>
          </div>
        </div>

        <!-- Themes -->
        <div v-if="anime.themes && anime.themes.length" class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-purple-400">Themes</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="theme in anime.themes"
              :key="theme"
              class="px-3 py-1 rounded-full bg-purple-600 text-white text-sm hover:bg-purple-700 transition-colors cursor-pointer"
            >
              {{ theme }}
            </span>
          </div>
        </div>

        <!-- Demographics -->
        <div
          v-if="anime.demographics && anime.demographics.length"
          class="bg-gray-800 rounded-xl p-6"
        >
          <h3 class="text-xl font-semibold mb-4 text-green-400">Demographics</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="demo in anime.demographics"
              :key="demo"
              class="px-3 py-1 rounded-full bg-green-600 text-white text-sm hover:bg-green-700 transition-colors cursor-pointer"
            >
              {{ demo }}
            </span>
          </div>
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
            <div v-if="anime.watching" class="flex justify-between text-sm">
              <span class="text-gray-400">Currently Watching:</span>
              <span class="font-medium">{{ formatNumber(anime.watching) }} users</span>
            </div>
            <div v-if="anime.completed" class="flex justify-between text-sm">
              <span class="text-gray-400">Completed:</span>
              <span class="font-medium">{{ formatNumber(anime.completed) }} users</span>
            </div>
            <div v-if="anime.on_hold" class="flex justify-between text-sm">
              <span class="text-gray-400">On Hold:</span>
              <span class="font-medium">{{ formatNumber(anime.on_hold) }} users</span>
            </div>
            <div v-if="anime.dropped" class="flex justify-between text-sm">
              <span class="text-gray-400">Dropped:</span>
              <span class="font-medium">{{ formatNumber(anime.dropped) }} users</span>
            </div>
            <div v-if="anime.plan_to_watch" class="flex justify-between text-sm">
              <span class="text-gray-400">Plan to Watch:</span>
              <span class="font-medium">{{ formatNumber(anime.plan_to_watch) }} users</span>
            </div>
          </div>
        </div>

        <!-- Additional Details -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-cyan-400">Additional Details</h3>
          <div class="space-y-3 text-sm">
            <div v-if="anime.approved" class="flex justify-between">
              <span class="text-gray-400">Status:</span>
              <span class="text-green-400 font-medium">✓ Approved</span>
            </div>
            <div v-if="anime.mal_id" class="flex justify-between">
              <span class="text-gray-400">MAL ID:</span>
              <span class="font-medium">{{ anime.mal_id }}</span>
            </div>
            <div v-if="anime.created_at" class="flex justify-between">
              <span class="text-gray-400">Added:</span>
              <span class="font-medium">{{ formatDate(anime.created_at) }}</span>
            </div>
            <div v-if="anime.updated_at" class="flex justify-between">
              <span class="text-gray-400">Last Updated:</span>
              <span class="font-medium">{{ formatDate(anime.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Streaming Platforms -->
      <div
        v-if="anime.streaming_platforms && anime.streaming_platforms.length"
        class="bg-gray-800 rounded-xl p-6"
      >
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
          <div
            v-for="platform in anime.streaming_platforms"
            :key="platform"
            class="bg-red-600 bg-opacity-20 border border-red-600 rounded-lg p-3 text-center hover:bg-red-600 hover:bg-opacity-30 transition-colors cursor-pointer"
          >
            <span class="text-red-400 font-medium">{{ platform }}</span>
          </div>
        </div>
      </div>

      <!-- External Links -->
      <div class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-xl font-semibold mb-4 text-indigo-400">External Links</h3>
        <div class="flex flex-wrap gap-4">
          <a
            v-if="anime.url"
            :href="anime.url"
            target="_blank"
            class="flex items-center px-4 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
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
            v-if="anime.trailer_url"
            :href="anime.trailer_url"
            target="_blank"
            class="flex items-center px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10v4a2 2 0 002 2h2a2 2 0 002-2v-4M9 10V6a2 2 0 012-2h2a2 2 0 012 2v4"
              ></path>
            </svg>
            Watch Trailer
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const anime = ref(null)
const loading = ref(true)
const error = ref(null)
const showDebug = ref(false)

const formatScore = (score) => {
  if (!score) return 'N/A'
  return (score * 1).toFixed(1)
}

const formatNumber = (num) => {
  if (!num) return 'N/A'
  return num.toLocaleString()
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

const formatDateRange = (from, to) => {
  if (!from && !to) return 'N/A'
  if (!to) return `${formatDate(from)} - ?`
  if (!from) return `? - ${formatDate(to)}`

  const fromDate = formatDate(from)
  const toDate = formatDate(to)

  if (fromDate === toDate) return fromDate
  return `${fromDate} - ${toDate}`
}

const getStatusColor = (status) => {
  const statusColors = {
    'Finished Airing': 'text-green-400',
    'Currently Airing': 'text-blue-400',
    'Not yet aired': 'text-yellow-400',
    Completed: 'text-green-400',
    Ongoing: 'text-blue-400',
    Upcoming: 'text-yellow-400',
  }
  return statusColors[status] || 'text-gray-400'
}

const handleImageError = (event) => {
  event.target.src = '/placeholder-anime.jpg'
}

const loadAnime = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('Fetching anime with ID:', route.params.id)
    const response = await axios.get(`http://127.0.0.1:8000/anime/${route.params.id}`)
    console.log('API Response:', response.data)

    if (response.data && response.data.error) {
      error.value = response.data.error
    } else {
      anime.value = response.data
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
</script>
