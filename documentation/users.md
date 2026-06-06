# User Administration Rules

## Key Points

- Every endpoint registered by `UserController` must require the `ADMIN`
  profile.
- No `UserController` endpoint may be public or accessible with only the `USER`
  profile.
- `/api/routes` must report every `UserController` endpoint with
  `required_profiles: ["ADMIN"]`.
- User administration responses must never expose passwords, password hashes,
  email verification tokens or collection file internals.

## Purpose

This document defines the rules to preserve when changing backend user
administration, user status, search, deletion or lock behavior.

## User Roles

The application supports these user profiles:

- `USER`: standard application profile for registered users. A `USER` can manage
  their own collection workflow after email verification and administrator
  validation. This role is intended for personal collection usage and must not
  grant access to user administration features.
- `ADMIN`: administration profile for the configured technical account. An
  `ADMIN` can supervise registered accounts, validate waiting users, lock or
  unlock accounts, delete users and access the Configuration page. This
  role is intended for application governance, not for owning a personal
  frontend collection.

Role rights must be described by functional intent, while exact route
protection remains enforced by backend decorators and exposed through
`/api/routes`.

## Backend Routes

All user administration routes are protected backend routes and must require the
`ADMIN` profile:

- `GET /api/users`: searches users.
- `DELETE /api/users/<id>`: deletes one user.
- `POST /api/users/<id>/lock`: changes one user status to `LOCKED`.
- `POST /api/users/<id>/unlock`: changes one user status to `ACTIVE`.
- `POST /api/users/<id>/validate`: changes one waiting user status to `ACTIVE`
  and sends the account activation email.

These routes must never be public and must appear in `/api/routes` with
`requires_auth: true`, `auth_schemes: ["Bearer"]` and
`required_profiles: ["ADMIN"]`.

## Search Contract

`GET /api/users` accepts optional query parameters:

- `name`: case-insensitive match against the user login name. Until a dedicated
  display-name column exists, the login name is the `email` column.
- `creation_date_from`: ISO datetime lower bound on `creation_date`.
- `creation_date_to`: ISO datetime upper bound on `creation_date`.
- `last_connexion_date_from`: ISO datetime lower bound on
  `last_connexion_date`.
- `last_connexion_date_to`: ISO datetime upper bound on
  `last_connexion_date`.
- `status`: exact user status, currently `ACTIVE`, `WAITING_VALIDATION` or
  `LOCKED`.

The response must not expose passwords, password hashes, email verification token
hashes, raw verification tokens, collection file paths or collection file
descriptions.

## Frontend Rules

The Configuration page may show a `Gerer les utilisateurs` section only when
the local token profile is `ADMIN`. Users with the `USER` profile must not see
this section.

The frontend `/users` page lists the properties returned by `GET /api/users` in a
table. The page must not add or display password fields. If the backend route
catalog does not confirm access to `GET /api/users`, the page must not call the
endpoint.

The `/users` page must provide filters for:

- email text with `contains` and exact modes;
- last sign-in date for current year, current month or current week;
- creation date for current year, current month or current week;
- user status with French labels mapped to backend status values.

The `/users` page must expose a validation action for users whose status is
`WAITING_VALIDATION` when backend route discovery confirms access to
`POST /api/users/<id>/validate`.

When `/users` receives `status=WAITING_VALIDATION` in the query string, the page
must display all users waiting for administrator validation so the administrator
can process the pending accounts from the notification email link.

The administrator notification email sent after a public registration must name
the newly created waiting user and include the total number of users currently
waiting for validation.

## Status Rules

Supported user statuses are:

- `ACTIVE`: account status allowed to sign in after email verification.
- `WAITING_VALIDATION`: default status for registered users after account
  creation, pending administrator approval.
- `LOCKED`: blocked status that prevents token issuance.

When a user is `WAITING_VALIDATION`, `POST /auth/token` must reject the account
with `401` and a clear message explaining that administrator validation is still
required.

When a user is `LOCKED`, `POST /auth/token` must reject the account with the
same generic `401` behavior used for invalid credentials. The response must not
reveal whether a user exists or is locked.

`POST /api/users/<id>/lock` is idempotent for an existing user: calling it for an
already locked user returns the user with `status: "LOCKED"`.

`POST /api/users/<id>/unlock` is idempotent for an existing user: calling it for
an already active user returns the user with `status: "ACTIVE"`.

`POST /api/users/<id>/validate` is idempotent for an existing user: calling it
for an already active user returns the user with `status: "ACTIVE"`.

## Deletion Rules

`DELETE /api/users/<id>` deletes the user from `t_user`. The implementation must
also remove dependent `t_user_collection` rows first unless the database schema
is changed to enforce an equivalent cascade.

Deleting an unknown user returns `404`.

## Database Rules

The `t_user.status` column is mandatory and constrained to `ACTIVE`,
`WAITING_VALIDATION` or `LOCKED`.
Every schema change around user status must update `documentation/database.md`
and include an Alembic migration.

## Tests

When modifying user administration, update backend tests for:

- `GET /api/users` requiring authentication and `ADMIN`;
- successful user search with name, creation date, last connexion date and
  status filters;
- invalid search date or status rejection;
- `DELETE /api/users/<id>` success and unknown-user `404`;
- `POST /api/users/<id>/lock` success and unknown-user `404`;
- `POST /api/users/<id>/unlock` success and unknown-user `404`;
- `POST /api/users/<id>/validate` success, activation email and unknown-user
  `404`;
- waiting users being rejected by `POST /auth/token` with a clear message;
- locked users being rejected by `POST /auth/token`;
- `/api/routes` metadata for user routes.

Run `./test_backend.sh` after changes.
