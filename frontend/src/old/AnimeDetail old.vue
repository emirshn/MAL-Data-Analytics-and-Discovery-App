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
              :src="getImageUrl() || '/placeholder-anime.jpg'"
              :alt="anime.title || 'Anime Cover'"
              class="w-64 h-96 rounded-lg shadow-2xl object-cover mx-auto lg:mx-0"
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
              <p
                v-if="anime.title_synonyms && anime.title_synonyms.length"
                class="text-gray-500 text-sm"
              >
                <strong>Also known as:</strong>
                {{ anime.title_synonyms.join(', ') }}
              </p>
            </div>

            <!-- Key Stats Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                v-if="anime.score"
                :value="`★ ${formatScore(anime.score)}`"
                label="Score"
                color="yellow"
              />

              <StatCard v-if="anime.rank" :value="`#${anime.rank}`" label="Rank" color="purple" />

              <StatCard
                v-if="anime.popularity"
                :value="`#${anime.popularity}`"
                label="Popularity"
                color="green"
              />

              <StatCard
                v-if="anime.members"
                :value="formatNumber(anime.members)"
                label="Members"
                color="blue"
              />
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
              <span class="font-medium" :class="anime.approved ? 'text-green-400' : 'text-red-400'">
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

      <!-- Relations Section -->
      <div v-if="anime.relations && anime.relations.length" class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-xl font-semibold mb-6 text-pink-400 flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
            ></path>
          </svg>
          Related Anime
        </h3>

        <!-- Single horizontal scrollable container for all entries -->
        <div class="flex gap-4 overflow-x-auto pb-4">
          <div v-for="relation in anime.relations" :key="relation.relation" class="flex gap-4">
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

      <!-- AI-Powered Recommendations Section -->
      <div
        v-if="aiRecommendations !== null && aiRecommendations !== undefined"
        class="bg-gray-800 rounded-xl p-6"
      >
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-semibold text-amber-400 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              ></path>
            </svg>
            AI-Powered Recommendations
          </h3>

          <!-- Filter Controls -->
          <div class="flex items-center gap-3 text-sm">
            <label class="flex items-center text-gray-300">
              <input
                v-model="recommendationFilters.includeSequels"
                type="checkbox"
                class="mr-2 rounded bg-gray-700 border-gray-600 text-amber-500 focus:ring-amber-500"
                @change="fetchAIRecommendations"
              />
              Include Sequels
            </label>
            <label class="flex items-center text-gray-300">
              <input
                v-model="recommendationFilters.showExplanations"
                type="checkbox"
                class="mr-2 rounded bg-gray-700 border-gray-600 text-amber-500 focus:ring-amber-500"
              />
              Show Explanations
            </label>
            <select
              v-model="recommendationFilters.minScore"
              class="bg-gray-700 border-gray-600 text-white rounded px-2 py-1 text-sm"
              @change="fetchAIRecommendations"
            >
              <option value="">Any Score</option>
              <option value="6.0">6.0+ Rating</option>
              <option value="7.0">7.0+ Rating</option>
              <option value="8.0">8.0+ Rating</option>
              <option value="8.5">8.5+ Rating</option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loadingRecommendations" class="text-center py-8">
          <div
            class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400"
          ></div>
          <p class="mt-2 text-gray-400">Finding similar anime...</p>
        </div>

        <!-- Recommendations Grid - Only show if we have recommendations -->
        <div
          v-else-if="aiRecommendations && aiRecommendations.length > 0"
          class="overflow-x-auto overflow-y-hidden"
        >
          <div class="flex gap-4 pb-4 min-w-max">
            <div
              v-for="recommendation in aiRecommendations"
              :key="recommendation.id"
              class="flex-shrink-0 w-48 group cursor-pointer"
              @click="openAnimeDetail(recommendation)"
            >
              <div
                class="bg-gray-900 rounded-lg overflow-hidden hover:bg-gray-700 transition-all duration-300 h-full hover:shadow-lg hover:shadow-amber-500/20"
              >
                <!-- Image -->
                <div class="aspect-[3/4] bg-gray-700 overflow-hidden relative">
                  <img
                    :src="
                      recommendation.image_url ||
                      recommendation.thumbnail_url ||
                      '/api/placeholder/160/213'
                    "
                    :alt="recommendation.title"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    @error="(e) => handleImageError(e, recommendation)"
                  />

                  <!-- Type Badge -->
                  <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded">
                      {{ recommendation.type || 'ANIME' }}
                    </span>
                  </div>

                  <!-- Score and Similarity -->
                  <div class="absolute bottom-2 left-2 flex flex-col gap-1">
                    <span
                      v-if="recommendation.score"
                      class="px-2 py-1 bg-amber-600 bg-opacity-90 text-white text-xs rounded flex items-center"
                    >
                      <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                        />
                      </svg>
                      {{ recommendation.score.toFixed(1) }}
                    </span>

                    <span class="px-2 py-1 bg-blue-600 bg-opacity-90 text-white text-xs rounded">
                      {{ Math.round(recommendation.similarity * 100) }}% match
                    </span>
                  </div>
                </div>

                <!-- Content -->
                <div class="p-3">
                  <h5
                    class="text-sm font-medium text-white line-clamp-2 group-hover:text-amber-300 transition-colors leading-tight mb-2"
                  >
                    {{ recommendation.title }}
                  </h5>

                  <!-- English Title -->
                  <p
                    v-if="
                      recommendation.title_english &&
                      recommendation.title_english !== recommendation.title
                    "
                    class="text-xs text-gray-400 mb-2 line-clamp-1"
                  >
                    {{ recommendation.title_english }}
                  </p>

                  <!-- Meta Info -->
                  <div class="flex items-center justify-between text-xs text-gray-400 mb-2">
                    <span v-if="recommendation.year">{{ recommendation.year }}</span>
                    <span v-if="recommendation.episodes">{{ recommendation.episodes }} eps</span>
                  </div>

                  <!-- Explanation (if enabled) -->
                  <div
                    v-if="recommendationFilters.showExplanations && recommendation.explanation"
                    class="bg-gray-800 rounded p-2 mt-2"
                  >
                    <p class="text-xs text-amber-200 leading-relaxed">
                      {{ recommendation.explanation }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results Message - Only show when not loading and no recommendations -->
        <div
          v-else-if="!loadingRecommendations && aiRecommendations.length === 0"
          class="text-center py-8 text-gray-400"
        >
          <svg
            class="w-12 h-12 mx-auto mb-4 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"
            ></path>
          </svg>
          <p>No recommendations found with current filters</p>
          <button
            @click="resetRecommendationFilters"
            class="mt-2 text-amber-400 hover:text-amber-300 text-sm underline"
          >
            Reset Filters
          </button>
        </div>
      </div>

      <!-- Show this section when aiRecommendations is null/undefined or empty -->
      <div v-else-if="!loadingRecommendations" class="bg-gray-800 rounded-xl p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-semibold text-amber-400 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              ></path>
            </svg>
            AI-Powered Recommendations
          </h3>
        </div>

        <div class="text-center py-8 text-gray-400">
          <svg
            class="w-12 h-12 mx-auto mb-4 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"
            ></path>
          </svg>
          <p>No recommendations available</p>
        </div>
      </div>

      <!-- Recommendations Section -->
      <div
        v-if="anime.recommendations && anime.recommendations.length"
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
              v-for="recommendation in anime.recommendations"
              :key="recommendation.entry.mal_id"
              class="flex-shrink-0 w-40 group cursor-pointer"
              @click="openAnimeDetail(recommendation)"
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
                      ANIME
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
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useRouter } from 'vue-router'
import StatCard from '@/components/common/StatCard.vue'
import TagSection from '@/components/common/TagSection.vue'
import RelatedInfo from '@/components/common/RelatedInfo.vue'

const router = useRouter()

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

function resetRecommendationFilters() {
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
    if (newId) {
      fetchAIRecommendations()
    }
  },
  { immediate: true },
)

function openAnimeDetail(item) {
  let animeId
  if (item.id) {
    animeId = item.id
  } else if (item.entry?.mal_id) {
    animeId = item.entry.mal_id
  } else if (item.mal_id) {
    animeId = item.mal_id
  } else {
    console.error('Unable to determine anime ID from:', item)
    return
  }

  window.location.href = `/anime/${animeId}`
}
const getImageUrl = () => {
  if (!anime.value?.images) return null

  if (anime.value.images.webp?.large_image_url) {
    return anime.value.images.webp.large_image_url
  }
  if (anime.value.images.webp?.image_url) {
    return anime.value.images.webp.image_url
  }
  if (anime.value.images.jpg?.large_image_url) {
    return anime.value.images.jpg.large_image_url
  }
  if (anime.value.images.jpg?.image_url) {
    return anime.value.images.jpg.image_url
  }

  return null
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

// Helper function to get relation type for a specific entry
const getRelationForEntry = (malId) => {
  if (!anime.value?.relations) return ''

  for (const relation of anime.value.relations) {
    const entry = relation.entry.find((e) => e.mal_id === malId)
    if (entry) return relation.relation
  }
  return ''
}

// Helper function to get recommendation image URL
const getRecommendationImageUrl = (entry) => {
  if (!entry?.images) return getPlaceholderImage({ type: 'anime' })

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

  return getPlaceholderImage({ type: 'anime' })
}

// Handle image error for recommendation images
const handleRecommendationImageError = (event, entry) => {
  event.target.src = getPlaceholderImage({ type: 'anime' })
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
  if (!anime.value?.relations) return

  for (const relation of anime.value.relations) {
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

      await loadRelationImages()
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
