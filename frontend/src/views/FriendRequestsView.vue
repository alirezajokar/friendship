<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { friendApi, type FriendRequest } from '@/api/endpoints'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const err = useApiError()
const requests = ref<FriendRequest[]>([])

async function load() {
  requests.value = (await friendApi.requests()).data
}

async function respond(r: FriendRequest, accept: boolean) {
  try {
    await friendApi.respond(r.id, accept)
    requests.value = requests.value.filter((x) => x.id !== r.id)
  } catch (e) {
    err.show(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <h2>{{ t('friends.requests') }}</h2>
    <p v-if="!requests.length" class="muted">{{ t('friends.noRequests') }}</p>

    <div class="card-list">
      <Card v-for="r in requests" :key="r.id">
        <template #content>
          <div class="row-between">
            <div class="row">
              <Avatar
                :label="(r.requester.display_name ?? '?').charAt(0)"
                :image="r.requester.avatar_url ?? undefined"
                shape="circle"
              />
              <span>{{ r.requester.display_name }}</span>
            </div>
            <div class="row">
              <Button :label="t('friends.accept')" size="small" @click="respond(r, true)" />
              <Button
                :label="t('friends.decline')"
                size="small"
                severity="secondary"
                outlined
                @click="respond(r, false)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>
