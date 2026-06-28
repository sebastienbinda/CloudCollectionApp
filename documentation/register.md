# User Registration Rules

## Purpose

This document defines the rules to preserve when changing user registration or
email verification.

## Public Routes

- `POST /api/auth/register` must remain public: the user does not have an
  account yet and cannot have a Bearer token.
- `GET /api/auth/pseudonym-availability` must remain public so the registration
  form can validate a pseudonym when its field loses focus.
- `GET /api/auth/verify-email` and `POST /api/auth/verify-email` must remain
  public: the user validates the account from an email link before signing in.
- `GET /api/auth/verify-email` is used by browser email links and returns an
  HTTP redirect to the public frontend page `/auth/verify-email`.
- `POST /api/auth/verify-email` is used by API clients and returns JSON.
- Keep these endpoints in `AuthGuard.protect_all_routes(..., exempt_endpoints=...)`.
- Keep `RouteDiscoveryService` reporting these endpoints with
  `requires_auth: false`, `access: "public"` and `auth_schemes: []`.

## Security Rules

- Never expose collection data from these public routes.
- Never return password hashes, raw passwords, email verification token hashes or
  raw verification tokens in API responses.
- Store only non-reversible password hashes.
- Store only the email verification token hash in database.
- Registered users must receive the `USER` profile by default.
- Registered users must receive the `WAITING_VALIDATION` status by default
  when `ADMIN_ACCOUNT_VALIDATION_ENABLED` is active.
- When `ADMIN_ACCOUNT_VALIDATION_ENABLED=false`, registered users receive
  `ACTIVE` immediately but still cannot sign in until email verification
  succeeds.
- Email verification confirms ownership of the address only; it must not change
  a `WAITING_VALIDATION` account to `ACTIVE`.
- The verification email must explain whether administrator validation is
  required after email verification.
- After a user validates their email, the backend must send an administrator
  notification email when `ADMIN_NOTIFICATION_EMAIL` is configured, even when
  administrator validation is disabled. This email must include the user's
  email, the total number of users waiting for administrator validation and a
  direct link to
  `/users?status=WAITING_VALIDATION`.
- Treat duplicate email, invalid password and invalid verification token as
  controlled business errors.
- Registration requires a pseudonym from 3 to 32 characters containing only
  letters, digits, `_` or `-`. It is trimmed, preserved for display and unique
  case-insensitively. Duplicate pseudonyms return `409` during registration.
- The availability route validates the same format and returns `available`.
  This early check is advisory: the database unique index and registration
  transaction remain authoritative against concurrent registrations.
- The frontend disables account creation until the current pseudonym has been
  checked after blur and confirmed available. It explains that the pseudonym is
  the connected-user display name and will identify future shared collections.
- Do not hardcode SMTP secrets, passwords, tokens or signing keys.

## Local Email Testing

The local Docker stack uses Mailpit to test registration and email verification
without a real SMTP account or production domain.

- `docker-compose.local.yml` starts a `mailpit` service.
- The backend sends local verification emails through `LOCAL_SMTP_HOST=mailpit`
  and `LOCAL_SMTP_PORT=1025`.
- `LOCAL_SMTP_USE_TLS` must remain `false` with Mailpit.
- The Mailpit web interface is exposed on `http://localhost:8025` by default.
- `BACKEND_PUBLIC_URL` must point to the local web entrypoint, for example
  `http://localhost:8080`, so verification links opened from Mailpit target the
  local application.
- `FRONTEND_PUBLIC_URL` must point to the public frontend origin used in
  administrator notification links.
- `ADMIN_ACCOUNT_VALIDATION_ENABLED` controls whether email-verified accounts
  must wait for administrator validation before sign-in. It defaults to `true`.
- `ADMIN_NOTIFICATION_EMAIL` configures the administrator recipient for new user
  email validation notifications.
- The production SMTP variables (`SMTP_HOST`, `SMTP_FROM_EMAIL`,
  `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`) remain reserved for the
  online Docker stack and must not be required to test registration locally.
- Mailpit is a development-only mailbox and must not be added to the online
  Docker stack.

## Tests

When modifying registration or email verification, update backend tests for:

- public registration without Bearer token;
- duplicate email rejection;
- invalid and duplicate pseudonym rejection;
- public pseudonym availability checks without a Bearer token;
- password policy rejection;
- public email verification without Bearer token;
- browser email verification redirect from `GET /api/auth/verify-email`;
- JSON email verification from `POST /api/auth/verify-email`;
- missing or invalid verification token rejection;
- created users receiving `WAITING_VALIDATION` when administrator validation is
  active;
- created users receiving `ACTIVE` when administrator validation is disabled;
- administrator notification email after user email verification when
  `ADMIN_NOTIFICATION_EMAIL` is configured;
- `/api/routes` public indicators for registration and verification routes.

Run `./scripts/test_backend.sh` after changes.
