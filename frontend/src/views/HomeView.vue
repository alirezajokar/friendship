<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useAuthStore } from '@/stores/auth'
import { friendApi, inviteApi } from '@/api/endpoints'
import { useNotificationsStore } from '@/stores/notifications'

const { t } = useI18n()
const toast = useToast()
const auth = useAuthStore()
const notifications = useNotificationsStore()

const inviteUrl = ref('')
const pending = ref(0)

async function load() {
  inviteUrl.value = (await inviteApi.mine()).data.url
  pending.value = (await friendApi.requests()).data.length
  await notifications.load()
}

async function regenerate() {
  inviteUrl.value = (await inviteApi.regenerate()).data.url
}

async function copy() {
  await navigator.clipboard.writeText(inviteUrl.value)
  toast.add({ severity: 'success', summary: t('home.copied'), life: 2000 })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <h2>{{ t('home.greeting', { name: auth.me?.display_name }) }}</h2>

    <Card>
      <template #title>{{ t('home.inviteTitle') }}</template>
      <template #content>
        <p class="muted">{{ t('home.inviteHint') }}</p>
        <div class="row" style="margin-top: 0.5rem">
          <InputText :value="inviteUrl" readonly dir="ltr" class="grow" />
          <Button icon="pi pi-copy" :aria-label="t('home.copy')" @click="copy" />
        </div>
        <Button
          class="p-button-text"
          size="small"
          icon="pi pi-refresh"
          :label="t('home.regenerate')"
          text
          style="margin-top: 0.5rem"
          @click="regenerate"
        />
      </template>
    </Card>

    <RouterLink v-if="pending > 0" to="/friends/requests" style="text-decoration: none">
      <Card>
        <template #content>
          <div class="row-between">
            <span>{{ t('home.pendingRequests', { count: pending }) }}</span>
            <i class="pi pi-angle-left" />
          </div>
        </template>
      </Card>
    </RouterLink>
  </div>
</template>
