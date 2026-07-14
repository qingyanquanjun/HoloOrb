import { createRouter, createWebHistory } from 'vue-router'
import { menuConfig, flattenMenuRoutes } from '@/config/menu'
import { useUserStore } from '@/stores/user'
import { getCurrentUser } from '@/api/users'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      ...flattenMenuRoutes(menuConfig),
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const hasToken = userStore.token

  if (to.path === '/login') {
    if (hasToken) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    if (hasToken) {
      if (!userStore.userInfo) {
        try {
          const userData = await getCurrentUser()
          userStore.setUserInfo(userData)
        } catch (e) {
          userStore.logout()
          next('/login')
          return
        }
      }
      next()
    } else {
      next('/login')
    }
  }
})

export default router