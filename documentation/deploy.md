# Deployment

## Purpose

This document owns production deployment, runtime scripts, deployment archive
content, host directory preparation, Docker Compose startup and encrypted secret
handling.

## Release Artifacts

Production uses the container images published to GitHub Container Registry and
the minimal deployment archive `cloud-application-deploy-<version>.zip`. The
archive is generated for release tags matching `X.Y.Z` and contains only:

- `deploy.sh`
- `secure.sh`
- `age_identity_cleanup.sh`
- `prepare_directories.sh`
- `userns_remap_detection.sh`
- `docker-compose.online.yml`
- `.env.production.example`

Published images:

```text
ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest
```

The backend and frontend image versions come from the release tag. The age
utility image is published as `latest`.

## Deployment Environment Directory

Production startup should use an external environment directory passed with
`deploy.sh -e`. This directory must contain the three files directly:

```text
deploy-env/.env
deploy-env/identity.txt
deploy-env/secrets.tar.gz.age
```

The `.env` file is initialized from `.env.production.example`. Configure at
least:

- `APP_VERSION` with the application tag to deploy.
- `RUNTIME_UID` and `RUNTIME_GID` for the non-root `backend` and `web`
  container identity.
- `RUNTIME_HOST_UID` and `RUNTIME_HOST_GID` for the host identity that must
  write backend bind mounts.
- `POSTGRES_HOST_ROOT_UID` and `POSTGRES_HOST_ROOT_GID` for the host identity
  corresponding to root inside the PostgreSQL container.
- `DNS_NAME`, `BACKEND_PUBLIC_URL`, `FRONTEND_PUBLIC_URL`.
- `APPLICATION_WORKDIR` as the common parent for application work data.
- `USERS_WORKSPACE`, `BACKEND_IMG_HOST_DIR`, `BACKEND_LOG_HOST_DIR`,
  `POSTGRES_DATA_HOST_DIR` and `TRAEFIK_LETSENCRYPT_HOST_DIR` when the default
  subdirectories of `APPLICATION_WORKDIR` do not fit.
- non-secret SMTP variables.

With Docker `userns-remap`, host UID/GID values must be computed from the
subordinate range start in `/etc/subuid` or `/etc/subgid` plus the container
UID/GID. For example, with `dockremap:100000:65536` and `RUNTIME_UID=10001`,
`RUNTIME_HOST_UID=110001`.

## Host Directories

`deploy.sh -p -e <env-directory>` calls `prepare_directories.sh` before Docker
Compose startup. The script creates and validates the configured host directory
tree.

Default persistent directories are under `/var/lib/cloudcollectionapp`:

```text
/var/lib/cloudcollectionapp/users-workspace
/var/lib/cloudcollectionapp/images
/var/lib/cloudcollectionapp/logs
/var/lib/cloudcollectionapp/postgres-data
/var/lib/cloudcollectionapp/letsencrypt
```

Backend-writable directories must be writable by
`RUNTIME_HOST_UID:RUNTIME_HOST_GID`. `POSTGRES_DATA_HOST_DIR` must be owned by
`POSTGRES_HOST_ROOT_UID:POSTGRES_HOST_ROOT_GID` and is mounted to
`/var/lib/postgresql/data`. When Docker reports active `userns-remap` and the
subordinate ranges are readable, `prepare_directories.sh` rejects inconsistent
host owner configuration.

If the configured paths require administrator privileges, `prepare_directories.sh`
may use `sudo` to create directories and apply owners.

## Secret Archive

Production secrets must not be stored in clear text in `.env` or durably on
disk. `deploy.sh -p -e <env-directory>` decrypts `secrets.tar.gz.age` with
`identity.txt` into a temporary Docker-bind-compatible directory, prepares
Docker secret files, derives `DATABASE_URL`, starts Docker Compose, then removes
the decrypted files.

Required secrets inside the archive:

- `AUTH_ENV_ENCRYPTION_KEY`
- `AUTH_PASSWORD_ENCRYPTED`
- `AUTH_SECRET_KEY_ENCRYPTED`
- `POSTGRES_PASSWORD`
- `SMTP_PASSWORD`

The production Compose file consumes:

- `POSTGRES_PASSWORD_FILE` for the PostgreSQL service.
- `DATABASE_URL_FILE` for the backend.
- `AUTH_ENV_ENCRYPTION_KEY_FILE`, `AUTH_PASSWORD_ENCRYPTED_FILE` and
  `AUTH_SECRET_KEY_ENCRYPTED_FILE` for backend authentication.
- `SMTP_PASSWORD_FILE` for backend email delivery.

By default, the temporary decrypted secret directory is created under `/tmp` if
Docker can bind-mount a test file from there. Set `PRODUCTION_SECRETS_TMP_PARENT`
to force another parent, for example `/dev/shm` when it is visible by Docker on
the host.

The age utility runs through the published image
`ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest`; `age` does not
need to be installed on the host.

## Creating Or Updating Secrets

For a first installation, generate the age identity and encrypted archive from
the extracted deployment archive:

```bash
./secure.sh bootstrap
```

The command creates:

```text
.age/identity.txt
env/secrets.tar.gz.age
```

Keep a protected copy of `identity.txt` outside the repository and outside the
server before deleting it from the deployment host. To use the external
environment directory, copy:

```text
.age/identity.txt -> deploy-env/identity.txt
env/secrets.tar.gz.age -> deploy-env/secrets.tar.gz.age
```

To use an existing archive:

```bash
cp /secure/path/identity.txt /etc/cloudcollectionapp/deploy-env/identity.txt
cp /secure/path/secrets.tar.gz.age /etc/cloudcollectionapp/deploy-env/secrets.tar.gz.age
chmod 600 /etc/cloudcollectionapp/deploy-env/identity.txt /etc/cloudcollectionapp/deploy-env/secrets.tar.gz.age
```

To read or update one secret:

```bash
./secure.sh read --name POSTGRES_PASSWORD
./secure.sh set --name SMTP_PASSWORD --value "new-secret"
```

## Start, Recreate And Stop

Start production:

```bash
./deploy.sh -p -e /etc/cloudcollectionapp/deploy-env
```

Pull published images and recreate containers:

```bash
./deploy.sh -p -r -e /etc/cloudcollectionapp/deploy-env
```

Stop production:

```bash
./deploy.sh -p -s -e /etc/cloudcollectionapp/deploy-env
```

The same environment directory must be passed for stop because Docker Compose
needs the same `.env` values to interpolate the production Compose file.

## Email Runtime Configuration

Production email delivery uses the SMTP variables from the deployment `.env`
and the encrypted `SMTP_PASSWORD` secret from the age archive.

Main non-secret variables:

```text
BACKEND_PUBLIC_URL
FRONTEND_PUBLIC_URL
EMAIL_DELIVERY_MODE
ADMIN_NOTIFICATION_EMAIL
ADMIN_ACCOUNT_VALIDATION_ENABLED
EMAIL_VERIFICATION_TOKEN_TTL_HOURS
GAME_DUPLICATE_DAILY_NOTIFICATION_TIME
SMTP_FROM_EMAIL
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_USE_TLS
```

To test email delivery against the production Compose stack:

```bash
./scripts/test_email.sh -p --to destinataire@example.com
```

## Compose Contract

`docker-compose.online.yml` must run published images instead of building local
images:

- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:${APP_VERSION:-latest}`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:${APP_VERSION:-latest}`

In production, `deploy.sh -p -r` pulls the published backend and frontend
images before recreating containers. It does not build images locally.

The stack runs PostgreSQL as an internal `database` service. The backend waits
for the PostgreSQL healthcheck before starting.

The `backend` and `web` containers run with `user: RUNTIME_UID:RUNTIME_GID`.
The frontend image listens on the non-privileged internal port `8080`, routed by
Traefik. Traefik uses `userns_mode: host` because the Docker provider needs to
read `/var/run/docker.sock`; this socket already grants elevated access to the
Docker daemon and cannot be read by a remapped root user.

## Local Docker Commands

Local Docker development still runs from the repository checkout:

```bash
cp runtime/.env.local.example runtime/.env
./runtime/deploy.sh -d
./runtime/deploy.sh -d -s
```
