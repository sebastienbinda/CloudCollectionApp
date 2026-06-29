# CI Summary

## Key Points

- Continuous integration is handled by GitHub Actions.
- CI and PR validation workflow files are `.github/workflows/ci.yml`,
  `.github/workflows/validate-pr.yml` and `.gitlab-ci.yml`.
- Pull requests are validated for Conventional Commits title format and release
  note labels.
- The CI workflow runs on pull requests, on every branch push, and on every
  pushed Git tag.
- Backend tests run only when backend-related files change, when the workflow
  file changes, and on every pushed Git tag.
- Frontend tests run only when frontend-related files change, when the workflow
  file changes, and on every pushed Git tag.
- The frontend production build runs only when frontend-related files change,
  when the workflow file changes, and on every pushed Git tag.
- Application Docker images are published only when a Git tag matching `X.Y.Z`
  is pushed.
- Application Docker image versions come from the Git tag.
- The production deployment archive is generated and published as a GitHub
  release asset only when a Git tag matching `X.Y.Z` is pushed.
- The `age` utility image is published as `latest` only when a Git tag matching
  `X.Y.Z` is pushed and `docker/age-secrets.Dockerfile` changed since the
  previous release tag.
- Published images are pushed to GitHub Container Registry.

## Objective

The CI pipeline validates pull requests, branch pushes and tagged releases.
Application Docker images are published only for release tags, and the release
version is explicit: it is the pushed Git tag in `X.Y.Z` format.

## Push And Release Workflow

The `.github/workflows/ci.yml` workflow contains seven jobs:

- `change-detection`: detects whether backend validation, frontend validation or
  the age utility image publication is needed from the changed files.
- `backend-tests`: runs `./scripts/test_backend.sh`.
- `frontend-tests`: installs frontend dependencies with `npm ci` and runs
  `npm test`.
- `frontend-build`: installs frontend dependencies with `npm ci` and runs
  `npm run build`.
- `age-secrets-image`: for Git tags only, builds and pushes
  `ghcr.io/<owner>/<repository>/age-secrets:latest` when the tag matches
  `X.Y.Z` and `docker/age-secrets.Dockerfile` changed since the previous
  release tag.
- `deploy-archive`: for Git tags only, builds
  `cloud-application-deploy-<version>.zip`, keeps it as a downloadable workflow
  artifact, creates the GitHub release for the tag when needed, and uploads the
  archive as a versioned release asset.
- `docker-images`: for Git tags only, builds and pushes the backend and frontend
  Docker images after the validation jobs succeed.

On pull requests and branch pushes, backend tests run for every added, modified
or removed path prefixed with `backend/`, for `scripts/test_backend.sh`, for
`docker/backend.Dockerfile`, for `docker/backend.Dockerfile.dockerignore`, or
for `.github/workflows/ci.yml`. Frontend tests and the frontend build run for
every added, modified or removed path prefixed with `frontend/`, for
`docker/frontend.Dockerfile`, for `docker/frontend.Dockerfile.dockerignore`, or
for `.github/workflows/ci.yml`. On Git tags, both validations always run before
Docker publication. The age utility image is published only on release tag
events where `docker/age-secrets.Dockerfile` was added, modified or removed
since the previous release tag. If there is no previous release tag, the first
tag publishes the image when the Dockerfile exists in the tagged source.

For branch push events, the workflow reads GitHub's event payload first so that
file deletions and multi-commit branch pushes are detected reliably. It falls
back to Git diff commands when the payload does not contain changed paths. For
release tags, the workflow compares the tagged commit with the previous release
tag to decide whether the age utility image must be published.

The `docker-images`, `age-secrets-image` and `deploy-archive` jobs depend on
backend tests, frontend tests and the frontend build. Docker images and the
deployment archive must not be published if tests or frontend build fail. Branch
pushes never publish Docker images or deployment archives.

Backend tests run through `./scripts/test_backend.sh`, which prepares the Python
environment and then executes the backend test suite. ODS fixtures are now
loaded directly by import tests when needed.

Frontend tests run through `npm test` in `frontend/`, using Node.js' native test
runner against `frontend/tests/*.test.js`.

The deploy archive is built by `scripts/create_deploy_archive.sh` and named
`cloud-application-deploy-<version>.zip`, where `<version>` is the release tag.
It contains only the production runtime files required on the deployment host:

- `runtime/start.sh`
- `runtime/stop.sh`
- `runtime/secure.sh`
- `runtime/age_identity_cleanup.sh`
- `runtime/prepare_directories.sh`
- `runtime/docker-compose.online.yml`
- `runtime/.env.production.example`
- empty `runtime/.age/` and `runtime/env/` directories for the fixed age
  identity and archive locations.

The GitLab CI file `.gitlab-ci.yml` exposes deploy archive generation as the
`cloud_application_deploy_archive` job. It runs on release tags matching
`X.Y.Z` and publishes `cloud-application-deploy.zip` as a GitLab artifact. The
GitHub workflow is authoritative for GitHub release assets.

The workflow uses GitHub and Docker actions that target the Node.js 24 runtime.
This is independent from the frontend application build, which uses the Node.js
version configured in `actions/setup-node`.

## Pull Request Workflow

The `.github/workflows/ci.yml` workflow runs on pull requests to validate code
changes before merge. The `.github/workflows/validate-pr.yml` workflow also runs
on pull requests and validates PR metadata before merge.

The PR title must follow Conventional Commits format, for example:

```text
feat(database): add user registration
```

The PR must also have at least one release-note label:

- `enhancement`
- `bug`
- `documentation`
- `dependencies`
- `breaking-change`
- `ignore-for-release`

Configure branch protection on `main` so the CI validation jobs and this
metadata workflow are required status checks before merging.

## Docker Version

Docker image versions are resolved from the Git tag that triggered the workflow.
The tag is also passed to Docker builds as `APP_VERSION`, stored in the image
label `org.opencontainers.image.version`, and exposed to the frontend build as
`VITE_APP_VERSION`.

The tag must match the `X.Y.Z` format, for example:

```text
0.2.0
```

Docker images are not published from branch pushes. Tags that do not match
`X.Y.Z` fail before image publication. To publish a release, create and push a
version tag:

```bash
git tag 0.2.1
git push origin 0.2.1
```

## Released Migrations

Release tags matching `X.Y.Z` are production boundaries. A database migration
script that exists in a released tag must be treated as immutable.

- Do not modify files already released under `backend/migrations/versions/`.
- If a released migration contains a bug, add a new migration that corrects the
  live database state without requiring a database reset.
- If Alembic orchestration must change, update infrastructure code such as
  `backend/migrations/env.py` instead of rewriting released migration scripts.
- Before changing an existing migration, check `git tag --list` and compare the
  migration against released tags.
- Never use database deletion or volume reset as the production answer to a
  migration issue.

## Published Images

The images are published to GitHub Container Registry:

- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:latest`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:latest`
- `ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest`

The `<version>` tag is the Git tag that triggered the workflow.
The age utility image is always published with only the `latest` tag.

## Deployment Archive

The `cloud-application-deploy-<version>.zip` release asset is intended for
production hosts that only need to run already published container images. It
deliberately excludes Dockerfiles, source code, test files, build compose files
and local development configuration. Production startup is expected to run from
this extracted archive, not from a Git checkout.

After extraction, configure `runtime/.env` from
`runtime/.env.production.example`, place the age identity at
`runtime/.age/identity.txt`, place the encrypted age secrets archive at
`runtime/env/secrets.tar.gz.age`, then start production with:

```bash
./runtime/start.sh -p
```

If the deployment environment file uses another name, pass it explicitly with
`./runtime/start.sh -p -e <env-file>`.

## Production Compose

The production compose file `runtime/docker-compose.online.yml` must consume the
published GitHub Container Registry images instead of building local images:

- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:${APP_VERSION:-latest}`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:${APP_VERSION:-latest}`

`APP_VERSION` is read from the deployment `.env` file. When it is not defined,
Docker Compose resolves the image tag to `latest`.

The production stack also runs PostgreSQL as a `database` service on an
internal Docker network. In production deployment, `./runtime/start.sh -p`
calls `runtime/prepare_directories.sh` to create and validate the configured
host directory tree, then
decrypts the age secrets archive with the published `age-secrets` Docker image
into a temporary Docker-bind-compatible directory, passes
`POSTGRES_PASSWORD_FILE` to PostgreSQL, generates `DATABASE_URL` as a Docker
secret file, exposes it to the backend through `DATABASE_URL_FILE`, starts
Docker Compose, then removes the decrypted files from the host. The backend
must wait for the database healthcheck before starting.

The application containers `backend` and `web` run with the numeric
`RUNTIME_UID:RUNTIME_GID` configured in `runtime/.env`. The frontend image must
listen on the unprivileged internal port `8080`, and Traefik must route traffic
to that port. Host directories mounted by the backend must be writable by
`RUNTIME_HOST_UID:RUNTIME_HOST_GID`, which may differ from the container
runtime UID/GID when Docker `userns-remap` is enabled. With `userns-remap`,
these host IDs must be computed from the subordinate range start in `/etc/subuid`
or `/etc/subgid` plus `RUNTIME_UID` or `RUNTIME_GID`. When Docker reports active
`userns-remap` and those ranges are readable, `runtime/prepare_directories.sh`
must reject inconsistent host owner configuration before preparing writable
backend bind mounts.
Traefik uses `userns_mode: host` in production because the Docker provider
mounts `/var/run/docker.sock`; a remapped root user cannot read that host
socket, and the socket already grants elevated access to the Docker daemon.

Production PostgreSQL data must be persisted through the host bind mount
configured by `POSTGRES_DATA_HOST_DIR`. Deployment `.env` files must set
`APPLICATION_WORKDIR` as the common parent directory for application work data,
and the default production paths derive from it:
`USERS_WORKSPACE`, `BACKEND_IMG_HOST_DIR`, `BACKEND_LOG_HOST_DIR`,
`POSTGRES_DATA_HOST_DIR` and `TRAEFIK_LETSENCRYPT_HOST_DIR`. Production host
paths must be absolute. Do not replace the production database persistence path
with a transient anonymous volume. The PostgreSQL data directory must be owned
by `POSTGRES_HOST_ROOT_UID:POSTGRES_HOST_ROOT_GID`, the host identity
corresponding to root inside the PostgreSQL container. Without Docker
`userns-remap`, these values are `0:0`; with `userns-remap`, they must be the
host remapped IDs for container root. When the default
`/var/lib/cloudcollectionapp` tree is used, `runtime/prepare_directories.sh` may
use `sudo` during `./runtime/start.sh -p` to create host directories and apply
the expected owners, while Docker Compose still starts from the current
deployment user.

## Required GitHub Permissions

The workflow requires:

- `contents: write` to checkout the tagged source, create the GitHub release
  when needed and upload the versioned deployment archive release asset.
- `packages: write` to publish images to GitHub Container Registry.

## Development Rules

- Do not publish backend or frontend Docker images before backend tests,
  frontend tests and frontend build have passed.
- Publish Docker images only from Git tags matching `X.Y.Z`.
- Use the release tag as the Docker image version.
- Publish the deployment archive as
  `cloud-application-deploy-<version>.zip` on the GitHub release matching the
  tag.
- Publish the age utility image only as `latest`, only from release tags matching
  `X.Y.Z`, and only when `docker/age-secrets.Dockerfile` changed since the
  previous release tag.
- Treat migrations present in release tags matching `X.Y.Z` as immutable.
- Do not use `.env` to define the application release version; the release tag is
  the source of truth for published Docker images.
- Do not hardcode registry credentials in the repository. Use GitHub Actions
  token permissions or repository secrets.
- Keep PR metadata validation aligned with GitHub release note labels.
- If image names, registry location, trigger branches, or versioning behavior
  change, update this document in the same change set.
