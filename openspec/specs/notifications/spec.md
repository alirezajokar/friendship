# notifications

## Purpose

In-app notifications plus Web Push and email fan-out.

## Requirements

### Requirement: Notification fan-out

The system SHALL, for every dispatched notification, write an in-app row and then
deliver it over each channel the recipient has enabled.

#### Scenario: Dispatch

- **WHEN** a notification is dispatched for a recipient
- **THEN** a `notifications` row is created, a Web Push message is sent to each of
  the recipient's subscriptions if `web_push` is enabled, and an email is sent if
  `email` is enabled and the recipient has an email address

#### Scenario: Dead push subscription

- **WHEN** a Web Push send returns 404 or 410
- **THEN** that subscription row is deleted

### Requirement: Reading notifications

The system SHALL list a user's most recent notifications and let them mark one read.

#### Scenario: Mark read

- **WHEN** a user POSTs `/notifications/<id>/read` for their own notification
- **THEN** `read_at` is set

### Requirement: Channel preferences

The system SHALL default both `web_push` and `email` to enabled for a new user
and let the user toggle each.

#### Scenario: Update prefs

- **WHEN** a user PUTs `/notifications/prefs` with `{ web_push, email }`
- **THEN** the values are persisted and returned

### Requirement: Push subscriptions

The system SHALL store one Web Push subscription per endpoint, re-binding an
existing endpoint to the current user on re-subscribe.

#### Scenario: Subscribe

- **WHEN** a user POSTs `/push/subscribe` with `{ endpoint, keys }`
- **THEN** the subscription is stored (or updated) for that user
