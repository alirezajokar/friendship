<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { friendApi, type PublicUser } from '@/api/endpoints'

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()

const friends = ref<PublicUser[]>([])
const requestCount = ref(0)

async function load() {
  friends.value = (await friendApi.list()).data
  requestCount.value = (await friendApi.requests()).data.length
}

function initials(name: string | null) {
  return (name ?? '?').trim().charAt(0).toUpperCase()
}

function unfriend(f: PublicUser) {
  confirm.require({
    message: t('friends.unfriend') + ' — ' + (f.display_name ?? ''),
    accept: async () => {
      await friendApi.unfriend(f.id)
      await load()
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <ConfirmDialog />
    <div class="row-between">
      <h2>{{ t('friends.title') }}</h2>
      <Button
        :label="t('friends.requests')"
        :badge="requestCount ? String(requestCount) : undefined"
        size="small"
        outlined
        @click="router.push('/friends/requests')"
      />
    </div>

    <p v-if="!friends.length" class="muted">{{ t('friends.empty') }}</p>

    <div class="card-list">
      <Card v-for="f in friends" :key="f.id">
        <template #content>
          <div class="row-between">
            <div class="row">
              <Avatar
                :label="!f.avatar_url ? initials(f.display_name) : undefined"
                :image="f.avatar_url ?? undefined"
                shape="circle"
              />
              <span>{{ f.display_name }}</span>
            </div>
            <div class="row">
              <Button
                icon="pi pi-gift"
                text
                :aria-label="t('friends.viewWishlist')"
                @click="router.push(`/wishlist/${f.id}`)"
              />
              <Button
                icon="pi pi-user-minus"
                text
                severity="danger"
                :aria-label="t('friends.unfriend')"
                @click="unfriend(f)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>
