import { createI18n } from 'vue-i18n'
import fa from './fa.json'
import en from './en.json'

export type LocaleCode = 'fa' | 'en'
const STORAGE_KEY = 'locale'

export function currentLocale(): LocaleCode {
  const saved = localStorage.getItem(STORAGE_KEY)
  return saved === 'en' ? 'en' : 'fa'
}

export const i18n = createI18n({
  legacy: false,
  locale: currentLocale(),
  fallbackLocale: 'fa',
  messages: { fa, en },
})

export function setLocale(code: LocaleCode) {
  i18n.global.locale.value = code
  localStorage.setItem(STORAGE_KEY, code)
  const html = document.documentElement
  html.lang = code
  html.dir = code === 'fa' ? 'rtl' : 'ltr'
}

setLocale(currentLocale())
