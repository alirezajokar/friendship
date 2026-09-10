import { ref } from 'vue'
import { notifyApi } from '@/api/endpoints'

// Injected at build time is overkill for one value; fetch it from a meta tag or env.
const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || ''

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  const raw = atob((base64 + padding).replace(/-/g, '+').replace(/_/g, '/'))
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)))
}

export function usePush() {
  const supported = 'serviceWorker' in navigator && 'PushManager' in window
  const busy = ref(false)

  async function enable(): Promise<boolean> {
    if (!supported || !VAPID_PUBLIC_KEY) return false
    busy.value = true
    try {
      const perm = await Notification.requestPermission()
      if (perm !== 'granted') return false
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      })
      await notifyApi.subscribe(sub.toJSON())
      return true
    } finally {
      busy.value = false
    }
  }

  async function disable() {
    if (!supported) return
    const reg = await navigator.serviceWorker.ready
    const sub = await reg.pushManager.getSubscription()
    if (sub) {
      await notifyApi.unsubscribe(sub.toJSON()).catch(() => {})
      await sub.unsubscribe()
    }
  }

  return { supported, busy, enable, disable }
}
