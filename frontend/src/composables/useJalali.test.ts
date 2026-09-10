import { describe, expect, it } from 'vitest'
import { jalaliToISO, isoToJalali, jMonthLength, formatJalali } from './useJalali'

describe('jalali helpers', () => {
  it('converts a known Jalali date to ISO', () => {
    expect(jalaliToISO(1376, 4, 11)).toBe('1997-07-02')
  })

  it('reflects the Jalali-leap-year anniversary shift', () => {
    // 1403 is a Jalali leap year -> "11 Tir" is 1 July that Gregorian year.
    expect(jalaliToISO(1403, 4, 11)).toBe('2024-07-01')
    expect(jalaliToISO(1404, 4, 11)).toBe('2025-07-02')
  })

  it('applies the 30-Esfand fallback in a common year', () => {
    expect(jMonthLength(1404, 12)).toBe(29)
    expect(jalaliToISO(1404, 12, 30)).toBe(jalaliToISO(1404, 12, 29))
  })

  it('round-trips iso <-> jalali', () => {
    const j = isoToJalali('2024-07-01')
    expect(j).toEqual({ jy: 1403, jm: 4, jd: 11 })
  })

  it('formats with and without a year', () => {
    expect(formatJalali(1376, 4, 11)).toBe('11 تیر 1376')
    expect(formatJalali(null, 4, 11)).toBe('11 تیر')
  })
})
