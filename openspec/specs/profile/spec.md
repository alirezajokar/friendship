# profile

## Purpose

User profile, including the Jalali birthday model.

## Requirements

### Requirement: Profile completion

The system SHALL treat a user as "profile complete" once a display name is set,
and SHALL let the user update display name, email, avatar URL, and timezone.

#### Scenario: Update profile

- **WHEN** a user PATCHes `/users/me` with a non-empty `display_name`
- **THEN** the fields are saved and the response reflects `profile_completed: true`

### Requirement: Jalali birthday storage

The system SHALL store a birthday as its Jalali components — `birth_jyear`
(optional), `birth_jmonth`, `birth_jday` — as the source of truth, and SHALL
derive `birth_gregorian` for display only.

#### Scenario: Birthday with year

- **WHEN** a user submits `{ jyear, jmonth, jday }`
- **THEN** the components are stored and `birth_gregorian` is computed via
  `persiantools` (applying the 30-Esfand→29-Esfand fallback)

#### Scenario: Birthday without year

- **WHEN** a user submits `jmonth` and `jday` with `jyear` null
- **THEN** the components are stored and `birth_gregorian` stays null

#### Scenario: Invalid components

- **WHEN** the month is out of 1–12, the day exceeds that Jalali month's length,
  or the year is outside 1200–1500
- **THEN** the response is `422` (`birthday_invalid`)
