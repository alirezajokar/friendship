import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi, type Me } from '@/api/endpoints'

export const useAuthStore = defineStore('auth', () => {
  const me = ref<Me | null>(null)
  const ready = ref(false)

  const isAuthenticated = computed(() => me.value !== null)
  const profileComplete = computed(() => !!me.value?.profile_completed)

  async function hydrate() {
    try {
      me.value = (await authApi.me()).data
    } catch {
      me.value = null
    } finally {
      ready.value = true
    }
  }

  async function verifyOtp(phone: string, code: string) {
    const res = await authApi.verifyOtp(phone, code)
    await hydrate()
    return res.data
  }

  async function updateProfile(body: Record<string, unknown>) {
    me.value = (await userApi.updateProfile(body)).data
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      me.value = null
    }
  }

  return { me, ready, isAuthenticated, profileComplete, hydrate, verifyOtp, updateProfile, logout }
})
