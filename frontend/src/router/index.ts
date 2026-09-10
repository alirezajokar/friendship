import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/verify', name: 'verify', component: () => import('@/views/VerifyOtpView.vue'), meta: { public: true } },
  { path: '/i/:code', name: 'invite', component: () => import('@/views/InviteLandingView.vue'), meta: { public: true } },
  { path: '/setup', name: 'setup', component: () => import('@/views/ProfileSetupView.vue'), meta: { requiresAuth: true, allowIncompleteProfile: true } },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { requiresAuth: true } },
  { path: '/friends', name: 'friends', component: () => import('@/views/FriendsView.vue'), meta: { requiresAuth: true } },
  { path: '/friends/requests', name: 'friend-requests', component: () => import('@/views/FriendRequestsView.vue'), meta: { requiresAuth: true } },
  { path: '/wishlist', name: 'wishlist', component: () => import('@/views/WishlistMineView.vue'), meta: { requiresAuth: true } },
  { path: '/wishlist/:userId', name: 'friend-wishlist', component: () => import('@/views/WishlistFriendView.vue'), meta: { requiresAuth: true } },
  { path: '/notifications', name: 'notifications', component: () => import('@/views/NotificationsView.vue'), meta: { requiresAuth: true } },
  { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) await auth.hydrate()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (auth.isAuthenticated && !auth.profileComplete && !to.meta.allowIncompleteProfile && !to.meta.public) {
    return { name: 'setup' }
  }
  if (auth.isAuthenticated && (to.name === 'login' || to.name === 'verify')) {
    return { name: 'home' }
  }
  return true
})
