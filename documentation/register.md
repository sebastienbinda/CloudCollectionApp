# User Registration Rules

## Purpose

This document defines the rules to preserve when changing user registration or
email verification.

## Public Routes

- `POST /api/auth/register` must remain public: the user does not have an
  account yet and cannot have a Bearer token.
- `GET /api/auth/verify-email` and `POST /api/auth/verify-email` must remain
  public: the user validates the account from an email link before signing in.
- Keep these endpoints in `AuthGuard.protect_all_routes(..., exempt_endpoints=...)`.
- Keep `RouteDiscoveryService` reporting these endpoints with
  `requires_auth: false`, `access: "public"` and `auth_schemes: []`.

## Security Rules

- Never expose collection data from these public routes.
- Never return password hashes, raw passwords, email verification token hashes or
  raw verification tokens in API responses.
- Store only non-reversible password hashes.
- Store only the email verification token hash in database.
- Treat duplicate email, invalid password and invalid verification token as
  controlled business errors.
- Do not hardcode SMTP secrets, passwords, tokens or signing keys.

## Tests

When modifying registration or email verification, update backend tests for:

- public registration without Bearer token;
- duplicate email rejection;
- password policy rejection;
- public email verification without Bearer token;
- missing or invalid verification token rejection;
- `/api/routes` public indicators for registration and verification routes.

Run `./test_backend.sh` after changes.
