# User Registration Rules

## Purpose

This document defines the rules to preserve when changing user registration or
email verification.

## Public Routes

- `POST /api/auth/register` must remain public: the user does not have an
  account yet and cannot have a Bearer token.
- `GET /api/auth/verify-email` and `POST /api/auth/verify-email` must remain
  public: the user validates the account from an email link before signing in.
- `GET /api/auth/verify-email` is used by browser email links and returns an
  HTML confirmation page.
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
- Registered users must receive the `ACTIVE` status by default.
- Treat duplicate email, invalid password and invalid verification token as
  controlled business errors.
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
- The production SMTP variables (`SMTP_HOST`, `SMTP_FROM_EMAIL`,
  `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`) remain reserved for the
  online Docker stack and must not be required to test registration locally.
- Mailpit is a development-only mailbox and must not be added to the online
  Docker stack.

## Tests

When modifying registration or email verification, update backend tests for:

- public registration without Bearer token;
- duplicate email rejection;
- password policy rejection;
- public email verification without Bearer token;
- browser email verification page from `GET /api/auth/verify-email`;
- JSON email verification from `POST /api/auth/verify-email`;
- missing or invalid verification token rejection;
- `/api/routes` public indicators for registration and verification routes.

Run `./test_backend.sh` after changes.
