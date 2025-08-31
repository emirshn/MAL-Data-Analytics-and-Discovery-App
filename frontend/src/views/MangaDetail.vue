<template>
  <div class="pt-20 min-h-screen text-white relative bg-container overflow-hidden">
    <div class="absolute inset-0 grid-container">
      <div class="grid-layer-1"></div>
      <div class="grid-layer-2"></div>
    </div>

    <div class="relative z-10 max-w-6xl mx-auto">
      <div v-if="loading" class="text-center">
        <div class="animate-pulse">
          <div class="text-lg">Loading manga details...</div>
          <div
            class="mt-4 w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto"
          ></div>
        </div>
      </div>

      <div v-else-if="error" class="text-center text-red-400">
        <div class="text-lg">{{ error }}</div>
        <button
          @click="retryLoad"
          class="mt-4 px-4 py-2 bg-purple-600 rounded hover:bg-purple-700 transition-colors"
        >
          Retry
        </button>
      </div>

      <div v-else-if="manga" class="space-y-8">
        <!-- Hero Section with Cover + Main Info -->
        <MangaHero :manga="manga" />

        <!-- Synopsis Section -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h2 class="text-2xl font-semibold mb-4 text-purple-400 flex items-center">
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
              {{ manga.synopsis || manga.background || 'No synopsis available.' }}
            </p>
          </div>
        </div>

        <!-- Publication and Author Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Publication Information -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-green-400">Publication Information</h3>
            <div class="space-y-3 text-sm">
              <div v-if="manga.published" class="flex justify-between">
                <span class="text-gray-400">Published:</span>
                <span class="font-medium">{{ getPublishedString() }}</span>
              </div>
              <div v-if="manga.publishing !== undefined" class="flex justify-between">
                <span class="text-gray-400">Currently Publishing:</span>
                <span
                  class="font-medium"
                  :class="manga.publishing ? 'text-green-400' : 'text-red-400'"
                >
                  {{ manga.publishing ? 'Yes' : 'No' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Authors and Publishers -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-orange-400">Authors & Publishers</h3>
            <div class="space-y-3 text-sm">
              <div v-if="getAuthorsList().length" class="space-y-1">
                <span class="text-gray-400 block">Authors:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="author in getAuthorsList()"
                    :key="author"
                    class="px-2 py-1 bg-orange-600 rounded text-xs"
                  >
                    {{ author }}
                  </span>
                </div>
              </div>
              <div v-if="getSerializationsList().length" class="space-y-1">
                <span class="text-gray-400 block">Serializations:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="serialization in getSerializationsList()"
                    :key="serialization"
                    class="px-2 py-1 bg-gray-600 rounded text-xs"
                  >
                    {{ serialization }}
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
              <div v-if="manga.scored_by" class="flex justify-between text-sm">
                <span class="text-gray-400">Scored by:</span>
                <span class="font-medium">{{ formatNumber(manga.scored_by) }} users</span>
              </div>
              <div v-if="manga.favorites" class="flex justify-between text-sm">
                <span class="text-gray-400">Favorited by:</span>
                <span class="font-medium">{{ formatNumber(manga.favorites) }} users</span>
              </div>
              <div v-if="manga.members" class="flex justify-between text-sm">
                <span class="text-gray-400">Total Members:</span>
                <span class="font-medium">{{ formatNumber(manga.members) }} users</span>
              </div>
            </div>
          </div>

          <!-- Additional Details -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-cyan-400">Additional Details</h3>
            <div class="space-y-3 text-sm">
              <div v-if="manga.approved !== undefined" class="flex justify-between">
                <span class="text-gray-400">Approved:</span>
                <span
                  class="font-medium"
                  :class="manga.approved ? 'text-green-400' : 'text-red-400'"
                >
                  {{ manga.approved ? 'Yes' : 'No' }}
                </span>
              </div>
              <div v-if="manga.mal_id" class="flex justify-between">
                <span class="text-gray-400">MAL ID:</span>
                <span class="font-medium">{{ manga.mal_id }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Relations Section -->
        <RelatedInfo
          v-if="manga"
          :anime="manga"
          :relationImages="relationImages"
          @relationImageError="handleRelationImageError"
          @entryClick="openMangaDetail"
        />

        <!-- External Links -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4 text-indigo-400">External Links</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Main Links -->
            <a
              v-if="manga.url"
              :href="manga.url"
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

            <!-- External links from the external array -->
            <a
              v-for="link in manga.external || []"
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
              JSON.stringify(manga, null, 2)
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
        <div class="text-xl font-semibold mb-2">Manga Not Found</div>
        <p class="text-gray-500">The requested manga could not be found in our database.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import TagSection from '@/components/common/TagSection.vue'
import RelatedInfo from '@/components/common/RelatedInfo.vue'
import MangaHero from '@/components/manga/MangaHero.vue'

const route = useRoute()
const manga = ref(null)
const loading = ref(true)
const error = ref(null)
const showDebug = ref(false)
const relationImages = ref({})

function openMangaDetail(item) {
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

const getPublishedString = () => {
  if (!manga.value?.published) return 'N/A'

  if (manga.value.published.string) {
    return manga.value.published.string
  }

  const from = manga.value.published.from
  const to = manga.value.published.to

  if (!from && !to) return 'N/A'
  if (!to) return `${formatDate(from)} - ?`
  if (!from) return `? - ${formatDate(to)}`

  const fromDate = formatDate(from)
  const toDate = formatDate(to)

  if (fromDate === toDate) return fromDate
  return `${fromDate} - ${toDate}`
}

// Helper function to get authors list
const getAuthorsList = () => {
  if (!manga.value?.authors || !Array.isArray(manga.value.authors)) return []
  return manga.value.authors.map((author) => author.name).filter((name) => name)
}

// Helper function to get serializations list
const getSerializationsList = () => {
  if (!manga.value?.serializations || !Array.isArray(manga.value.serializations)) return []
  return manga.value.serializations
    .map((serialization) => serialization.name)
    .filter((name) => name)
}

// Helper function to get genres list
const getGenresList = () => {
  if (!manga.value?.genres || !Array.isArray(manga.value.genres)) return []
  return manga.value.genres.map((genre) => genre.name).filter((name) => name)
}

// Helper function to get themes list
const getThemesList = () => {
  if (!manga.value?.themes || !Array.isArray(manga.value.themes)) return []
  return manga.value.themes.map((theme) => theme.name).filter((name) => name)
}

// Helper function to get demographics list
const getDemographicsList = () => {
  if (!manga.value?.demographics || !Array.isArray(manga.value.demographics)) return []
  return manga.value.demographics.map((demo) => demo.name).filter((name) => name)
}

// Helper function to get relation type for a specific entry
const getRelationForEntry = (malId) => {
  if (!manga.value?.relations) return ''

  for (const relation of manga.value.relations) {
    const entry = relation.entry.find((e) => e.mal_id === malId)
    if (entry) return relation.relation
  }
  return ''
}

// Helper function to get recommendation image URL
const getRecommendationImageUrl = (entry) => {
  if (!entry?.images) return getPlaceholderImage({ type: 'manga' })

  // Try different image formats in order of preference
  if (entry.images.webp?.large_image_url) {
    return entry.images.webp.large_image_url
  }
  if (entry.images.webp?.image_url) {
    return entry.images.webp.image_url
  }
  if (entry.images.jpg?.large_image_url) {
    return entry.images.jpg.large_image_url
  }
  if (entry.images.jpg?.image_url) {
    return entry.images.jpg.image_url
  }

  return getPlaceholderImage({ type: 'manga' })
}

// Helper function to get placeholder image
const getPlaceholderImage = (entry) => {
  return `https://via.placeholder.com/200x280/374151/f3f4f6?text=${encodeURIComponent(entry.type)}`
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
    let endpoint = ''

    if (entry.type === 'anime') {
      endpoint = `${baseUrl}/anime/${entry.mal_id}/image`
    } else if (entry.type === 'manga') {
      endpoint = `${baseUrl}/manga/${entry.mal_id}/image`
    } else {
      return
    }

    const response = await axios.get(endpoint)
    if (response.data && response.data.image_url) {
      relationImages.value[entry.mal_id] = response.data.image_url
    }
  } catch (error) {
    if (error.response?.status === 429) {
      console.warn(`Rate limited for ${entry.type} ${entry.mal_id}, retrying...`)
      await sleep(1200)
      return loadRelationImage(entry)
    }
    console.log(`Failed to load image for ${entry.type} ${entry.mal_id}:`, error)
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
  if (!manga.value?.relations) return
  for (const relation of manga.value.relations) {
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

const loadManga = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('Fetching manga with ID:', route.params.id)
    const response = await axios.get(`http://127.0.0.1:8000/manga/${route.params.id}`)
    console.log('Full API Response:', response.data)

    if (response.data && response.data.error) {
      error.value = response.data.error
    } else {
      let mangaData = null

      // Handle the nested manga structure
      if (response.data.manga) {
        console.log('Using response.data.manga')
        mangaData = response.data.manga

        // Add recommendations from top level if they exist
        if (response.data.recommendations && !mangaData.recommendations) {
          console.log('Adding recommendations from top level')
          mangaData.recommendations = response.data.recommendations
        }
      } else if (response.data.data) {
        console.log('Using response.data.data')
        mangaData = response.data.data

        // Add recommendations from top level if they exist
        if (response.data.recommendations && !mangaData.recommendations) {
          console.log('Adding recommendations from top level')
          mangaData.recommendations = response.data.recommendations
        }
      } else {
        console.log('Using response.data directly')
        mangaData = response.data
      }

      console.log('Final manga data recommendations:', mangaData.recommendations?.length || 0)

      manga.value = mangaData

      nextTick(() => startRelationImageFetch())
    }
  } catch (err) {
    console.error('Error fetching manga detail:', err)

    if (err.response) {
      error.value = `Error ${err.response.status}: ${err.response.data?.detail || 'Failed to load manga'}`
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
  loadManga()
}

onMounted(() => {
  loadManga()
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
