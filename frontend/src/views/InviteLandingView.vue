<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { inviteApi, type PublicUser } from '@/api/endpoints'
import { useAuthStore } from '@/stores/auth'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const err = useApiError()

const code = route.params.code as string
const inviter = ref<PublicUser | null>(null)
const state = ref<'loading' | 'ready' | 'done' | 'notfound'>('loading')
const resultKey = ref<'sent' | 'alreadyFriends'>('sent')

async function load() {
  try {
    inviter.value = (await inviteApi.preview(code)).data.inviter
    state.value = 'ready'
  } catch {
    state.value = 'notfound'
  }
}

function goLogin() {
  router.push({ name: 'login', query: { redirect: `/i/${code}` } })
}

async function accept() {
  try {
    const res = (await inviteApi.accept(code)).data
    resultKey.value = res.status === 'accepted' ? 'alreadyFriends' : 'sent'
    state.value = 'done'
  } catch (e) {
    err.show(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="center-screen">
    <template v-if="state === 'loading'">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem" />
    </template>

    <template v-else-if="state === 'notfound'">
      <Message severity="warn">{{ t('common.error') }}</Message>
      <Button :label="t('nav.home')" text @click="router.replace('/')" />
    </template>

    <template v-else-if="state === 'done'">
      <Message severity="success">{{ t('invite.' + resultKey) }}</Message>
      <Button :label="t('nav.friends')" @click="router.replace('/friends')" />
    </template>

    <template v-else>
      <h2>{{ t('invite.title') }}</h2>
      <p>{{ t('invite.from', { name: inviter?.display_name }) }}</p>
      <Button v-if="auth.isAuthenticated" :label="t('invite.accept')" @click="accept" />
      <template v-else>
        <p class="muted">{{ t('invite.loginFirst') }}</p>
        <Button :label="t('auth.loginTitle')" @click="goLogin" />
      </template>
    </template>
  </div>
</template>
