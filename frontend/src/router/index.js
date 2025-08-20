import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Anime from '../views/Anime.vue'
import Manga from '../views/Manga.vue'
import Browse from '../views/Browse.vue'
import Stats from '../views/Stats.vue'
import Recommend from '../views/Recommend.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: Home },
  { path: '/anime', name: 'Anime', component: Anime },
  { path: '/manga', name: 'Manga', component: Manga },
  { path: '/browse', name: 'Browse', component: Browse },
  { path: '/stats', name: 'Stats', component: Stats },
  { path: '/recommend', name: 'Recommend', component: Recommend },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
