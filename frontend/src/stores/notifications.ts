import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notifyApi, type AppNotification } from '@/api/endpoints'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<AppNotification[]>([])
  const unread = computed(() => items.value.filter((n) => !n.read_at).length)

  async function load() {
    items.value = (await notifyApi.list()).data
  }

  async function markRead(id: number) {
    await notifyApi.markRead(id)
    const n = items.value.find((x) => x.id === id)
    if (n) n.read_at = new Date().toISOString()
  }

  return { items, unread, load, markRead }
})
