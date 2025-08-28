<template>
  <div
    class="max-w-[1400px] mx-auto p-8 bg-gradient-to-br from-slate-800 to-slate-950 min-h-screen text-white"
  >
    <!-- Header -->
    <div class="text-center mb-12">
      <h1
        class="text-5xl font-extrabold mb-4 bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent"
      >
        📊 Database Statistics
      </h1>
      <p class="text-xl text-slate-400">Comprehensive analysis of our anime and manga collection</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-[400px]">
      <div
        class="w-10 h-10 border-4 border-slate-700 border-t-indigo-500 rounded-full animate-spin mb-4"
      ></div>
      <p>Loading statistics...</p>
    </div>

    <!-- Overview + Charts -->
    <div v-else class="flex flex-col gap-12">
      <!-- Overview Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        <div
          v-for="(card, index) in overviewCards"
          :key="index"
          class="flex items-center gap-6 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 transition transform hover:-translate-y-2 hover:shadow-2xl hover:border-indigo-500/40"
        >
          <div class="text-4xl">{{ card.icon }}</div>
          <div class="flex-1">
            <h3 class="text-sm text-slate-400 font-medium mb-1">{{ card.title }}</h3>
            <div class="text-2xl font-extrabold mb-1">{{ animatedValues[card.key] || 0 }}</div>
            <p class="text-xs text-slate-500">{{ card.description }}</p>
          </div>
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        <!-- Top Genres -->
        <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-center mb-6">🎭 Top Genres (Combined)</h3>
          <canvas ref="genresChart"></canvas>
        </div>

        <!-- Anime Types -->
        <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-center mb-6">📺 Anime Types Distribution</h3>
          <canvas ref="animeTypesChart"></canvas>
        </div>

        <!-- Manga Types -->
        <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-center mb-6">📖 Manga Types Distribution</h3>
          <canvas ref="mangaTypesChart"></canvas>
        </div>

        <!-- Score Distribution (full width) -->
        <div
          class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 md:col-span-2 xl:col-span-3"
        >
          <h3 class="text-lg font-semibold text-center mb-6">
            📈 Score Distribution Comparison (Logarithmic)
          </h3>
          <canvas ref="scoreDistributionChart"></canvas>
        </div>

        <!-- Anime Years Timeline (full width) -->
        <div
          class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 md:col-span-2 xl:col-span-3"
        >
          <h3 class="text-lg font-semibold text-center mb-6">📅 Anime Release Timeline</h3>
          <canvas ref="animeYearsChart"></canvas>
        </div>

        <!-- Episode Distribution -->
        <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-center mb-6">⏱️ Episode Distribution</h3>
          <canvas ref="episodeChart"></canvas>
        </div>

        <!-- Chapter Distribution -->
        <div class="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-center mb-6">📄 Chapter Distribution</h3>
          <canvas ref="chapterChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'Stats',
  setup() {
    const loading = ref(true)
    const animatedValues = ref({})

    // Chart refs
    const scoreDistributionChart = ref(null)
    const genresChart = ref(null)
    const animeTypesChart = ref(null)
    const mangaTypesChart = ref(null)
    const animeYearsChart = ref(null)
    const episodeChart = ref(null)
    const chapterChart = ref(null)

    // Chart instances
    const scoreDistributionChartInstance = ref(null)
    const genresChartInstance = ref(null)
    const animeTypesChartInstance = ref(null)
    const mangaTypesChartInstance = ref(null)
    const animeYearsChartInstance = ref(null)
    const episodeChartInstance = ref(null)
    const chapterChartInstance = ref(null)

    // Data
    const animeStats = ref({})
    const mangaStats = ref({})
    const overviewStats = ref({})

    // Overview cards data
    const overviewCards = ref([
      { icon: '📺', title: 'Total Anime', key: 'total_anime', description: 'Anime in database' },
      { icon: '📖', title: 'Total Manga', key: 'total_manga', description: 'Manga in database' },
      { icon: '📊', title: 'Combined Total', key: 'total_items', description: 'Total entries' },
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
    ])

    // Chart colors
    const colors = {
      primary: '#6366f1',
      secondary: '#8b5cf6',
      accent: '#06b6d4',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      anime: '#ff6b6b',
      manga: '#4ecdc4',
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
    ]

    // Fetch API data
    const fetchStats = async () => {
      try {
        const [animeRes, mangaRes, overviewRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/stats/anime'),
          fetch('http://127.0.0.1:8000/stats/manga'),
          fetch('http://127.0.0.1:8000/stats/overview'),
        ])

        animeStats.value = await animeRes.json()
        mangaStats.value = await mangaRes.json()
        overviewStats.value = await overviewRes.json()

        animateNumbers()

        // Show charts
        loading.value = false

        // Wait until <canvas> elements exist
        await nextTick()

        // Create all charts
        createCharts()
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        loading.value = false
      }
    }

    // Number animation
    const animateNumbers = () => {
      overviewCards.value.forEach((card) => {
        const target = overviewStats.value[card.key] || 0
        animateValue(card.key, 0, target, 2000, target % 1 !== 0)
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

    // Create charts
    const createCharts = () => {
      createScoreDistributionChart()
      createGenresChart()
      createAnimeTypesChart()
      createMangaTypesChart()
      createAnimeYearsChart()
      createEpisodeChart()
      createChapterChart()
    }

    // Helper to destroy previous chart instance
    const destroyChart = (chartRef) => {
      if (chartRef?.value) chartRef.value.destroy()
    }

    const createScoreDistributionChart = () => {
      if (scoreDistributionChartInstance.value) scoreDistributionChartInstance.value.destroy()

      const ctx = scoreDistributionChart.value.getContext('2d')
      const labels = Object.keys(animeStats.value.score_distribution || {})
      const animeData = Object.values(animeStats.value.score_distribution || {})
      const mangaData = Object.values(mangaStats.value.score_distribution || {})

      scoreDistributionChartInstance.value = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'Anime',
              data: animeData,
              backgroundColor: colors.anime + '80',
              borderColor: colors.anime,
              borderWidth: 2,
            },
            {
              label: 'Manga',
              data: mangaData,
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
              enabled: true,
              callbacks: {
                label: function (context) {
                  return `${context.dataset.label}: ${context.raw.toLocaleString()}`
                },
              },
            },
          },
          scales: {
            y: {
              type: 'logarithmic', // makes small bars visible
              beginAtZero: false, // cannot be zero for log scale
              grid: { color: '#374151' },
              ticks: {
                callback: function (value) {
                  return Number(value.toString()) // shows nice integer numbers
                },
              },
            },
            x: { grid: { color: '#374151' } },
          },
          animation: { duration: 2000, easing: 'easeOutQuart' },
        },
      })
    }

    const createGenresChart = () => {
      if (genresChartInstance.value) genresChartInstance.value.destroy()
      const ctx = genresChart.value.getContext('2d')
      const data = overviewStats.value.top_genres_combined || {}
      genresChartInstance.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data),
          datasets: [
            {
              data: Object.values(data).map((g) => g.total),
              backgroundColor: chartColors,
              borderWidth: 3,
              borderColor: '#1f2937',
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom' } },
          animation: { animateRotate: true, animateScale: true, duration: 2000 },
        },
      })
    }

    const createAnimeTypesChart = () => {
      if (animeTypesChartInstance.value) animeTypesChartInstance.value.destroy()
      const ctx = animeTypesChart.value.getContext('2d')
      const data = animeStats.value.type_distribution || {}
      animeTypesChartInstance.value = new Chart(ctx, {
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
          plugins: { legend: { position: 'bottom' } },
          animation: { animateRotate: true, duration: 1500 },
        },
      })
    }

    const createMangaTypesChart = () => {
      if (mangaTypesChartInstance.value) mangaTypesChartInstance.value.destroy()
      const ctx = mangaTypesChart.value.getContext('2d')
      const data = mangaStats.value.type_distribution || {}
      mangaTypesChartInstance.value = new Chart(ctx, {
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
          plugins: { legend: { position: 'bottom' } },
          animation: { animateRotate: true, duration: 1500 },
        },
      })
    }

    const createAnimeYearsChart = () => {
      if (animeYearsChartInstance.value) animeYearsChartInstance.value.destroy()
      const ctx = animeYearsChart.value.getContext('2d')
      const yearsData = animeStats.value.year_distribution || {}

      // Sort years ascending
      const sortedYears = Object.keys(yearsData).sort((a, b) => a - b)
      const counts = sortedYears.map((y) => yearsData[y])

      animeYearsChartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: sortedYears,
          datasets: [
            {
              label: 'Anime Released',
              data: counts,
              borderColor: colors.primary,
              backgroundColor: colors.primary + '20',
              fill: true,
              tension: 0.4,
              pointRadius: 4,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true, grid: { color: '#374151' } },
            x: { grid: { color: '#374151' } },
          },
          animation: { duration: 2500, easing: 'easeOutCubic' },
        },
      })
    }

    const createEpisodeChart = () => {
      if (episodeChartInstance.value) episodeChartInstance.value.destroy()
      const ctx = episodeChart.value.getContext('2d')
      const data = animeStats.value.episode_distribution || {}
      episodeChartInstance.value = new Chart(ctx, {
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
          scales: {
            y: { beginAtZero: true, grid: { color: '#374151' } },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    const createChapterChart = () => {
      if (chapterChartInstance.value) chapterChartInstance.value.destroy()
      const ctx = chapterChart.value.getContext('2d')
      const data = mangaStats.value.chapter_distribution || {}
      chapterChartInstance.value = new Chart(ctx, {
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
          scales: {
            y: { beginAtZero: true, grid: { color: '#374151' } },
            x: { grid: { color: '#374151' } },
          },
          animation: { delay: (ctx) => ctx.dataIndex * 200, duration: 1000 },
        },
      })
    }

    onMounted(fetchStats)

    return {
      loading,
      animatedValues,
      overviewCards,
      scoreDistributionChart,
      genresChart,
      animeTypesChart,
      mangaTypesChart,
      animeYearsChart,
      episodeChart,
      chapterChart,
    }
  },
}
</script>
