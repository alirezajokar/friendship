<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { authApi } from '@/api/endpoints'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const err = useApiError()

const phone = ref('')
const loading = ref(false)

async function submit() {
  if (!phone.value.trim()) return
  loading.value = true
  try {
    await authApi.requestOtp(phone.value.trim())
    router.push({
      name: 'verify',
      query: { phone: phone.value.trim(), redirect: route.query.redirect as string | undefined },
    })
  } catch (e) {
    err.show(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="center-screen">
    <h1>{{ t('app.name') }}</h1>
    <p class="muted" style="text-align: center">{{ t('auth.loginHint') }}</p>
    <div class="field" style="width: 100%; max-width: 320px">
      <label for="phone">{{ t('auth.phoneLabel') }}</label>
      <InputText
        id="phone"
        v-model="phone"
        :placeholder="t('auth.phonePlaceholder')"
        inputmode="tel"
        dir="ltr"
        @keyup.enter="submit"
      />
    </div>
    <Button
      :label="t('auth.sendCode')"
      :loading="loading"
      style="width: 100%; max-width: 320px"
      @click="submit"
    />
  </div>
</template>
