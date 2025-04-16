import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView,
        },
        {
          path: 'about',
          name: 'about',
          component: () => import('../views/AboutView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'projects',
          name: 'projects',
          component: () => import('../views/ProjectView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: () => import('@/views/ProjectDetailView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'agents',
          name: 'agents',
          component: () => import('../views/AgentsView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('../views/DocumentsView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'playground',
          name: 'playground',
          component: () => import('../views/PlaygroundView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'files',
          name: 'files',
          component: () => import('../views/FilesView.vue'),
          meta: { transition: 'slide-right' },
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('../views/SettingsView.vue'),
          meta: { transition: 'slide-right' },
        },
      ],
    },
  ],
})

export default router
