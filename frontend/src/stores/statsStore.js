import { defineStore } from 'pinia'

export const useStatsStore = defineStore('stats', {
  state: () => ({
    stats: {},
    loading: false,
    lastFetched: null,
    cacheExpiry: 5 * 60 * 1000,
  }),

  getters: {
    isDataFresh: (state) => {
      if (!state.lastFetched) return false
      return Date.now() - state.lastFetched < state.cacheExpiry
    },

    hasData: (state) => {
      return Object.keys(state.stats).length > 0
    },
  },

  actions: {
    async fetchStats(forceRefresh = false) {
      if (!forceRefresh && this.hasData && this.isDataFresh) {
        return this.stats
      }

      this.loading = true

      try {
        const response = await fetch('http://127.0.0.1:8000/stats/')
        const data = await response.json()

        this.stats = data
        this.lastFetched = Date.now()
        console.log('Stats fetched and cached:', data)

        return data
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    clearCache() {
      this.stats = {}
      this.lastFetched = null
    },
  },

  persist: {
    key: 'anime-stats',
    storage: localStorage,
    paths: ['stats', 'lastFetched'],
  },
})
