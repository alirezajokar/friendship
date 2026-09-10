<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Card from 'primevue/card'
import Button from 'primevue/button'
import ToggleSwitch from 'primevue/toggleswitch'
import SelectButton from 'primevue/selectbutton'
import { notifyApi } from '@/api/endpoints'
import { useAuthStore } from '@/stores/auth'
import { usePush } from '@/composables/usePush'
import { setLocale, currentLocale, type LocaleCode } from '@/i18n'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const push = usePush()
const err = useApiError()

const webPush = ref(true)
const email = ref(true)
const locale = ref<LocaleCode>(currentLocale())
const localeOptions = [
  { label: 'فارسی', value: 'fa' },
  { label: 'English', value: 'en' },
]

async function loadPrefs() {
  const p = (await notifyApi.getPrefs()).data
  webPush.value = p.web_push
  email.value = p.email
}

async function savePrefs() {
  try {
    await notifyApi.setPrefs({ web_push: webPush.value, email: email.value })
  } catch (e) {
    err.show(e)
  }
}

async function enablePush() {
  const ok = await push.enable()
  if (ok) {
    webPush.value = true
    await savePrefs()
  }
}

function changeLocale(code: LocaleCode) {
  setLocale(code)
  locale.value = code
}

async function logout() {
  await auth.logout()
  router.replace({ name: 'login' })
}

onMounted(loadPrefs)
</script>

<template>
  <div class="page">
    <h2>{{ t('settings.title') }}</h2>

    <Card>
      <template #title>{{ t('settings.notifChannels') }}</template>
      <template #content>
        <div class="row-between" style="margin-bottom: 0.75rem">
          <span>{{ t('settings.webPush') }}</span>
          <ToggleSwitch v-model="webPush" @change="savePrefs" />
        </div>
        <div class="row-between">
          <span>{{ t('settings.email') }}</span>
          <ToggleSwitch v-model="email" @change="savePrefs" />
        </div>
        <Button
          v-if="push.supported"
          class="p-button-sm"
          :label="t('settings.enablePush')"
          :loading="push.busy.value"
          text
          style="margin-top: 0.75rem"
          @click="enablePush"
        />
        <p v-else class="muted" style="margin-top: 0.5rem">{{ t('settings.pushUnsupported') }}</p>
      </template>
    </Card>

    <Card>
      <template #title>{{ t('settings.language') }}</template>
      <template #content>
        <SelectButton
          :modelValue="locale"
          :options="localeOptions"
          option-label="label"
          option-value="value"
          @update:model-value="changeLocale"
        />
      </template>
    </Card>

    <Button :label="t('nav.logout')" severity="danger" outlined @click="logout" />
  </div>
</template>
