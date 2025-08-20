<template>
  <header
    class="fixed top-0 left-0 w-full bg-white/20 group hover:bg-white/90 backdrop-blur-md transition-colors duration-300 shadow-md z-50 h-16"
  >
    <div class="max-w-7xl mx-auto h-full flex items-center justify-between px-4 md:px-8">
      <!-- Logo + Text -->
      <router-link to="/home" class="flex items-center space-x-2">
        <img src="/logo.jpg" alt="Logo" class="h-10 w-auto" />
        <span
          class="text-white group-hover:text-gray-900 font-bold uppercase text-lg tracking-wide logo-text transition-colors duration-300"
        >
          MAL Discovery
        </span>
      </router-link>

      <!-- Centered Nav (Desktop only) -->
      <nav class="hidden md:flex space-x-8">
        <router-link
          v-for="link in links"
          :key="link.name"
          :to="link.to"
          class="px-3 py-2 rounded-md font-medium transition-colors duration-300"
          :class="[
            $route.path === link.to
              ? 'text-blue-600'
              : 'text-white group-hover:text-gray-900 hover:text-blue-600',
          ]"
        >
          {{ link.name }}
        </router-link>
      </nav>

      <!-- Profile (Desktop only) -->
      <router-link to="/home" class="hidden md:flex items-center space-x-2">
        <img src="/profile.jpg" alt="Profile" class="h-10 w-auto rounded-full" />
        <span
          class="text-white group-hover:text-gray-900 font-bold text-lg transition-colors duration-300"
        >
          Profile
        </span>
      </router-link>

      <!-- Mobile menu button -->
      <div class="md:hidden">
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="text-white group-hover:text-gray-900 hover:text-blue-600 focus:outline-none transition-colors duration-300"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              v-if="!mobileMenuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 8h16M4 16h16"
            />
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="md:hidden bg-white/90 backdrop-blur-md shadow-inner">
      <nav class="px-4 pt-4 pb-4 space-y-1">
        <router-link
          v-for="link in links"
          :key="link.name + '-mobile'"
          :to="link.to"
          class="block px-3 py-2 rounded-md text-gray-900 hover:text-blue-600 font-medium transition-colors duration-300"
          @click="mobileMenuOpen = false"
        >
          {{ link.name }}
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const mobileMenuOpen = ref(false)

const links = [
  { name: 'Home', to: '/home' },
  { name: 'Anime', to: '/anime' },
  { name: 'Manga', to: '/manga' },
  { name: 'Browse', to: '/browse' },
  { name: 'Stats', to: '/stats' },
  { name: 'Recommend', to: '/recommend' },
]
</script>

<style scoped>
header {
  transition:
    background-color 0.3s ease,
    backdrop-filter 0.3s ease;
}

.logo-text {
  font-family: 'Roboto Condensed', sans-serif;
}
</style>
