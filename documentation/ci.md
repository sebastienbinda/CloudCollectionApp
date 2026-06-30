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
- Published images are pushed to GitHub Container Registry.

## Objective

The CI pipeline validates pull requests, branch pushes and tagged releases.
Application Docker images are published only for release tags, and the release
version is explicit: it is the pushed Git tag in `X.Y.Z` format.

## Push And Release Workflow

The `.github/workflows/ci.yml` workflow contains validation and publication
jobs:

- `change-detection`: detects which validation and publication jobs are needed
  from the changed files.
- `backend-tests`: runs `./scripts/test_backend.sh`.
- `frontend-tests`: installs frontend dependencies with `npm ci` and runs
  `npm test`.
- `frontend-build`: installs frontend dependencies with `npm ci` and runs
  `npm run build`.
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
Docker publication.

For branch push events, the workflow reads GitHub's event payload first so that
file deletions and multi-commit branch pushes are detected reliably. It falls
back to Git diff commands when the payload does not contain changed paths. For
release tags, the workflow may compare the tagged commit with the previous
release tag when a publication job needs changed-file decisions.

The `docker-images` and `deploy-archive` jobs depend on backend tests, frontend
tests and the frontend build. Docker images and the deployment archive must not
be published if tests or frontend build fail. Branch pushes never publish
Docker images or deployment archives.

Backend tests run through `./scripts/test_backend.sh`, which prepares the Python
environment and then executes the backend test suite. ODS fixtures are now
loaded directly by import tests when needed.

Frontend tests run through `npm test` in `frontend/`, using Node.js' native test
runner against `frontend/tests/*.test.js`.

The deploy archive is built by `scripts/create_deploy_archive.sh` and named
`cloud-application-deploy-<version>.zip`, where `<version>` is the release tag.
Archive content and runtime usage are documented in `documentation/deploy.md`.

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

The `<version>` tag is the Git tag that triggered the workflow.

## Deployment Runtime

Production deployment runtime and archive content are documented in
`documentation/deploy.md`.

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
- Treat migrations present in release tags matching `X.Y.Z` as immutable.
- Do not use `.env` to define the application release version; the release tag is
  the source of truth for published Docker images.
- Do not hardcode registry credentials in the repository. Use GitHub Actions
  token permissions or repository secrets.
- Keep PR metadata validation aligned with GitHub release note labels.
- If image names, registry location, trigger branches, or versioning behavior
  change, update this document in the same change set.
