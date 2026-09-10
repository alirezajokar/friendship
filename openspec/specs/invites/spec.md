# invites

## Purpose

One reusable invite link per user.

## Requirements

### Requirement: Reusable invite code

The system SHALL give every user exactly one invite code, creating it on first
request, and SHALL let the user replace it.

#### Scenario: Fetch my invite

- **WHEN** a user GETs `/invites/me`
- **THEN** the response contains the code and a full URL `<PUBLIC_BASE_URL>/i/<code>`

#### Scenario: Regenerate

- **WHEN** a user POSTs `/invites/regenerate`
- **THEN** a new code replaces the old one and the old code stops resolving

### Requirement: Public invite preview

The system SHALL expose the inviter's public profile for a valid code without
authentication.

#### Scenario: Valid code

- **WHEN** anyone GETs `/i/<code>` for an active user's code
- **THEN** the response is `200` with `{ inviter: { id, display_name, avatar_url } }`

#### Scenario: Unknown code

- **WHEN** the code does not exist
- **THEN** the response is `404` (`invite_not_found`)

### Requirement: Accepting an invite

The system SHALL, when an authenticated user accepts a code, create a friend
request from that user to the inviter.

#### Scenario: New connection

- **WHEN** an authenticated user POSTs `/invites/<code>/accept` and is not already
  connected to the inviter
- **THEN** a `pending` friendship is created and the inviter receives a
  `friend_request` notification

#### Scenario: Own code

- **WHEN** a user accepts their own invite code
- **THEN** the response is `422` (`cannot_invite_self`)
