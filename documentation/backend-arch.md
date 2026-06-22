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
- ODS parsing for user imports must stay under `backend/services/ods/`.
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
- `UserCollectionImportController` for connected-user collection status,
  collection import routes and collection reinitialization;
- `CollectionController` for connected-user SQL collection consultation,
  future game actions and raw user ODS download;
- `RouteController` for `/api/routes`;
- `PlatformController`, `StudioController` and `GameController` for public
  Bibliotheque reads of global platforms, studios and games.
- `PlatformImageController` for platform image upload, accepted public image
  files and administrator moderation routes.

### Services

Services own business behavior and orchestration.

Use domain folders under `backend/services/`:

- `auth/`: token, password, profile, registration and email verification logic;
- `database/`: database configuration, ORM models, repositories and schema
  initialization. The platform catalog seed/update services also live there
  because they own SQL synchronization from backend CSV resources;
- `email/`: email configuration and sending;
- `formatting/`: value formatting helpers;
- `collection/`: connected-user SQL collection consultation and query
  contracts; `collection/imports/` also owns format-independent import
  contracts, value mapping, matching configuration and shared validators;
- `library/`: public read-only consultation of global reference games,
  platforms and studios, plus platform image upload/public read/moderation
  business services;
- `logging/`: backend logging setup and handlers;
- `ods/`: user collection ODS import readers, archive access, XML fallback and
  import cache;
- `routing/`: route catalog discovery;
- `security/`: secret encryption utilities;
- `users/`: user administration workflows, user status and connected-user
  collection import orchestration;
Services may compose other services, validators and repositories. Keep service
constructors injectable when useful for tests.

Endpoints that expose a `sort` query parameter must have their final ordering
owned by the backend service/repository layer. Frontend clients may request a
supported sort order, but must not be required to recalculate list ordering
after receiving backend results.

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
- the platform reference catalog is cached server-side by schema for five
  hours. The cache is shared by public Library reads and user import platform
  matching, protected by an in-process lock, and invalidated after imports,
  Library reset cleanup and admin CSV synchronization.

### ODS Infrastructure

ODS code is limited to user import parsing. SQL is the source of truth for
collection consultation after import.

- Import readers parse ODS content and expose normalized data to services.
- ODS readers own only format-specific extraction, sheet/range addressing and
  row traversal. They delegate reusable value conversion to services under
  `backend/services/collection/imports/`.
- The raw user ODS download sends `t_user.collection_file_path` without parsing.
- No collection consultation route may depend on a global ODS path, ODS writer,
  embedded image extraction or spreadsheet formula recalculation.
- Cache services may be used only inside the import reader to avoid repeated
  reads during a single import workflow.

Do not bypass these services from controllers.

The user collection import and reinitialization workflows must use domain
services under `backend/services/users/`. Format-specific parsing belongs to
dedicated reader infrastructure, such as the ODS readers under
`backend/services/ods/`. Controllers may save the multipart upload to a
temporary file, but parsing, copying to the user workspace, transaction
orchestration, reinitialization cleanup and cleanup on failure belong to
services and repositories.

Platform image workflows must keep HTTP mapping in
`backend/controllers/platform_image_controller.py`. File validation, storage
path selection, public accepted-image lookup, moderation status/type decisions
and administrator notifications belong in `backend/services/library/`.
Persistence details for `t_platform_image` belong in
`backend/services/database/platform_image_repository.py`. Controllers must not
copy files, build SQL queries or decide whether an image is public.

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
- ODS import parsing behavior: update ODS reader/cache tests;
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
5. put reusable payload validation in the owning domain service or a dedicated
   domain helper;
6. add or update backend tests for the changed behavior;
7. update functional documentation when a documented area changes;
8. update `README.md` when behavior, commands, routes, configuration or
   architecture visible to maintainers changes.
