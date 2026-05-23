# Backend Architecture Rules

## Purpose

This document defines the backend code architecture to preserve when changing
Flask startup, HTTP controllers, business services, ODS handling, database
infrastructure, authentication, routing or backend tests.

## Core Principles

- `backend/app.py` must remain the Flask composition entry point only.
- `backend/app.py` must configure cross-cutting services, create Flask/CORS,
  initialize runtime infrastructure, instantiate controllers, register routes
  and apply global route protection.
- `backend/app.py` must not contain business logic, payload validation, ODS
  manipulation, database queries or endpoint implementation details.
- HTTP endpoints must live in controllers under `backend/controllers/`.
- Business workflows must live in domain services under `backend/services/`.
- Persistence details must live in repositories or infrastructure services,
  not in controllers.
- ODS parsing, writing, backup and formula handling must stay under
  `backend/services/ods/`.
- Database schema, ORM models, repositories and migrations must follow
  `documentation/database.md`.
- Authentication, route protection and frontend session contracts must follow
  `documentation/authentication.md`.
- Keep backend files under 500 lines and methods under 150 lines. Split by
  domain before those limits are reached.

## Current Entry Points

- `backend/app.py`: Flask application composition root.
- `backend/controllers/`: HTTP route registration and HTTP response mapping.
- `backend/services/`: domain, infrastructure and integration services.
- `backend/models/`: simple transport/domain models not backed by the database.
- `backend/services/database/`: SQLAlchemy models, database configuration,
  schema initialization and repositories.
- `backend/migrations/`: Alembic environment and migration scripts.
- `backend/tests/`: backend unit and route tests.

## Layers And Responsibilities

### Flask Composition

`backend/app.py` is responsible for the startup sequence:

1. configure backend logging;
2. create Flask and configure CORS;
3. initialize the PostgreSQL schema when database configuration is present;
4. instantiate shared services and controllers;
5. register controller routes;
6. apply global Bearer protection with `AuthGuard`;
7. run Flask only when executed directly.

Do not add route handlers directly in `app.py`. Create or extend a controller
instead.

### Controllers

Controllers are responsible for HTTP concerns:

- registering Flask URL rules;
- reading query parameters and JSON payloads;
- invoking backend services;
- mapping service results to JSON or file responses;
- mapping domain errors to HTTP status codes;
- applying route-specific authentication/profile decorators when needed.

Controllers must not:

- manipulate ODS XML directly;
- perform SQL queries directly;
- duplicate authentication token validation;
- contain reusable business decisions that belong in services.

Use one controller per functional area when possible, for example:

- `AuthenticationController` for authentication, registration and email
  verification routes;
- `UserController` for administrative user management;
- `RouteController` for `/api/routes`;
- `UserGamesCollectionController` for platform game collection routes;
- `UserWishListController` for wishlist routes;
- `PlatformController` for platform metadata and images.

### Services

Services own business behavior and orchestration.

Use domain folders under `backend/services/`:

- `auth/`: token, password, profile, registration and email verification logic;
- `database/`: database configuration, ORM models, repositories and schema
  initialization;
- `email/`: email configuration and sending;
- `formatting/`: value formatting helpers;
- `games/`: game collection workflows and add-game choices;
- `logging/`: backend logging setup and handlers;
- `ods/`: ODS reading, writing, backup, cache, path resolution and formulas;
- `routing/`: route catalog discovery;
- `security/`: secret encryption utilities;
- `users/`: user administration workflows and status;
- `validation/`: payload validation rules.

Services may compose other services, validators and repositories. Keep service
constructors injectable when useful for tests.

### Database Infrastructure

Database code must follow these boundaries:

- one ORM model class per file under `backend/services/database/`;
- repositories own SQLAlchemy persistence details;
- business decisions using persisted data belong in services outside the
  repository layer;
- schema initialization and Alembic orchestration belong in database
  infrastructure services or `backend/migrations/env.py`;
- database structure changes must use Alembic migrations and update
  `documentation/database.md` when the schema contract changes.

### ODS Infrastructure

ODS code must preserve the file as the current collection source of truth.

- Readers parse ODS content and expose normalized data to services.
- Writers update `content.xml` while preserving spreadsheet styles.
- Backup services create a backup before writes.
- Cache services own read caching and invalidation.
- Validators reject invalid payloads before writer calls.

Do not bypass these services from controllers.

### Authentication And Authorization

- Public endpoints must be explicitly documented in
  `documentation/authentication.md`.
- All non-public routes must be protected by `AuthGuard.protect_all_routes`.
- Route-specific profile checks must use `AuthGuard.require_profile`.
- Do not read or validate Bearer tokens directly in controllers except for an
  explicitly documented exception.

### Tests

Backend tests should mirror the layer being changed:

- controller or route behavior: update route tests such as
  `backend/tests/test_app_routes.py`;
- business service behavior: update the relevant service test;
- ODS parsing/writing behavior: update ODS reader/writer/cache tests;
- database schema or migration orchestration: update database tests;
- authentication and authorization behavior: update auth route and token tests.

After backend code changes, run:

```bash
./test_backend.sh
```

Rebuild affected Docker images when runtime behavior changes.

## Adding New Backend Features

When adding a feature:

1. identify the functional domain first;
2. search for similar controllers, services, validators and tests;
3. add or extend the controller only for HTTP mapping;
4. put business logic in a service under the domain folder;
5. put payload validation in `backend/services/validation/` when reusable;
6. add or update backend tests for the changed behavior;
7. update functional documentation when a documented area changes;
8. update `README.md` when behavior, commands, routes, configuration or
   architecture visible to maintainers changes.
