import { createRouter, createWebHistory } from 'vue-router'
import HotTopicsView from './views/HotTopicsView.vue'
import HistoryView from './views/HistoryView.vue'
import AdminView from './views/AdminView.vue'
import RecycleBinView from './views/RecycleBinView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'hot-topics',
      component: HotTopicsView
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    },
    {
      path: '/recycle-bin',
      name: 'recycle-bin',
      component: RecycleBinView
    }
  ]
})

export default router