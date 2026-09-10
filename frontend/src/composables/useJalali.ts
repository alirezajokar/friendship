import jalaali from 'jalaali-js'

export const J_MONTHS = [
  'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
]

export function jMonthLength(jy: number, jm: number): number {
  if (jm <= 6) return 31
  if (jm <= 11) return 30
  return jalaali.isLeapJalaaliYear(jy) ? 30 : 29
}

/** Jalali (jy optional) -> ISO Gregorian date string, applying the 30-Esfand fallback. */
export function jalaliToISO(jy: number, jm: number, jd: number): string {
  const day = Math.min(jd, jMonthLength(jy, jm))
  const g = jalaali.toGregorian(jy, jm, day)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${g.gy}-${pad(g.gm)}-${pad(g.gd)}`
}

export function isoToJalali(iso: string): { jy: number; jm: number; jd: number } {
  const [y, m, d] = iso.split('-').map(Number)
  const j = jalaali.toJalaali(y, m, d)
  return { jy: j.jy, jm: j.jm, jd: j.jd }
}

export function formatJalali(jy: number | null, jm: number, jd: number): string {
  const base = `${jd} ${J_MONTHS[jm - 1]}`
  return jy ? `${base} ${jy}` : base
}

export function todayJalali(): { jy: number; jm: number; jd: number } {
  const now = new Date()
  const j = jalaali.toJalaali(now.getFullYear(), now.getMonth() + 1, now.getDate())
  return { jy: j.jy, jm: j.jm, jd: j.jd }
}
