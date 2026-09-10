import type { App } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import 'primeicons/primeicons.css'

export function installPrimeVue(app: App) {
  app.use(PrimeVue, {
    ripple: true,
    theme: {
      preset: Aura,
      options: { darkModeSelector: '.dark', cssLayer: false },
    },
  })
  app.use(ToastService)
  app.use(ConfirmationService)
}
