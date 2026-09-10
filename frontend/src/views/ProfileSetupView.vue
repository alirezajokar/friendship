<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { useAuthStore } from '@/stores/auth'
import { useApiError } from '@/composables/useApiError'
import { J_MONTHS, jMonthLength, todayJalali } from '@/composables/useJalali'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const err = useApiError()

const name = ref(auth.me?.display_name ?? '')
const email = ref(auth.me?.email ?? '')
const jy = ref<number | null>(auth.me?.birth_jyear ?? null)
const jm = ref<number>(auth.me?.birth_jmonth ?? 1)
const jd = ref<number>(auth.me?.birth_jday ?? 1)
const loading = ref(false)

const thisJy = todayJalali().jy
const years = Array.from({ length: 90 }, (_, i) => thisJy - 5 - i)
const months = J_MONTHS.map((label, i) => ({ label, value: i + 1 }))
const days = () => Array.from({ length: jMonthLength(jy.value ?? 1403, jm.value) }, (_, i) => i + 1)

async function save() {
  if (!name.value.trim()) return
  loading.value = true
  try {
    await auth.updateProfile({
      display_name: name.value.trim(),
      email: email.value.trim() || null,
      birthday: { jyear: jy.value, jmonth: jm.value, jday: Math.min(jd.value, jMonthLength(jy.value ?? 1403, jm.value)) },
    })
    // birth_gregorian is derived server-side from these Jalali parts.
    router.replace((route.query.redirect as string) || '/')
  } catch (e) {
    err.show(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <h2>{{ t('profile.title') }}</h2>

    <div class="field">
      <label for="name">{{ t('profile.displayName') }}</label>
      <InputText id="name" v-model="name" />
    </div>

    <div class="field">
      <label for="email">{{ t('profile.email') }}</label>
      <InputText id="email" v-model="email" inputmode="email" dir="ltr" />
    </div>

    <div class="field">
      <label>{{ t('profile.birthday') }}</label>
      <div class="row">
        <Select
          v-model="jd"
          :options="days()"
          :placeholder="t('profile.day')"
          class="grow"
        />
        <Select
          v-model="jm"
          :options="months"
          option-label="label"
          option-value="value"
          :placeholder="t('profile.month')"
          class="grow"
        />
        <Select
          v-model="jy"
          :options="years"
          :placeholder="t('profile.birthYear')"
          show-clear
          class="grow"
        />
      </div>
    </div>

    <Button :label="t('profile.save')" :loading="loading" @click="save" />
  </div>
</template>
