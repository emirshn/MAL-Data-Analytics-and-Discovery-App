<template>
  <div class="relative bg-gradient-to-r from-gray-800 via-gray-900 to-black rounded-xl p-6">
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Cover Image -->
      <div class="flex-shrink-0">
        <img
          :src="getImageUrl()"
          :alt="anime.title || 'Anime Cover'"
          class="w-64 h-96 rounded-lg shadow-2xl object-cover mx-auto lg:mx-0"
          @error="handleImageError"
        />
      </div>

      <!-- Main Info -->
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
</template>

<script setup>
import StatCard from '../common/StatCard.vue'
const { anime } = defineProps({
  anime: { type: Object, required: true },
})

function handleImageError(event) {
  event.target.src = '/placeholder-anime.jpg'
}

function formatScore(score) {
  return score.toFixed(2)
}

function formatNumber(num) {
  return num.toLocaleString()
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

const getImageUrl = () => {
  if (!anime.images) return '/placeholder-anime.jpg'

  if (anime.images.webp?.large_image_url) return anime.images.webp.large_image_url
  if (anime.images.webp?.image_url) return anime.images.webp.image_url
  if (anime.images.jpg?.large_image_url) return anime.images.jpg.large_image_url
  if (anime.images.jpg?.image_url) return anime.images.jpg.image_url

  return '/placeholder-anime.jpg'
}
</script>
