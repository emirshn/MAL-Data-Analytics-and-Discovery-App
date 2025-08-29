<template>
  <div
    class="w-full mx-auto p-8 bg-gradient-to-br from-slate-800 to-slate-950 min-h-screen text-white pt-[100px]"
  >
    <!-- Header -->
    <div class="text-center mb-12">
      <h1
        class="text-6xl font-extrabold mb-4 bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent"
      >
        Database Analytics
      </h1>
      <p class="text-xl text-slate-400">Complete analysis of anime and manga collection</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-[400px]">
      <div
        class="w-12 h-12 border-4 border-slate-700 border-t-indigo-500 rounded-full animate-spin mb-4"
      ></div>
      <p class="text-xl">Loading statistics...</p>
      <p class="text-xl">It can take a while...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-16">
      <OverviewSection :cards="overviewCards" :animatedValues="animatedValues" />

      <ScoreAnalysisSection :stats="stats" />
      <GenreAnalysisSection :stats="stats" />
      <StudioAnalysisSection :stats="stats" />
      <ClassificationAnalysisSection :stats="stats" />
      <BroadcastingAnalysisSection :stats="stats" />
      <CommunityAnalysisSection :stats="stats" />
      <ContentLengthSection :stats="stats" />
      <CreatorsPublicationsSection :stats="stats" />
      <TopListsSection :stats="stats" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import ScoreAnalysisSection from '@/components/sections/ScoreAnalysisSection.vue'
import GenreAnalysisSection from '@/components/sections/GenreAnalysisSection.vue'
import StudioAnalysisSection from '@/components/sections/StudioAnalysisSection.vue'
import ClassificationAnalysisSection from '@/components/sections/ClassificationAnalysisSection.vue'
import BroadcastingAnalysisSection from '@/components/sections/BroadcastingAnalysisSection.vue'
import CommunityAnalysisSection from '@/components/sections/CommunityAnalysisSection.vue'
import ContentLengthSection from '@/components/sections/ContentLengthSection.vue'
import CreatorsPublicationsSection from '@/components/sections/CreatorsPublicationsSection.vue'
import TopListsSection from '@/components/sections/TopListsSection.vue'
import OverviewSection from '@/components/sections/OverviewSection.vue'

export default {
  name: 'ComprehensiveStats',
  components: {
    ScoreAnalysisSection,
    GenreAnalysisSection,
    StudioAnalysisSection,
    ClassificationAnalysisSection,
    BroadcastingAnalysisSection,
    CommunityAnalysisSection,
    ContentLengthSection,
    CreatorsPublicationsSection,
    TopListsSection,
    OverviewSection,
  },
  setup() {
    const loading = ref(true)
    const stats = ref({})
    const animatedValues = ref({})

    // Chart instances for cleanup
    const chartInstances = ref(new Map())

    // Overview cards
    const overviewCards = ref([
      { icon: '📺', title: 'Total Anime', key: 'total_anime', description: 'Anime entries' },
      { icon: '📖', title: 'Total Manga', key: 'total_manga', description: 'Manga entries' },
      { icon: '📊', title: 'Combined Total', key: 'total_items', description: 'Total items' },
      {
        icon: '✅',
        title: 'Completed Anime',
        key: 'completed_anime',
        description: 'Finished anime',
      },
      {
        icon: '✅',
        title: 'Completed Manga',
        key: 'completed_manga',
        description: 'Finished manga',
      },
      {
        icon: '⭐',
        title: 'Avg Anime Score',
        key: 'anime_avg_score',
        description: 'Average rating',
      },
      {
        icon: '⭐',
        title: 'Avg Manga Score',
        key: 'manga_avg_score',
        description: 'Average rating',
      },
      {
        icon: '📈',
        title: 'Anime Completion',
        key: 'anime_completion_rate',
        description: 'Completion %',
      },
      {
        icon: '📈',
        title: 'Manga Completion',
        key: 'manga_completion_rate',
        description: 'Completion %',
      },
    ])

    // Fetch comprehensive stats
    const fetchStats = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/stats/comprehensive')
        const data = await response.json()

        stats.value = data
        console.log('Comprehensive stats loaded:', data)

        // Prepare overview data for animation
        const overviewData = {
          ...data.overview,
          anime_completion_rate: data.overview.completion_rates.anime,
          manga_completion_rate: data.overview.completion_rates.manga,
        }

        // Animate numbers
        animateNumbers(overviewData)

        loading.value = false
        await nextTick()
        createAllCharts()
      } catch (error) {
        console.error('Failed to fetch comprehensive stats:', error)
        loading.value = false
      }
    }

    // Animation functions
    const animateNumbers = (data) => {
      overviewCards.value.forEach((card) => {
        const target = data[card.key] || 0
        const isDecimal = target % 1 !== 0
        animateValue(card.key, 0, target, 2000, isDecimal)
      })
    }

    const animateValue = (key, start, end, duration, isDecimal = false) => {
      const startTime = performance.now()
      const range = end - start

      const animate = (now) => {
        const elapsed = now - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easeOut = 1 - Math.pow(1 - progress, 4)
        const value = start + range * easeOut

        animatedValues.value[key] = isDecimal
          ? value.toFixed(2)
          : Math.floor(value).toLocaleString()

        if (progress < 1) requestAnimationFrame(animate)
      }
      requestAnimationFrame(animate)
    }

    const cleanup = () => {
      chartInstances.value.forEach((instance) => {
        if (instance) instance.destroy()
      })
      chartInstances.value.clear()
    }

    onMounted(() => {
      fetchStats()
    })

    return {
      loading,
      stats,
      animatedValues,
      overviewCards,

      cleanup,
    }
  },

  beforeUnmount() {
    this.cleanup()
  },
}
</script>

<style scoped>
/* Custom scrollbar for top lists */
.max-h-96::-webkit-scrollbar {
  width: 4px;
}

.max-h-96::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.max-h-96::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.6);
  border-radius: 4px;
}

.max-h-96::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.8);
}

/* Hover effects for chart containers */
.bg-white\/5:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

/* Responsive text sizing */
@media (max-width: 640px) {
  .text-6xl {
    font-size: 2.5rem;
  }

  .text-3xl {
    font-size: 1.5rem;
  }
}

/* Chart container responsiveness */
canvas {
  max-width: 100%;
  height: auto !important;
}

/* Loading animation enhancement */
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Gradient text animation */
.bg-gradient-to-r {
  background-size: 200% 200%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* Smooth transitions for all interactive elements */
* {
  transition: all 0.2s ease;
}

/* Card hover effects */
.hover\:shadow-2xl:hover {
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(99, 102, 241, 0.1);
}

/* Backdrop blur enhancement */
.backdrop-blur-lg {
  backdrop-filter: blur(16px) saturate(180%);
}
</style>
