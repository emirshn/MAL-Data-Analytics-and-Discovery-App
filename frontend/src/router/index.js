import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Anime from '../views/Anime.vue'
import Manga from '../views/Manga.vue'
import Stats from '../views/Stats.vue'
import Recommend from '../views/Recommend.vue'
import AnimeDetail from '../views/AnimeDetail.vue'
import MangaDetail from '../views/MangaDetail.vue'
import Topology from '@/views/Topology.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: Home },
  { path: '/anime', name: 'Anime', component: Anime },
  { path: '/anime/:id', name: 'AnimeDetail', component: AnimeDetail, props: true },
  { path: '/manga', name: 'Manga', component: Manga },
  { path: '/manga/:id', name: 'MangaDetail', component: MangaDetail, props: true },
  { path: '/topology', name: 'Topology', component: Topology },
  { path: '/stats', name: 'Stats', component: Stats },
  { path: '/recommend', name: 'Recommend', component: Recommend },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
