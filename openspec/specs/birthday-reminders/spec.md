# birthday-reminders

## Purpose

Multi-window birthday reminders to a user's friends, computed in the Jalali calendar.

## Requirements

### Requirement: Jalali anniversary resolution

The system SHALL compute each year's birthday occurrence from the stored Jalali
month/day in the given Jalali year, not by reusing a Gregorian month/day.

#### Scenario: Leap-year shift

- **WHEN** resolving "11 Tir" for Jalali year 1403 (a leap year)
- **THEN** the Gregorian occurrence is 2024-07-01, not 2024-07-02

#### Scenario: 30 Esfand in a common year

- **WHEN** a user was born on 30 Esfand and the target Jalali year is not a leap year
- **THEN** the occurrence resolves to 29 Esfand of that year

### Requirement: Reminder windows

The system SHALL evaluate the configured offsets (default 7, 3, 1, 0 days before,
at local wall-clock times 09:00/09:00/21:00/09:00) in the birthday user's
timezone, applying offsets as whole calendar days.

#### Scenario: Day-of window becomes due

- **WHEN** the hourly scan runs at or after 09:00 local time on the occurrence date
- **THEN** the `d0` window is due for that user's friends

#### Scenario: Window not yet reached

- **WHEN** the scan runs before the window's local time on the trigger day
- **THEN** that window is not due

#### Scenario: Window straddles Nowruz

- **WHEN** a birthday falls just after Nowruz so a -7d window lands in the
  previous Jalali year
- **THEN** the window is still detected (both the current and next Jalali year are checked)

### Requirement: Idempotent delivery

The system SHALL send each (recipient, birthday user, occurrence Jalali year,
offset) reminder at most once.

#### Scenario: Re-running the scan

- **WHEN** the scan runs twice for the same due window
- **THEN** the first run dispatches a `birthday` notification to each friend and
  the second run dispatches nothing

### Requirement: Manual trigger

The system SHALL support `python -m app.worker --run-now [--base-now <iso>]` to
run a single scan for testing and demos.

#### Scenario: One-off scan

- **WHEN** `python -m app.worker --run-now` is run
- **THEN** exactly one scan executes against the current time and the process exits

#### Scenario: Scan at an injected time

- **WHEN** `--base-now <iso>` is supplied
- **THEN** the scan treats that timestamp as "now"
