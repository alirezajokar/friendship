import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { router } from './router'
import { i18n } from './i18n'
import { installPrimeVue } from './plugins/primevue'
import { setAuthLostHandler } from './api/client'
import { useAuthStore } from './stores/auth'

import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
installPrimeVue(app)

setAuthLostHandler(() => {
  useAuthStore().me = null
  router.replace({ name: 'login' })
})

app.mount('#app')

if ('serviceWorker' in navigator) {
  import('virtual:pwa-register').then(({ registerSW }) => registerSW({ immediate: true }))
}
