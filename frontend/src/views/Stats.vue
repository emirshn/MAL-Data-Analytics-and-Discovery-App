<template>
  <div
    class="max-w-[1600px] mx-auto p-8 bg-gradient-to-br from-slate-800 to-slate-950 min-h-screen text-white"
  >
    <!-- Header -->
    <div class="text-center mb-12">
      <h1
        class="text-6xl font-extrabold mb-4 bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent"
      >
        📊 Comprehensive Database Analytics
      </h1>
      <p class="text-xl text-slate-400">Complete analysis of anime and manga collection</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-[400px]">
      <div
        class="w-12 h-12 border-4 border-slate-700 border-t-indigo-500 rounded-full animate-spin mb-4"
      ></div>
      <p class="text-xl">Loading comprehensive statistics...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-16">
      <!-- Overview Dashboard Cards -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">📈 Overview Dashboard</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          <div
            v-for="(card, index) in overviewCards"
            :key="index"
            class="flex flex-col items-center gap-4 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 transition transform hover:-translate-y-2 hover:shadow-2xl hover:border-indigo-500/40"
          >
            <div class="text-3xl">{{ card.icon }}</div>
            <div class="text-center">
              <h3 class="text-sm text-slate-400 font-medium mb-1">{{ card.title }}</h3>
              <div class="text-xl font-extrabold mb-1">{{ animatedValues[card.key] || 0 }}</div>
              <p class="text-xs text-slate-500">{{ card.description }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Score Analysis Section -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">⭐ Score Analysis</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Score Distribution Comparison -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">
              📊 Score Distribution (Logarithmic)
            </h3>
            <canvas ref="scoreDistributionChart" class="max-h-80"></canvas>
          </div>

          <!-- Rating Performance -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🏆 Rating Performance</h3>
            <canvas ref="ratingPerformanceChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Genre Analysis Section -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">🎭 Genre Analysis</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <!-- Top Combined Genres -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🔥 Top Genres (Combined)</h3>
            <canvas ref="topGenresChart" class="max-h-80"></canvas>
          </div>

          <!-- Genre Performance -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📈 Genre Performance</h3>
            <canvas ref="genrePerformanceChart" class="max-h-80"></canvas>
          </div>

          <!-- Top Genre Combinations -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2 xl:col-span-1"
          >
            <h3 class="text-lg font-semibold text-center mb-6">🤝 Popular Genre Pairs</h3>
            <canvas ref="genreCombinationsChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Studio & Production Analysis -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">🏭 Studio & Production</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <!-- Top Studios by Count -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🏢 Most Prolific Studios</h3>
            <canvas ref="topStudiosChart" class="max-h-80"></canvas>
          </div>

          <!-- Best Studios by Score -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">⭐ Highest Rated Studios</h3>
            <canvas ref="bestStudiosChart" class="max-h-80"></canvas>
          </div>

          <!-- Top Producers -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2 xl:col-span-1"
          >
            <h3 class="text-lg font-semibold text-center mb-6">🎬 Top Producers</h3>
            <canvas ref="topProducersChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Content Classification -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">📚 Content Classification</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <!-- Anime Types -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📺 Anime Types</h3>
            <canvas ref="animeTypesChart" class="max-h-80"></canvas>
          </div>

          <!-- Manga Types -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📖 Manga Types</h3>
            <canvas ref="mangaTypesChart" class="max-h-80"></canvas>
          </div>

          <!-- Rating Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🔞 Rating Distribution</h3>
            <canvas ref="ratingDistributionChart" class="max-h-80"></canvas>
          </div>

          <!-- Source Material -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📚 Source Material</h3>
            <canvas ref="sourceMaterialChart" class="max-h-80"></canvas>
          </div>

          <!-- Demographics Comparison -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 md:col-span-2"
          >
            <h3 class="text-lg font-semibold text-center mb-6">👥 Demographics Comparison</h3>
            <canvas ref="demographicsChart" class="max-h-80"></canvas>
          </div>

          <!-- Source Performance -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 md:col-span-2"
          >
            <h3 class="text-lg font-semibold text-center mb-6">🎯 Source Material Performance</h3>
            <canvas ref="sourcePerformanceChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Time & Broadcasting Analysis -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">📅 Time & Broadcasting</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <!-- Year Distribution Timeline -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2 xl:col-span-3"
          >
            <h3 class="text-lg font-semibold text-center mb-6">📈 Release Timeline by Year</h3>
            <canvas ref="yearTimelineChart" class="max-h-80"></canvas>
          </div>

          <!-- Season Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🌸 Season Distribution</h3>
            <canvas ref="seasonChart" class="max-h-80"></canvas>
          </div>

          <!-- Season Performance -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🏆 Season Performance</h3>
            <canvas ref="seasonPerformanceChart" class="max-h-80"></canvas>
          </div>

          <!-- Broadcast Days -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📺 Broadcast Days</h3>
            <canvas ref="broadcastDaysChart" class="max-h-80"></canvas>
          </div>

          <!-- Broadcast Time Slots -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2"
          >
            <h3 class="text-lg font-semibold text-center mb-6">⏰ Broadcast Time Slots</h3>
            <canvas ref="timeSlotsChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Popularity & Community Analysis -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">🌟 Popularity & Community</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <!-- Members Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">👥 Members Distribution</h3>
            <canvas ref="membersDistributionChart" class="max-h-80"></canvas>
          </div>

          <!-- Popularity vs Score Correlation -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2"
          >
            <h3 class="text-lg font-semibold text-center mb-6">📊 Popularity vs Score</h3>
            <canvas ref="popularityScoreChart" class="max-h-80"></canvas>
          </div>

          <!-- Rank vs Score Correlation -->
          <div
            class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 lg:col-span-2"
          >
            <h3 class="text-lg font-semibold text-center mb-6">🏆 Rank vs Score</h3>
            <canvas ref="rankScoreChart" class="max-h-80"></canvas>
          </div>

          <!-- Members vs Score -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">👥 Members vs Score</h3>
            <canvas ref="membersScoreChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Content Length Analysis -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">📏 Content Length</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Episode Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">⏱️ Episode Distribution</h3>
            <canvas ref="episodeDistributionChart" class="max-h-80"></canvas>
          </div>

          <!-- Chapter Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📄 Chapter Distribution</h3>
            <canvas ref="chapterDistributionChart" class="max-h-80"></canvas>
          </div>

          <!-- Volume Distribution -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📚 Volume Distribution</h3>
            <canvas ref="volumeDistributionChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Creators Analysis (Manga) -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">✍️ Creators & Publications</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <!-- Top Authors -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">✍️ Most Prolific Authors</h3>
            <canvas ref="topAuthorsChart" class="max-h-80"></canvas>
          </div>

          <!-- Best Authors by Score -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">🌟 Highest Rated Authors</h3>
            <canvas ref="bestAuthorsChart" class="max-h-80"></canvas>
          </div>

          <!-- Top Serializations -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">📰 Top Serializations</h3>
            <canvas ref="topSerializationsChart" class="max-h-80"></canvas>
          </div>
        </div>
      </section>

      <!-- Top Lists Section -->
      <section class="space-y-8">
        <h2 class="text-3xl font-bold text-center text-indigo-400">🏆 Top Lists</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Top Favorites -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">❤️ Most Favorited</h3>
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="(item, index) in stats.popularity?.top_favorites?.slice(0, 10)"
                :key="index"
                class="flex justify-between items-center p-3 bg-white/5 rounded-lg"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{{ item.title }}</p>
                  <p class="text-xs text-slate-400">Score: {{ item.score }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-bold text-red-400">
                    {{ (item.favorites || 0).toLocaleString() }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Top Members -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">👥 Most Members</h3>
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="(item, index) in stats.popularity?.top_members?.slice(0, 10)"
                :key="index"
                class="flex justify-between items-center p-3 bg-white/5 rounded-lg"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{{ item.title }}</p>
                  <p class="text-xs text-slate-400">Score: {{ item.score }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-bold text-blue-400">
                    {{ (item.members || 0).toLocaleString() }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Top Scored -->
          <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-center mb-6">⭐ Highest Scored</h3>
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="(item, index) in stats.popularity?.top_scored?.slice(0, 10)"
                :key="index"
                class="flex justify-between items-center p-3 bg-white/5 rounded-lg"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{{ item.title }}</p>
                  <p class="text-xs text-slate-400">
                    {{ (item.members || 0).toLocaleString() }} members
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-bold text-yellow-400">{{ item.score }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'ComprehensiveStats',
  setup() {
    const loading = ref(true)
    const stats = ref({})
    const animatedValues = ref({})

    // Chart refs - All possible charts
    const scoreDistributionChart = ref(null)
    const ratingPerformanceChart = ref(null)
    const topGenresChart = ref(null)
    const genrePerformanceChart = ref(null)
    const genreCombinationsChart = ref(null)
    const topStudiosChart = ref(null)
    const bestStudiosChart = ref(null)
    const topProducersChart = ref(null)
    const animeTypesChart = ref(null)
    const mangaTypesChart = ref(null)
    const ratingDistributionChart = ref(null)
    const sourceMaterialChart = ref(null)
    const demographicsChart = ref(null)
    const sourcePerformanceChart = ref(null)
    const yearTimelineChart = ref(null)
    const seasonChart = ref(null)
    const seasonPerformanceChart = ref(null)
    const broadcastDaysChart = ref(null)
    const timeSlotsChart = ref(null)
    const membersDistributionChart = ref(null)
    const popularityScoreChart = ref(null)
    const rankScoreChart = ref(null)
    const membersScoreChart = ref(null)
    const episodeDistributionChart = ref(null)
    const chapterDistributionChart = ref(null)
    const volumeDistributionChart = ref(null)
    const topAuthorsChart = ref(null)
    const bestAuthorsChart = ref(null)
    const topSerializationsChart = ref(null)

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

    // Color schemes
    const colors = {
      primary: '#6366f1',
      secondary: '#8b5cf6',
      accent: '#06b6d4',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      anime: '#ff6b6b',
      manga: '#4ecdc4',
      pink: '#ec4899',
      purple: '#8b5cf6',
      blue: '#3b82f6',
      cyan: '#06b6d4',
      teal: '#14b8a6',
      green: '#10b981',
      yellow: '#f59e0b',
      orange: '#f97316',
      red: '#ef4444',
      slate: '#64748b',
    }

    const chartColors = [
      '#FF6384',
      '#36A2EB',
      '#FFCE56',
      '#4BC0C0',
      '#9966FF',
      '#FF9F40',
      '#FF6384',
      '#C9CBCF',
      '#4BC0C0',
      '#FF6384',
      '#8b5cf6',
      '#06b6d4',
      '#10b981',
      '#f59e0b',
      '#ef4444',
      '#ec4899',
      '#14b8a6',
      '#f97316',
      '#3b82f6',
      '#64748b',
    ]

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

    // Helper function to destroy chart
    const destroyChart = (chartKey) => {
      const instance = chartInstances.value.get(chartKey)
      if (instance) {
        instance.destroy()
        chartInstances.value.delete(chartKey)
      }
    }

    // Helper function to create chart
    const createChart = (canvasRef, chartKey, config) => {
      if (!canvasRef.value) return

      destroyChart(chartKey)

      const ctx = canvasRef.value.getContext('2d')
      const instance = new Chart(ctx, config)
      chartInstances.value.set(chartKey, instance)

      return instance
    }

    // Create all charts
    const createAllCharts = () => {
      createScoreDistributionChart()
      createRatingPerformanceChart()
      createTopGenresChart()
      createGenrePerformanceChart()
      createGenreCombinationsChart()
      createTopStudiosChart()
      createBestStudiosChart()
      createTopProducersChart()
      createAnimeTypesChart()
      createMangaTypesChart()
      createRatingDistributionChart()
      createSourceMaterialChart()
      createDemographicsChart()
      createSourcePerformanceChart()
      createYearTimelineChart()
      createSeasonChart()
      createSeasonPerformanceChart()
      createBroadcastDaysChart()
      createTimeSlotsChart()
      createMembersDistributionChart()
      createPopularityScoreChart()
      createRankScoreChart()
      createMembersScoreChart()
      createEpisodeDistributionChart()
      createChapterDistributionChart()
      createVolumeDistributionChart()
      createTopAuthorsChart()
      createBestAuthorsChart()
      createTopSerializationsChart()
    }

    // Individual chart creation functions
    const createScoreDistributionChart = () => {
      const animeData = stats.value.scores?.anime_distribution || {}
      const mangaData = stats.value.scores?.manga_distribution || {}

      createChart(scoreDistributionChart, 'scoreDistribution', {
        type: 'bar',
        data: {
          labels: Object.keys(animeData),
          datasets: [
            {
              label: 'Anime',
              data: Object.values(animeData),
              backgroundColor: colors.anime + '80',
              borderColor: colors.anime,
              borderWidth: 2,
            },
            {
              label: 'Manga',
              data: Object.values(mangaData),
              backgroundColor: colors.manga + '80',
              borderColor: colors.manga,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'top' },
            tooltip: {
              callbacks: {
                label: (context) => `${context.dataset.label}: ${context.raw.toLocaleString()}`,
              },
            },
          },
          scales: {
            y: {
              type: 'logarithmic',
              beginAtZero: false,
              grid: { color: '#374151' },
              ticks: {
                callback: (value) => Number(value.toString()),
              },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { duration: 2000, easing: 'easeOutQuart' },
        },
      })
    }

    const createRatingPerformanceChart = () => {
      const data = stats.value.classification?.rating_scores || {}

      createChart(ratingPerformanceChart, 'ratingPerformance', {
        type: 'polarArea',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: chartColors.map((color) => color + '80'),
              borderColor: chartColors,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          scales: {
            r: {
              beginAtZero: true,
              grid: { color: '#374151' },
              ticks: { color: '#94a3b8' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createTopGenresChart = () => {
      const data = stats.value.genres?.top_combined || {}

      createChart(topGenresChart, 'topGenres', {
        type: 'doughnut',
        data: {
          labels: Object.keys(data).slice(0, 10),
          datasets: [
            {
              data: Object.keys(data)
                .slice(0, 10)
                .map((key) => data[key].total),
              backgroundColor: chartColors,
              borderWidth: 3,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const genre = context.label
                  const genreData = data[genre]
                  return `${genre}: ${genreData.total.toLocaleString()} (A:${genreData.anime}, M:${genreData.manga})`
                },
              },
            },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    }

    const createGenrePerformanceChart = () => {
      const data = stats.value.genres?.performance || {}
      const sortedGenres = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)

      createChart(genrePerformanceChart, 'genrePerformance', {
        type: 'bar',
        data: {
          labels: sortedGenres.map(([genre]) => genre),
          datasets: [
            {
              label: 'Average Score',
              data: sortedGenres.map(([, score]) => score),
              backgroundColor: colors.success + '80',
              borderColor: colors.success,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
            y: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 100, duration: 1500 },
        },
      })
    }

    const createGenreCombinationsChart = () => {
      const data = stats.value.genres?.combinations || []

      createChart(genreCombinationsChart, 'genreCombinations', {
        type: 'bar',
        data: {
          labels: data.slice(0, 10).map((item) => item.pair),
          datasets: [
            {
              label: 'Frequency',
              data: data.slice(0, 10).map((item) => item.count),
              backgroundColor: colors.purple + '80',
              borderColor: colors.purple,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 20 ? label.substring(0, 20) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 150, duration: 1500 },
        },
      })
    }

    const createTopStudiosChart = () => {
      const data = stats.value.studios?.top_by_count || {}
      const sortedStudios = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)

      createChart(topStudiosChart, 'topStudios', {
        type: 'bar',
        data: {
          labels: sortedStudios.map(([studio]) => studio),
          datasets: [
            {
              label: 'Anime Count',
              data: sortedStudios.map(([, count]) => count),
              backgroundColor: colors.blue + '80',
              borderColor: colors.blue,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 100, duration: 1500 },
        },
      })
    }

    const createBestStudiosChart = () => {
      const data = stats.value.studios?.best_by_score || {}
      const sortedStudios = Object.entries(data)
        .sort((a, b) => b[1].avg_score - a[1].avg_score)
        .slice(0, 10)

      createChart(bestStudiosChart, 'bestStudios', {
        type: 'bar',
        data: {
          labels: sortedStudios.map(([studio]) => studio),
          datasets: [
            {
              label: 'Average Score',
              data: sortedStudios.map(([, data]) => data.avg_score),
              backgroundColor: colors.warning + '80',
              borderColor: colors.warning,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const studioData = data[context.label]
                  return `Score: ${context.raw.toFixed(2)} (${studioData.count} anime)`
                },
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 120, duration: 1500 },
        },
      })
    }

    const createTopProducersChart = () => {
      const data = stats.value.studios?.top_producers || {}
      const sortedProducers = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)

      createChart(topProducersChart, 'topProducers', {
        type: 'doughnut',
        data: {
          labels: sortedProducers.map(([producer]) => producer),
          datasets: [
            {
              data: sortedProducers.map(([, count]) => count),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                generateLabels: function (chart) {
                  const data = chart.data
                  if (data.labels.length && data.datasets.length) {
                    return data.labels.map((label, i) => ({
                      text: label.length > 20 ? label.substring(0, 20) + '...' : label,
                      fillStyle: data.datasets[0].backgroundColor[i],
                      index: i,
                    }))
                  }
                  return []
                },
              },
            },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    }

    const createAnimeTypesChart = () => {
      const data = stats.value.classification?.anime_types || {}

      createChart(animeTypesChart, 'animeTypes', {
        type: 'pie',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          animation: { animateRotate: true, duration: 1500 },
        },
      })
    }

    const createMangaTypesChart = () => {
      const data = stats.value.classification?.manga_types || {}

      createChart(mangaTypesChart, 'mangaTypes', {
        type: 'pie',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          animation: { animateRotate: true, duration: 1500 },
        },
      })
    }

    const createRatingDistributionChart = () => {
      const data = stats.value.classification?.ratings || {}

      createChart(ratingDistributionChart, 'ratingDistribution', {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Count',
              data: Object.values(data),
              backgroundColor: colors.error + '80',
              borderColor: colors.error,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: {
              grid: { color: '#374151' },
              ticks: {
                maxRotation: 45,
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    const createSourceMaterialChart = () => {
      const data = stats.value.classification?.source_material || {}
      const sortedSources = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)

      createChart(sourceMaterialChart, 'sourceMaterial', {
        type: 'doughnut',
        data: {
          labels: sortedSources.map(([source]) => source),
          datasets: [
            {
              data: sortedSources.map(([, count]) => count),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    }

    const createDemographicsChart = () => {
      const animeDemo = stats.value.classification?.anime_demographics || {}
      const mangaDemo = stats.value.classification?.manga_demographics || {}

      // Combine demographics
      const allDemographics = new Set([...Object.keys(animeDemo), ...Object.keys(mangaDemo)])

      createChart(demographicsChart, 'demographics', {
        type: 'bar',
        data: {
          labels: Array.from(allDemographics),
          datasets: [
            {
              label: 'Anime',
              data: Array.from(allDemographics).map((demo) => animeDemo[demo] || 0),
              backgroundColor: colors.anime + '80',
              borderColor: colors.anime,
              borderWidth: 2,
            },
            {
              label: 'Manga',
              data: Array.from(allDemographics).map((demo) => mangaDemo[demo] || 0),
              backgroundColor: colors.manga + '80',
              borderColor: colors.manga,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'top' },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1500 },
        },
      })
    }

    const createSourcePerformanceChart = () => {
      const data = stats.value.classification?.source_performance || {}
      const sortedSources = Object.entries(data).sort((a, b) => b[1].avg_score - a[1].avg_score)

      createChart(sourcePerformanceChart, 'sourcePerformance', {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Source Performance',
              data: sortedSources.map(([source, data]) => ({
                x: data.count,
                y: data.avg_score,
                label: source,
              })),
              backgroundColor: colors.cyan + '80',
              borderColor: colors.cyan,
              borderWidth: 2,
              pointRadius: 8,
              pointHoverRadius: 12,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const point = context.raw
                  return `${point.label}: ${point.y.toFixed(2)} score (${point.x} anime)`
                },
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Number of Anime' },
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            y: {
              title: { display: true, text: 'Average Score' },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createYearTimelineChart = () => {
      const data = stats.value.timing?.year_distribution || {}
      const sortedYears = Object.keys(data).sort((a, b) => parseInt(a) - parseInt(b))

      createChart(yearTimelineChart, 'yearTimeline', {
        type: 'line',
        data: {
          labels: sortedYears,
          datasets: [
            {
              label: 'Anime Released',
              data: sortedYears.map((year) => data[year]),
              borderColor: colors.primary,
              backgroundColor: colors.primary + '20',
              fill: true,
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: {
              grid: { color: '#374151' },
              ticks: {
                maxTicksLimit: 20,
              },
            },
          },
          animation: { duration: 2500, easing: 'easeOutCubic' },
        },
      })
    }

    const createSeasonChart = () => {
      const data = stats.value.timing?.season_distribution || {}
      const seasons = ['spring', 'summer', 'fall', 'winter']

      createChart(seasonChart, 'season', {
        type: 'polarArea',
        data: {
          labels: seasons.map((s) => s.charAt(0).toUpperCase() + s.slice(1)),
          datasets: [
            {
              data: seasons.map((season) => data[season] || 0),
              backgroundColor: [
                colors.pink + '80',
                colors.yellow + '80',
                colors.orange + '80',
                colors.blue + '80',
              ],
              borderColor: [colors.pink, colors.yellow, colors.orange, colors.blue],
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          scales: {
            r: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createSeasonPerformanceChart = () => {
      const data = stats.value.timing?.season_performance || {}
      const seasons = Object.keys(data)

      createChart(seasonPerformanceChart, 'seasonPerformance', {
        type: 'radar',
        data: {
          labels: seasons.map((s) => s.charAt(0).toUpperCase() + s.slice(1)),
          datasets: [
            {
              label: 'Average Score',
              data: seasons.map((season) => data[season]?.avg_score || 0),
              backgroundColor: colors.success + '30',
              borderColor: colors.success,
              borderWidth: 2,
              pointBackgroundColor: colors.success,
              pointBorderColor: colors.success,
              pointRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
              pointLabels: { color: '#94a3b8' },
              ticks: { color: '#94a3b8' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createBroadcastDaysChart = () => {
      const data = stats.value.timing?.broadcast_days || {}

      createChart(broadcastDaysChart, 'broadcastDays', {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Broadcast Count',
              data: Object.values(data),
              backgroundColor: colors.purple + '80',
              borderColor: colors.purple,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 150, duration: 1000 },
        },
      })
    }

    const createTimeSlotsChart = () => {
      const data = stats.value.timing?.broadcast_time_slots || {}

      createChart(timeSlotsChart, 'timeSlots', {
        type: 'doughnut',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: [
                colors.yellow + '80',
                colors.orange + '80',
                colors.red + '80',
                colors.purple + '80',
              ],
              borderColor: [colors.yellow, colors.orange, colors.red, colors.purple],
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    }

    const createMembersDistributionChart = () => {
      const data = stats.value.popularity?.members_ranges || {}

      createChart(membersDistributionChart, 'membersDistribution', {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Anime Count',
              data: Object.values(data),
              backgroundColor: colors.cyan + '80',
              borderColor: colors.cyan,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    const createPopularityScoreChart = () => {
      const data = stats.value.popularity?.correlations?.popularity_score || []

      createChart(popularityScoreChart, 'popularityScore', {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Popularity vs Score',
              data: data.map((item) => ({
                x: item.popularity,
                y: item.score,
                title: item.title,
              })),
              backgroundColor: colors.pink + '60',
              borderColor: colors.pink,
              borderWidth: 1,
              pointRadius: 4,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const point = context.raw
                  return `${point.title}: Score ${point.y}, Popularity #${point.x}`
                },
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Popularity Rank (lower = more popular)' },
              reverse: true,
              grid: { color: '#374151' },
            },
            y: {
              title: { display: true, text: 'Score' },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createRankScoreChart = () => {
      const data = stats.value.popularity?.correlations?.rank_score || []

      createChart(rankScoreChart, 'rankScore', {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Rank vs Score',
              data: data.map((item) => ({
                x: item.rank,
                y: item.score,
                title: item.title,
              })),
              backgroundColor: colors.warning + '60',
              borderColor: colors.warning,
              borderWidth: 1,
              pointRadius: 4,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const point = context.raw
                  return `${point.title}: Score ${point.y}, Rank #${point.x}`
                },
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Rank (lower = better)' },
              reverse: true,
              grid: { color: '#374151' },
            },
            y: {
              title: { display: true, text: 'Score' },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createMembersScoreChart = () => {
      const data = stats.value.popularity?.correlations?.members_score || []

      createChart(membersScoreChart, 'membersScore', {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Members vs Score',
              data: data.map((item) => ({
                x: item.members,
                y: item.score,
                title: item.title,
              })),
              backgroundColor: colors.teal + '60',
              borderColor: colors.teal,
              borderWidth: 1,
              pointRadius: 4,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const point = context.raw
                  return `${point.title}: Score ${point.y}, ${point.x.toLocaleString()} members`
                },
              },
            },
          },
          scales: {
            x: {
              title: { display: true, text: 'Members' },
              type: 'logarithmic',
              grid: { color: '#374151' },
            },
            y: {
              title: { display: true, text: 'Score' },
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
          },
          animation: { duration: 2000 },
        },
      })
    }

    const createEpisodeDistributionChart = () => {
      const data = stats.value.content_length?.episode_distribution || {}

      createChart(episodeDistributionChart, 'episodeDistribution', {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Anime Count',
              data: Object.values(data),
              backgroundColor: colors.accent + '80',
              borderColor: colors.accent,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    const createChapterDistributionChart = () => {
      const data = stats.value.content_length?.chapter_distribution || {}

      createChart(chapterDistributionChart, 'chapterDistribution', {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              label: 'Manga Count',
              data: Object.values(data),
              backgroundColor: colors.success + '80',
              borderColor: colors.success,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    const createVolumeDistributionChart = () => {
      const data = stats.value.content_length?.volume_distribution || {}

      createChart(volumeDistributionChart, 'volumeDistribution', {
        type: 'pie',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
          },
          animation: { animateRotate: true, duration: 1500 },
        },
      })
    }

    const createTopAuthorsChart = () => {
      const data = stats.value.creators?.top_authors || {}
      const sortedAuthors = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)

      createChart(topAuthorsChart, 'topAuthors', {
        type: 'bar',
        data: {
          labels: sortedAuthors.map(([author]) => author),
          datasets: [
            {
              label: 'Manga Count',
              data: sortedAuthors.map(([, count]) => count),
              backgroundColor: colors.purple + '80',
              borderColor: colors.purple,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: '#374151' },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 100, duration: 1500 },
        },
      })
    }

    const createBestAuthorsChart = () => {
      const data = stats.value.creators?.best_authors || {}
      const sortedAuthors = Object.entries(data)
        .sort((a, b) => b[1].avg_score - a[1].avg_score)
        .slice(0, 10)

      createChart(bestAuthorsChart, 'bestAuthors', {
        type: 'bar',
        data: {
          labels: sortedAuthors.map(([author]) => author),
          datasets: [
            {
              label: 'Average Score',
              data: sortedAuthors.map(([, data]) => data.avg_score),
              backgroundColor: colors.warning + '80',
              borderColor: colors.warning,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const authorData = data[context.label]
                  return `Score: ${context.raw.toFixed(2)} (${authorData.count} works)`
                },
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 10,
              grid: { color: '#374151' },
            },
            y: {
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  const label = this.getLabelForValue(value)
                  return label.length > 15 ? label.substring(0, 15) + '...' : label
                },
              },
            },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 120, duration: 1500 },
        },
      })
    }

    const createTopSerializationsChart = () => {
      const data = stats.value.creators?.top_serializations || {}
      const sortedSeries = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)

      createChart(topSerializationsChart, 'topSerializations', {
        type: 'doughnut',
        data: {
          labels: sortedSeries.map(([series]) => series),
          datasets: [
            {
              data: sortedSeries.map(([, count]) => count),
              backgroundColor: chartColors,
              borderWidth: 2,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                generateLabels: function (chart) {
                  const data = chart.data
                  if (data.labels.length && data.datasets.length) {
                    return data.labels.map((label, i) => ({
                      text: label.length > 25 ? label.substring(0, 25) + '...' : label,
                      fillStyle: data.datasets[0].backgroundColor[i],
                      index: i,
                    }))
                  }
                  return []
                },
              },
            },
          },
          animation: { animateRotate: true, duration: 2000 },
        },
      })
    }

    // Cleanup function
    const cleanup = () => {
      chartInstances.value.forEach((instance) => {
        if (instance) instance.destroy()
      })
      chartInstances.value.clear()
    }

    // Mount and cleanup
    onMounted(() => {
      fetchStats()
    })

    // Return reactive data and functions
    return {
      loading,
      stats,
      animatedValues,
      overviewCards,

      // Chart refs
      scoreDistributionChart,
      ratingPerformanceChart,
      topGenresChart,
      genrePerformanceChart,
      genreCombinationsChart,
      topStudiosChart,
      bestStudiosChart,
      topProducersChart,
      animeTypesChart,
      mangaTypesChart,
      ratingDistributionChart,
      sourceMaterialChart,
      demographicsChart,
      sourcePerformanceChart,
      yearTimelineChart,
      seasonChart,
      seasonPerformanceChart,
      broadcastDaysChart,
      timeSlotsChart,
      membersDistributionChart,
      popularityScoreChart,
      rankScoreChart,
      membersScoreChart,
      episodeDistributionChart,
      chapterDistributionChart,
      volumeDistributionChart,
      topAuthorsChart,
      bestAuthorsChart,
      topSerializationsChart,

      // Cleanup
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
