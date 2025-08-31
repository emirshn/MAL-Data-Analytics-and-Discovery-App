<template>
  <div class="relative bg-gradient-to-r from-gray-800 via-gray-900 to-black rounded-xl p-6">
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Cover Image -->
      <div class="flex-shrink-0">
        <img
          :src="getImageUrl()"
          :alt="manga.title || 'Manga Cover'"
          class="w-64 h-96 rounded-lg shadow-2xl object-cover mx-auto lg:mx-0"
          @error="handleImageError"
        />
      </div>

      <!-- Main Info -->
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
          <StatCard
            v-if="manga.score"
            :value="`★ ${formatScore(manga.score)}`"
            label="Score"
            color="yellow"
          />
          <StatCard v-if="manga.rank" :value="`#${manga.rank}`" label="Rank" color="purple" />
          <StatCard
            v-if="manga.popularity"
            :value="`#${manga.popularity}`"
            label="Popularity"
            color="green"
          />
          <StatCard
            v-if="manga.members"
            :value="formatNumber(manga.members)"
            label="Members"
            color="blue"
          />
        </div>

        <!-- Basic Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div v-if="manga.type" class="flex justify-between">
            <span class="text-gray-400">Type:</span>
            <span class="font-medium">{{ manga.type }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Chapters:</span>
            <span class="font-medium">{{ manga.chapters || 'Ongoing' }}</span>
          </div>
          <div v-if="manga.status" class="flex justify-between">
            <span class="text-gray-400">Status:</span>
            <span class="font-medium" :class="getStatusColor(manga.status)">{{
              manga.status
            }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Volumes:</span>
            <span class="font-medium">{{ manga.volumes || 'Ongoing' }}</span>
          </div>
          <div v-if="getAuthorsList().length" class="flex justify-between">
            <span class="text-gray-400">Author{{ getAuthorsList().length > 1 ? 's' : '' }}:</span>
            <span class="font-medium truncate" :title="getAuthorsList().join(', ')">
              {{ getAuthorsList().slice(0, 2).join(', ') }}
              {{ getAuthorsList().length > 2 ? '...' : '' }}
            </span>
          </div>
          <div v-if="getSerializationsList().length" class="flex justify-between">
            <span class="text-gray-400">Magazine:</span>
            <span class="font-medium truncate" :title="getSerializationsList().join(', ')">
              {{ getSerializationsList()[0] }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatCard from '../common/StatCard.vue'

const { manga } = defineProps({
  manga: { type: Object, required: true },
})

function handleImageError(event) {
  event.target.src = '/placeholder-manga.jpg'
}

function formatScore(score) {
  if (!score) return 'N/A'
  return parseFloat(score).toFixed(1)
}

function formatNumber(num) {
  if (!num) return 'N/A'
  return parseInt(num).toLocaleString()
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

const getImageUrl = () => {
  if (!manga.images) return '/placeholder-manga.jpg'

  if (manga.images.webp?.large_image_url) return manga.images.webp.large_image_url
  if (manga.images.webp?.image_url) return manga.images.webp.image_url
  if (manga.images.jpg?.large_image_url) return manga.images.jpg.large_image_url
  if (manga.images.jpg?.image_url) return manga.images.jpg.image_url

  return '/placeholder-manga.jpg'
}

const getAuthorsList = () => {
  if (!manga.authors || !Array.isArray(manga.authors)) return []
  return manga.authors.map((author) => author.name).filter((name) => name)
}

const getSerializationsList = () => {
  if (!manga.serializations || !Array.isArray(manga.serializations)) return []
  return manga.serializations.map((serialization) => serialization.name).filter((name) => name)
}
</script>
