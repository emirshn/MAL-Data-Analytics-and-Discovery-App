<template>
  <div class="p-6 pt-20 bg-gray-900 min-h-screen text-white max-w-6xl mx-auto">
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
      <div class="relative bg-gradient-to-r from-gray-800 via-gray-900 to-black rounded-xl p-6">
        <div class="flex flex-col lg:flex-row gap-8">
          <div class="flex-shrink-0">
            <img
              :src="getImageUrl() || '/placeholder-manga.jpg'"
              :alt="manga.title || 'Manga Cover'"
              class="w-64 h-96 rounded-lg shadow-2xl object-cover mx-auto lg:mx-0"
              @error="handleImageError"
            />
          </div>

          <div class="flex-1 space-y-4">
            <div>
              <h1 class="text-4xl font-bold mb-2">{{ manga.title || 'Unknown Title' }}</h1>
              <p
                v-if="manga.title_english && manga.title_english !== manga.title"
                class="text-gray-300 text-xl"
              >
                {{ manga.title_english }}
              </p>
              <p v-if="manga.title_japanese" class="text-gray-400 text-lg">
                {{ manga.title_japanese }}
              </p>
              <p
                v-if="manga.title_synonyms && manga.title_synonyms.length"
                class="text-gray-500 text-sm"
              >
                <strong>Also known as:</strong>
                {{ manga.title_synonyms.join(', ') }}
              </p>
            </div>

            <!-- Key Stats Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div
                v-if="manga.score"
                class="bg-yellow-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-yellow-400 text-2xl font-bold">
                  ★ {{ formatScore(manga.score) }}
                </div>
                <div class="text-xs text-gray-400">Score</div>
              </div>
              <div v-if="manga.rank" class="bg-purple-600 bg-opacity-20 p-3 rounded-lg text-center">
                <div class="text-purple-400 text-2xl font-bold">#{{ manga.rank }}</div>
                <div class="text-xs text-gray-400">Rank</div>
              </div>
              <div
                v-if="manga.popularity"
                class="bg-green-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-green-400 text-2xl font-bold">#{{ manga.popularity }}</div>
                <div class="text-xs text-gray-400">Popularity</div>
              </div>
              <div
                v-if="manga.members"
                class="bg-blue-600 bg-opacity-20 p-3 rounded-lg text-center"
              >
                <div class="text-blue-400 text-2xl font-bold">
                  {{ formatNumber(manga.members) }}
                </div>
                <div class="text-xs text-gray-400">Members</div>
              </div>
            </div>

            <!-- Basic Info Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div v-if="manga.type" class="flex justify-between">
                <span class="text-gray-400">Type:</span>
                <span class="font-medium">{{ manga.type }}</span>
              </div>
              <div v-if="manga.status" class="flex justify-between">
                <span class="text-gray-400">Status:</span>
                <span class="font-medium" :class="getStatusColor(manga.status)">{{
                  manga.status
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Chapters:</span>
                <span class="font-medium">{{ manga.chapters || 'Ongoing' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Volumes:</span>
                <span class="font-medium">{{ manga.volumes || 'Ongoing' }}</span>
              </div>

              <div v-if="getAuthorsList().length" class="flex justify-between">
                <span class="text-gray-400"
                  >Author{{ getAuthorsList().length > 1 ? 's' : '' }}:</span
                >
                <span class="font-medium truncate" :title="getAuthorsList().join(', ')"
                  >{{ getAuthorsList().slice(0, 2).join(', ')
                  }}{{ getAuthorsList().length > 2 ? '...' : '' }}</span
                >
              </div>
              <div v-if="getSerializationsList().length" class="flex justify-between">
                <span class="text-gray-400">Magazine:</span>
                <span class="font-medium truncate" :title="getSerializationsList().join(', ')">{{
                  getSerializationsList()[0]
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

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
        <!-- Genres and Themes Row -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Genres -->
          <div v-if="getGenresList().length" class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-blue-400">Genres</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="genre in getGenresList()"
                :key="genre"
                class="px-3 py-1 rounded-full bg-blue-600 text-white text-sm hover:bg-blue-700 transition-colors cursor-pointer"
              >
                {{ genre }}
              </span>
            </div>
          </div>

          <!-- Themes -->
          <div v-if="getThemesList().length" class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-purple-400">Themes</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="theme in getThemesList()"
                :key="theme"
                class="px-3 py-1 rounded-full bg-purple-600 text-white text-sm hover:bg-purple-700 transition-colors cursor-pointer"
              >
                {{ theme }}
              </span>
            </div>
          </div>
        </div>

        <!-- Demographics Row -->
        <div v-if="getDemographicsList().length" class="grid grid-cols-1 gap-6">
          <div class="bg-gray-800 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4 text-green-400">Demographics</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="demo in getDemographicsList()"
                :key="demo"
                class="px-3 py-1 rounded-full bg-green-600 text-white text-sm hover:bg-green-700 transition-colors cursor-pointer"
              >
                {{ demo }}
              </span>
            </div>
          </div>
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
              <span class="font-medium" :class="manga.approved ? 'text-green-400' : 'text-red-400'">
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
      <div v-if="manga.relations && manga.relations.length" class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-xl font-semibold mb-6 text-pink-400 flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
            ></path>
          </svg>
          Related Media
        </h3>

        <!-- Single horizontal scrollable container for all entries -->
        <div class="flex gap-4 overflow-x-auto pb-4">
          <div v-for="relation in manga.relations" :key="relation.relation" class="flex gap-4">
            <div
              v-for="entry in relation.entry"
              :key="entry.mal_id"
              class="flex-shrink-0 w-32 group cursor-pointer"
            >
              <a v-if="entry.url" :href="entry.url" target="_blank" class="block">
                <div
                  class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors"
                >
                  <!-- Image with fallback -->
                  <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                    <img
                      :src="relationImages[entry.mal_id] || getPlaceholderImage(entry)"
                      :alt="entry.name"
                      class="w-full h-full object-cover"
                      @error="() => handleRelationImageError(entry)"
                      :class="{ 'opacity-50': !relationImages[entry.mal_id] }"
                    />
                    <div class="absolute top-2 right-2">
                      <span
                        class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded uppercase"
                      >
                        {{ entry.type }}
                      </span>
                    </div>
                  </div>

                  <!-- Content -->
                  <div class="p-2">
                    <h5
                      class="text-xs font-medium text-white line-clamp-2 group-hover:text-pink-300 transition-colors leading-tight mb-1"
                    >
                      {{ entry.name }}
                    </h5>
                    <span class="text-xs text-pink-300 capitalize">{{
                      getRelationForEntry(entry.mal_id)
                    }}</span>
                  </div>
                </div>
              </a>

              <!-- Non-clickable version if no URL -->
              <div v-else class="block">
                <div class="bg-gray-900 rounded-lg overflow-hidden">
                  <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                    <img
                      :src="relationImages[entry.mal_id] || getPlaceholderImage(entry)"
                      :alt="entry.name"
                      class="w-full h-full object-cover"
                      @error="() => handleRelationImageError(entry)"
                      :class="{ 'opacity-50': !relationImages[entry.mal_id] }"
                    />
                    <div class="absolute top-2 right-2">
                      <span
                        class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded uppercase"
                      >
                        {{ entry.type }}
                      </span>
                    </div>
                  </div>

                  <div class="p-2">
                    <h5 class="text-xs font-medium text-white line-clamp-2 leading-tight mb-1">
                      {{ entry.name }}
                    </h5>
                    <span class="text-xs text-pink-300 capitalize">{{
                      getRelationForEntry(entry.mal_id)
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations Section -->
      <div
        v-if="manga.recommendations && manga.recommendations.length"
        class="bg-gray-800 rounded-xl p-6"
      >
        <h3 class="text-xl font-semibold mb-6 text-amber-400 flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            ></path>
          </svg>
          Recommended By Users
        </h3>

        <!-- Horizontal scrollable container -->
        <div class="overflow-x-auto overflow-y-hidden">
          <div class="flex gap-4 pb-4 min-w-max">
            <div
              v-for="recommendation in manga.recommendations"
              :key="recommendation.entry.mal_id"
              class="flex-shrink-0 w-40 group cursor-pointer"
              @click="openMangaDetail(recommendation)"
            >
              <div
                class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors h-full"
              >
                <!-- Image -->
                <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                  <img
                    :src="getRecommendationImageUrl(recommendation.entry)"
                    :alt="recommendation.entry.title"
                    class="w-full h-full object-cover"
                    @error="(e) => handleRecommendationImageError(e, recommendation.entry)"
                  />
                  <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded">
                      MANGA
                    </span>
                  </div>
                  <div class="absolute bottom-2 left-2">
                    <span
                      class="px-2 py-1 bg-amber-600 bg-opacity-90 text-white text-xs rounded flex items-center"
                    >
                      <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                        />
                      </svg>
                      {{ recommendation.votes }}
                    </span>
                  </div>
                </div>

                <!-- Content -->
                <div class="p-3">
                  <h5
                    class="text-sm font-medium text-white line-clamp-2 group-hover:text-amber-300 transition-colors leading-tight mb-1"
                  >
                    {{ recommendation.entry.title }}
                  </h5>
                  <span class="text-xs text-amber-300"> {{ recommendation.votes }} votes </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const route = useRoute()
const manga = ref(null)
const loading = ref(true)
const error = ref(null)
const showDebug = ref(false)
const relationImages = ref({})

const openMangaDetail = (manga) => {
  window.location.href = `/manga/${manga.entry.mal_id}`
}

const getImageUrl = () => {
  if (!manga.value?.images) return null

  if (manga.value.images.webp?.large_image_url) {
    return manga.value.images.webp.large_image_url
  }
  if (manga.value.images.webp?.image_url) {
    return manga.value.images.webp.image_url
  }
  if (manga.value.images.jpg?.large_image_url) {
    return manga.value.images.jpg.large_image_url
  }
  if (manga.value.images.jpg?.image_url) {
    return manga.value.images.jpg.image_url
  }

  return null
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

// Handle image error for recommendation images
const handleRecommendationImageError = (event, entry) => {
  event.target.src = getPlaceholderImage({ type: 'manga' })
}

// Helper function to get placeholder image
const getPlaceholderImage = (entry) => {
  return `https://via.placeholder.com/200x280/374151/f3f4f6?text=${encodeURIComponent(entry.type)}`
}

// Handle image error for relation images
const handleRelationImageError = (entry) => {
  // Remove the failed image from relationImages so placeholder is shown
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

const loadRelationImages = async () => {
  if (!manga.value?.relations) return

  for (const relation of manga.value.relations) {
    for (const entry of relation.entry) {
      await loadRelationImage(entry)
      await sleep(400)
    }
  }
}

const formatScore = (score) => {
  if (!score) return 'N/A'
  return parseFloat(score).toFixed(1)
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

const getStatusColor = (status) => {
  const statusColors = {
    Finished: 'text-green-400',
    Publishing: 'text-blue-400',
    'On Hiatus': 'text-yellow-400',
    Discontinued: 'text-red-400',
    'Not yet published': 'text-yellow-400',
    Completed: 'text-green-400',
    Ongoing: 'text-blue-400',
    Upcoming: 'text-yellow-400',
  }
  return statusColors[status] || 'text-gray-400'
}

const handleImageError = (event) => {
  event.target.src = '/placeholder-manga.jpg'
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

      await loadRelationImages()
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
</script>

<style scoped>
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
