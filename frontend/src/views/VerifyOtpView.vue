<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { authApi } from '@/api/endpoints'
import { useAuthStore } from '@/stores/auth'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const err = useApiError()

const phone = (route.query.phone as string) || ''
const redirect = (route.query.redirect as string) || '/'
const code = ref('')
const loading = ref(false)
const cooldown = ref(30)
let timer: number | undefined

function startCooldown(sec: number) {
  cooldown.value = sec
  window.clearInterval(timer)
  timer = window.setInterval(() => {
    if (cooldown.value > 0) cooldown.value--
    else window.clearInterval(timer)
  }, 1000)
}

onMounted(() => {
  if (!phone) router.replace({ name: 'login' })
  else startCooldown(30)
})
onUnmounted(() => window.clearInterval(timer))

async function verify() {
  if (code.value.trim().length < 4) return
  loading.value = true
  try {
    const res = await auth.verifyOtp(phone, code.value.trim())
    router.replace(
      res.profile_completed && !res.is_new
        ? redirect
        : { name: 'setup', query: { redirect } },
    )
  } catch (e) {
    err.show(e)
  } finally {
    loading.value = false
  }
}

async function resend() {
  try {
    await authApi.requestOtp(phone)
    startCooldown(30)
  } catch (e) {
    err.show(e)
  }
}
</script>

<template>
  <div class="center-screen">
    <h2>{{ t('auth.loginTitle') }}</h2>
    <p class="muted" dir="ltr">{{ phone }}</p>
    <div class="field" style="width: 100%; max-width: 320px">
      <label for="code">{{ t('auth.codeLabel') }}</label>
      <InputText
        id="code"
        v-model="code"
        inputmode="numeric"
        maxlength="8"
        dir="ltr"
        style="text-align: center; letter-spacing: 0.4em; font-size: 1.3rem"
        @keyup.enter="verify"
      />
    </div>
    <Button
      :label="t('auth.verify')"
      :loading="loading"
      style="width: 100%; max-width: 320px"
      @click="verify"
    />
    <Button
      :label="cooldown > 0 ? t('auth.resendIn', { sec: cooldown }) : t('auth.resend')"
      text
      :disabled="cooldown > 0"
      @click="resend"
    />
  </div>
</template>
