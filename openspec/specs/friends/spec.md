# friends

## Purpose

Friend requests and the symmetric friendship they become once accepted.

## Requirements

### Requirement: Sending a request

The system SHALL create a directed `pending` friendship and SHALL collapse
duplicate or reciprocal requests instead of stacking them.

#### Scenario: Reciprocal request auto-accepts

- **WHEN** user A has a pending request to B and B sends a request to A
- **THEN** the existing edge becomes `accepted` rather than creating a second row

#### Scenario: Cannot friend yourself

- **WHEN** a user targets their own id
- **THEN** the response is `422` (`cannot_friend_self`)

### Requirement: Responding to a request

The system SHALL let only the addressee accept or decline a pending request.

#### Scenario: Accept

- **WHEN** the addressee POSTs `/friends/requests/<id>/respond` with `accept: true`
- **THEN** the edge becomes `accepted` and the requester receives a
  `friend_accepted` notification

#### Scenario: Not the addressee

- **WHEN** someone other than the addressee responds
- **THEN** the response is `404` (`request_not_found`)

### Requirement: Listing and removing

The system SHALL list a user's accepted friends and incoming pending requests,
and SHALL let a user remove an accepted friendship.

#### Scenario: Unfriend

- **WHEN** a user DELETEs `/friends/<other_id>` for an accepted friend
- **THEN** the friendship row is deleted for both sides
