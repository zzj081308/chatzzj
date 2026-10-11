import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/appeal',
      name: 'Appeal',
      component: () => import('../views/AppealView.vue'),
    },
    {
      path: '/chat/:friendId?',
      name: 'Chat',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      redirect: '/chat',
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/chat',
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('../views/admin/Dashboard.vue'),
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: () => import('../views/admin/UserManagement.vue'),
        },
        {
          path: 'messages',
          name: 'AdminMessages',
          component: () => import('../views/admin/MessageManagement.vue'),
        },
        {
          path: 'settings',
          name: 'AdminSettings',
          component: () => import('../views/admin/Settings.vue'),
        },
        {
          path: 'appeals',
          name: 'AdminAppeals',
          component: () => import('../views/admin/AdminAppeals.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to, _from) => {
  const authStore = useAuthStore()
  authStore.restoreSession()

  if (to.meta.requiresAdmin && (!authStore.isAuthenticated || !authStore.user?.is_admin)) {
    return '/chat'
  }
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return '/chat'
  }
})

export default router
