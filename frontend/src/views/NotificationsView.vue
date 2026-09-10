<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from 'primevue/card'
import Button from 'primevue/button'
import { useNotificationsStore } from '@/stores/notifications'
import type { AppNotification } from '@/api/endpoints'

const { t } = useI18n()
const store = useNotificationsStore()

function line(n: AppNotification): string {
  const p = n.payload as Record<string, string>
  if (n.type === 'friend_request') return `${p.name ?? ''} — ${t('notifications.types.friend_request')}`
  if (n.type === 'friend_accepted') return `${p.name ?? ''} — ${t('notifications.types.friend_accepted')}`
  if (n.type === 'birthday') return `${p.days_text ?? ''} ${t('friends.birthday', { date: p.name })}`
  return n.type
}

onMounted(store.load)
</script>

<template>
  <div class="page">
    <h2>{{ t('notifications.title') }}</h2>
    <p v-if="!store.items.length" class="muted">{{ t('notifications.empty') }}</p>

    <div class="card-list">
      <Card v-for="n in store.items" :key="n.id" :class="{ claimed: !!n.read_at }">
        <template #content>
          <div class="row-between">
            <span>{{ line(n) }}</span>
            <Button
              v-if="!n.read_at"
              icon="pi pi-check"
              text
              size="small"
              :aria-label="t('notifications.markRead')"
              @click="store.markRead(n.id)"
            />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>
