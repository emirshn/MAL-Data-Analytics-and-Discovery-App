<template>
  <div class="p-4 pt-24 min-h-screen bg-gray-900 text-white">
    <!-- Header text -->
    <h1 class="text-5xl font-bold text-center mb-8">Welcome to MAL Discovery</h1>

    <!-- Description -->
    <p class="text-center text-lg md:text-xl mb-12 max-w-3xl mx-auto text-gray-300">
      This platform helps you explore anime and manga data in depth. Use the navigation above to
      access different pages and discover their functionalities.
    </p>

    <!-- Page explanations -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
      <!-- Example card -->
      <div
        class="bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
      >
        <h2 class="text-2xl font-semibold mb-2 text-blue-400">Anime Page</h2>
        <p class="text-gray-300 text-sm">
          Explore anime entries, search by title, filter by score, and view recommendations based on
          your selected titles including AI-generated recommendations.
        </p>
      </div>

      <div
        class="bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
      >
        <h2 class="text-2xl font-semibold mb-2 text-green-400">Manga Page</h2>
        <p class="text-gray-300 text-sm">
          Explore manga entries, search by title, filter by score, and view recommendations based on
          your selected titles.
        </p>
      </div>

      <div
        class="bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
      >
        <h2 class="text-2xl font-semibold mb-2 text-purple-400">Topology Page</h2>
        <p class="text-gray-300 text-sm">
          Visualize relationships between anime and manga using hierarchical graphs. Analyze
          clusters and see how different titles connect. (Work in progress, it can be slow)
        </p>
      </div>

      <div
        class="bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
      >
        <h2 class="text-2xl font-semibold mb-2 text-yellow-400">Stats Page</h2>
        <p class="text-gray-300 text-sm">
          Access detailed statistics about anime, manga, genres, authors, and user ratings. Compare
          trends over years and top-rated works.
        </p>
      </div>

      <div
        class="bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
      >
        <h2 class="text-2xl font-semibold mb-2 text-red-400">Recommend Page</h2>
        <p class="text-gray-300 text-sm">
          Generate personalized recommendations by selecting your favorite anime titles. Filter by
          score, sequels, and see explanations.
        </p>
      </div>
    </div>

    <!-- Optional footer note -->
    <p class="text-center text-gray-500 mt-12 text-sm">
      Navigate through the sections above to explore all features of MAL Discovery.
    </p>
  </div>
</template>

<script setup></script>

<style scoped>
.bg-gray-800:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}
</style>
