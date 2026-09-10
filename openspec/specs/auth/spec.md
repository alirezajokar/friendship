# auth

## Purpose

Phone-number one-time-code authentication and session management.

## Requirements

### Requirement: OTP request

The system SHALL let a client request a one-time code for a phone number,
normalizing the number to E.164 (default region IR) before use.

#### Scenario: Code is sent

- **WHEN** a client POSTs a valid phone number to `/auth/otp/request`
- **THEN** a 6-digit code is generated, stored only as an HMAC-SHA256 hash with a
  120-second expiry, and handed to the configured SMS provider
- **AND** the response is `200` with `resend_cooldown_seconds`

#### Scenario: Resend cooldown

- **WHEN** a second request for the same phone arrives within the cooldown window
- **THEN** the response is `429` with detail `otp_cooldown:<seconds>` and no new code is sent

#### Scenario: Hourly and per-IP limits

- **WHEN** more than 5 requests for one phone occur within an hour, or more than
  30 from one IP
- **THEN** the response is `429` with detail `otp_rate_limited`

### Requirement: OTP verification

The system SHALL verify a submitted code in constant time, enforce an attempt
cap, and consume the code on success.

#### Scenario: Correct code

- **WHEN** a client POSTs the matching code to `/auth/otp/verify` before expiry
- **THEN** the code is marked consumed, the user is created if new, session
  cookies are set, and the body reports `is_new` and `profile_completed`

#### Scenario: Wrong code

- **WHEN** the submitted code does not match
- **THEN** the attempt counter increments and the response is `400` (`otp_invalid`)

#### Scenario: Attempts exhausted

- **WHEN** a 6th verification attempt is made against the same code
- **THEN** the response is `429` (`otp_too_many_attempts`)

#### Scenario: Code is single-use

- **WHEN** an already-consumed code is submitted again
- **THEN** the response is `400` (`otp_invalid_or_expired`)

### Requirement: Rotating refresh sessions

The system SHALL issue a short-lived access JWT and an opaque refresh token
stored as a hash, and SHALL rotate the refresh token on every use.

#### Scenario: Refresh succeeds

- **WHEN** `/auth/refresh` is called with a valid, unrotated refresh cookie
- **THEN** the old token is marked rotated, a new refresh + access + csrf cookie
  trio is issued, and the absolute expiry cap is preserved

#### Scenario: Refresh-token reuse

- **WHEN** a refresh token that was already rotated is presented again
- **THEN** every token in that session family is revoked and the response is `401`

#### Scenario: Logout

- **WHEN** `/auth/logout` is called
- **THEN** the session family is revoked and all auth cookies are cleared

### Requirement: CSRF protection

The system SHALL reject state-changing requests whose `X-CSRF-Token` header does
not match the `csrf_token` cookie.

#### Scenario: Missing or wrong token

- **WHEN** a `POST`/`PATCH`/`PUT`/`DELETE` arrives without a matching CSRF token
- **THEN** the response is `403` (`csrf_failed`)

### Requirement: Security headers and CORS

The system SHALL send `X-Content-Type-Options`, `X-Frame-Options: DENY`,
`Referrer-Policy`, and a minimal CSP on every response, add HSTS in production,
and restrict CORS to the configured frontend origin with credentials allowed.

#### Scenario: Response headers

- **WHEN** any endpoint responds
- **THEN** the response carries `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy`, and a `Content-Security-Policy`
- **AND** `Strict-Transport-Security` is present when `ENV=prod`

#### Scenario: Cross-origin request

- **WHEN** a browser on an origin other than `FRONTEND_ORIGIN` calls the API
- **THEN** CORS does not grant credentialed access
