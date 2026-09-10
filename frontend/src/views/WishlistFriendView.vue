<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { friendApi, wishlistApi, type FriendItem } from '@/api/endpoints'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const route = useRoute()
const err = useApiError()

const userId = Number(route.params.userId)
const ownerName = ref('')
const items = ref<FriendItem[]>([])

async function load() {
  items.value = (await wishlistApi.ofFriend(userId)).data
  const friends = (await friendApi.list()).data
  ownerName.value = friends.find((f) => f.id === userId)?.display_name ?? ''
}

async function toggleClaim(it: FriendItem) {
  try {
    if (it.claimed_by_me) await wishlistApi.unclaim(it.id)
    else await wishlistApi.claim(it.id)
    await load()
  } catch (e) {
    err.show(e)
    await load()
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <h2>{{ t('wishlist.friendTitle', { name: ownerName }) }}</h2>
    <p v-if="!items.length" class="muted">{{ t('wishlist.empty') }}</p>

    <div class="card-list">
      <Card v-for="it in items" :key="it.id" :class="{ claimed: it.is_claimed && !it.claimed_by_me }">
        <template #content>
          <div class="row-between">
            <div class="row">
              <img
                v-if="it.image_url"
                :src="it.image_url"
                alt=""
                style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px"
              />
              <div>
                <div>{{ it.title }}</div>
                <a v-if="it.url" :href="it.url" target="_blank" rel="noopener" class="muted" dir="ltr">
                  {{ it.url }}
                </a>
              </div>
            </div>

            <div class="row">
              <Tag
                v-if="it.claimed_by_me"
                :value="t('wishlist.claimedByMe')"
                severity="success"
              />
              <Tag
                v-else-if="it.is_claimed"
                :value="t('wishlist.claimed')"
                severity="secondary"
              />
              <Button
                v-if="!it.is_claimed || it.claimed_by_me"
                size="small"
                :label="it.claimed_by_me ? t('wishlist.unclaim') : t('wishlist.claim')"
                :severity="it.claimed_by_me ? 'secondary' : 'primary'"
                :outlined="it.claimed_by_me"
                @click="toggleClaim(it)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>
