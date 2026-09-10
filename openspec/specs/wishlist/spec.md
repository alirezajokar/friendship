# wishlist

## Purpose

Gift wishlist items and friend claims, with surprise-preserving visibility.

## Requirements

### Requirement: Item ownership

The system SHALL let a user create, edit, reorder, and delete their own wishlist
items, and SHALL reject operations on items owned by someone else with `404`.

#### Scenario: Delete cascades claims

- **WHEN** an owner deletes an item that a friend had claimed
- **THEN** the item and its claim row are both removed

### Requirement: Owner view hides claims

The system SHALL return the owner's own items with no claim information of any
kind.

#### Scenario: Owner lists their wishlist

- **WHEN** a user GETs `/wishlists/me`
- **THEN** each item has no `is_claimed`, `claimed_by_me`, or claimer identity field

### Requirement: Friend view shows reservation only

The system SHALL return a friend's items only to an accepted friend, annotating
each with `is_claimed` and `claimed_by_me` but never the identity of another
person's claim.

#### Scenario: A friend claims one item

- **WHEN** friend A claims item #3 on the owner's list
- **THEN** friend B, viewing the same list, sees item #3 as `is_claimed: true`,
  `claimed_by_me: false`, every other item unclaimed, and no field naming A

#### Scenario: Non-friend is blocked

- **WHEN** a user who is not an accepted friend GETs `/wishlists/<owner_id>`
- **THEN** the response is `403` (`not_friends`)

### Requirement: Claiming

The system SHALL allow at most one claim per item, only by an accepted friend
who is not the owner, and SHALL allow only the claimer to release it.

#### Scenario: Owner cannot claim

- **WHEN** the owner tries to claim their own item
- **THEN** the response is `403` (`cannot_claim_own`)

#### Scenario: Double claim races

- **WHEN** two friends claim the same free item concurrently
- **THEN** exactly one succeeds and the other gets `409` (`already_claimed`)

#### Scenario: Release by non-claimer

- **WHEN** a friend other than the claimer deletes the claim
- **THEN** the response is `403` (`not_your_claim`)
