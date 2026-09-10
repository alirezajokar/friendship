<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ unread: number }>()
const { t } = useI18n()

const links = [
  { to: '/', icon: 'pi-home', key: 'home' },
  { to: '/friends', icon: 'pi-users', key: 'friends' },
  { to: '/wishlist', icon: 'pi-gift', key: 'wishlist' },
  { to: '/notifications', icon: 'pi-bell', key: 'notifications', badge: true },
  { to: '/settings', icon: 'pi-cog', key: 'settings' },
]
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink
      v-for="l in links"
      :key="l.to"
      :to="l.to"
      class="nav-item"
      active-class="active"
      :aria-label="t('nav.' + l.key)"
    >
      <span class="icon-wrap">
        <i class="pi" :class="l.icon" />
        <span v-if="l.badge && unread > 0" class="dot">{{ unread }}</span>
      </span>
      <span class="label">{{ t('nav.' + l.key) }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  inset-inline: 0;
  bottom: 0;
  margin: 0 auto;
  max-width: var(--page-max);
  display: flex;
  justify-content: space-around;
  background: var(--p-content-background, #fff);
  border-top: 1px solid var(--p-content-border-color, #e4e4e7);
  padding: 0.4rem 0 calc(0.4rem + env(safe-area-inset-bottom));
  z-index: 50;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-decoration: none;
  color: var(--p-text-muted-color, #71717a);
  font-size: 0.7rem;
  padding: 0.25rem 0.6rem;
}
.nav-item.active { color: var(--p-primary-color, #6366f1); }
.icon-wrap { position: relative; }
.icon-wrap .pi { font-size: 1.2rem; }
.dot {
  position: absolute;
  top: -6px;
  inset-inline-end: -10px;
  background: var(--p-red-500, #ef4444);
  color: #fff;
  border-radius: 999px;
  font-size: 0.6rem;
  min-width: 15px;
  height: 15px;
  display: grid;
  place-items: center;
  padding: 0 3px;
}
</style>
