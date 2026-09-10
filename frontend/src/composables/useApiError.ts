import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

const MAP: Record<string, string> = {
  otp_invalid: 'auth.wrongCode',
  otp_invalid_or_expired: 'auth.wrongCode',
  otp_too_many_attempts: 'auth.tooManyAttempts',
  otp_rate_limited: 'auth.rateLimited',
  already_claimed: 'wishlist.claimTaken',
}

export function useApiError() {
  const toast = useToast()
  const { t } = useI18n()

  function messageFor(err: unknown): string {
    if (axios.isAxiosError(err)) {
      const detail = (err.response?.data as { detail?: string } | undefined)?.detail
      const code = detail?.split(':')[0] ?? ''
      if (code && MAP[code]) return t(MAP[code])
    }
    return t('common.error')
  }

  function show(err: unknown) {
    toast.add({ severity: 'error', summary: messageFor(err), life: 4000 })
  }

  return { messageFor, show }
}
