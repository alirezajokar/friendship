<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import { wishlistApi, type OwnItem } from '@/api/endpoints'
import { useApiError } from '@/composables/useApiError'

const { t } = useI18n()
const err = useApiError()

const items = ref<OwnItem[]>([])
const dialog = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ title: '', description: '', url: '', image_url: '', price: null as number | null })

async function load() {
  items.value = (await wishlistApi.mine()).data
}

function openNew() {
  editingId.value = null
  Object.assign(form, { title: '', description: '', url: '', image_url: '', price: null })
  dialog.value = true
}

function openEdit(it: OwnItem) {
  editingId.value = it.id
  Object.assign(form, {
    title: it.title,
    description: it.description ?? '',
    url: it.url ?? '',
    image_url: it.image_url ?? '',
    price: it.price ? Number(it.price) : null,
  })
  dialog.value = true
}

async function save() {
  if (!form.title.trim()) return
  const body = {
    title: form.title.trim(),
    description: form.description || null,
    url: form.url || null,
    image_url: form.image_url || null,
    price: form.price,
  }
  try {
    if (editingId.value) await wishlistApi.update(editingId.value, body as Partial<OwnItem>)
    else await wishlistApi.create(body as Partial<OwnItem>)
    dialog.value = false
    await load()
  } catch (e) {
    err.show(e)
  }
}

async function remove(id: number) {
  await wishlistApi.remove(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="row-between">
      <h2>{{ t('wishlist.mineTitle') }}</h2>
      <Button icon="pi pi-plus" :label="t('wishlist.add')" size="small" @click="openNew" />
    </div>

    <p v-if="!items.length" class="muted">{{ t('wishlist.empty') }}</p>

    <div class="card-list">
      <Card v-for="it in items" :key="it.id">
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
                <div v-if="it.price" class="muted">{{ Number(it.price).toLocaleString() }}</div>
              </div>
            </div>
            <div class="row">
              <Button icon="pi pi-pencil" text @click="openEdit(it)" />
              <Button icon="pi pi-trash" text severity="danger" @click="remove(it.id)" />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="dialog" modal :header="t('wishlist.add')" style="width: 92vw; max-width: 420px">
      <div class="page" style="padding: 0; gap: 0.75rem">
        <div class="field">
          <label>{{ t('wishlist.itemTitle') }}</label>
          <InputText v-model="form.title" />
        </div>
        <div class="field">
          <label>{{ t('wishlist.itemDesc') }}</label>
          <Textarea v-model="form.description" rows="2" autoResize />
        </div>
        <div class="field">
          <label>{{ t('wishlist.itemUrl') }}</label>
          <InputText v-model="form.url" dir="ltr" />
        </div>
        <div class="field">
          <label>{{ t('wishlist.itemImage') }}</label>
          <InputText v-model="form.image_url" dir="ltr" />
        </div>
        <div class="field">
          <label>{{ t('wishlist.itemPrice') }}</label>
          <InputNumber v-model="form.price" :useGrouping="true" />
        </div>
        <Button :label="t('wishlist.save')" @click="save" />
      </div>
    </Dialog>
  </div>
</template>
