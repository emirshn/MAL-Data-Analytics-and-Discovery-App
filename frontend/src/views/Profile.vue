<template>
  <div class="p-4 pt-24 min-h-screen text-white bg-gray-900 relative">
    <h1 id="mock-text" class="text-5xl font-bold text-center mb-8 flex justify-center flex-wrap">
      <span
        v-for="(char, index) in letters"
        :key="index"
        class="letter"
        :style="{ 'animation-delay': Math.random() * 0.5 + 's', color: getRandomColor() }"
      >
        {{ char }}
      </span>
    </h1>

    <div v-if="showVideo" class="w-full max-w-3xl mx-auto aspect-video mt-4">
      <iframe
        class="w-full h-full rounded-lg shadow-lg animate-pulse"
        src="https://www.youtube.com/embed/2GgiZZhO-PA?autoplay=1&mute=1"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>

    <div v-if="showVideo" class="mt-4 flex justify-center items-center">
      <p
        class="bg-purple-700/80 text-white text-lg md:text-xl font-bold px-6 py-3 rounded-lg animate-bounce shadow-lg"
      >
        🎉 You can use your mouse now! 🎉
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { headerLock } from '@/stores/headerLock.js'

const text = 'This is a mock page'
const letters = text.split('')

const showVideo = ref(false)

const colors = ['yellow', 'cyan', 'magenta', 'lime', 'orange', 'pink']
const getRandomColor = () => colors[Math.floor(Math.random() * colors.length)]

onMounted(() => {
  headerLock.unlocked = false

  setTimeout(() => {
    showVideo.value = true
    headerLock.unlocked = true
  }, 3000)
})
</script>

<style scoped>
.letter {
  display: inline-block;
  animation: jump 0.6s infinite;
}

@keyframes jump {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-8px) rotate(-3deg);
  }
  50% {
    transform: translateY(0) rotate(2deg);
  }
  75% {
    transform: translateY(-4px) rotate(-2deg);
  }
  100% {
    transform: translateY(0) rotate(0deg);
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-pulse {
  animation: pulse 0.3s ease-in-out 1;
}
</style>
