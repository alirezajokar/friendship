<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import Toast from 'primevue/toast'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import BottomNav from '@/components/BottomNav.vue'

const route = useRoute()
const auth = useAuthStore()
const { ready, isAuthenticated, profileComplete } = storeToRefs(auth)
const notifications = useNotificationsStore()

const showNav = computed(
  () => isAuthenticated.value && profileComplete.value && !route.meta.public && route.name !== 'setup',
)
</script>

<template>
  <Toast position="top-center" />
  <template v-if="ready">
    <router-view v-slot="{ Component }">
      <component :is="Component" />
    </router-view>
    <BottomNav v-if="showNav" :unread="notifications.unread" />
  </template>
  <div v-else class="center-screen">
    <i class="pi pi-spin pi-spinner" style="font-size: 2rem" />
  </div>
</template>
