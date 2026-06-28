#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-28
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : prepare l'arborescence runtime avant le demarrage Docker.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
DEPLOY_ENV="local"

print_usage() {
  echo "Usage: ./runtime/prepare_directories.sh [--env-file <path>] [--mode local|online]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --mode)
      DEPLOY_ENV="${2:-}"
      shift 2
      ;;
    -h | --help)
      print_usage
      exit 0
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
done

if [ "$DEPLOY_ENV" != "local" ] && [ "$DEPLOY_ENV" != "online" ]; then
  echo "Mode invalide: ${DEPLOY_ENV}"
  print_usage
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Fichier d'environnement introuvable: ${ENV_FILE}"
  exit 1
fi

env_value() {
  # Description : lit une valeur depuis le fichier .env sans executer son contenu.
  # Parametres : $1 nom de variable, $2 valeur par defaut.
  # Retour : ecrit la valeur retenue sur stdout.
  local variable_name="$1"
  local default_value="$2"
  local line
  local value

  line="$(grep -E "^[[:space:]]*${variable_name}=" "$ENV_FILE" 2>/dev/null | tail -n 1 || true)"
  if [ -z "$line" ]; then
    printf '%s\n' "$default_value"
    return
  fi

  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  printf '%s\n' "$value"
}

resolve_host_path() {
  # Description : resout un chemin hote comme Docker Compose le fera.
  # Parametres : $1 chemin configure.
  # Retour : ecrit un chemin absolu.
  local configured_path="$1"
  local base_dir="$SCRIPT_DIR"

  if [ "$DEPLOY_ENV" = "local" ]; then
    base_dir="${PROJECT_ROOT}/docker"
  fi

  if [ -z "$configured_path" ]; then
    printf '%s\n' "$configured_path"
    return
  fi

  if [[ "$configured_path" = /* ]]; then
    printf '%s\n' "$configured_path"
    return
  fi

  printf '%s\n' "${base_dir}/${configured_path#./}"
}

require_absolute_path() {
  # Description : refuse les chemins relatifs en production.
  # Parametres : $1 nom de variable, $2 chemin configure.
  # Retour : void.
  local variable_name="$1"
  local configured_path="$2"

  if [ "$DEPLOY_ENV" = "online" ] && [[ "$configured_path" != /* ]]; then
    echo "${variable_name} doit etre un chemin absolu en production: ${configured_path}"
    exit 1
  fi
}

directory_owner() {
  # Description : retourne le proprietaire numerique d'un repertoire.
  # Parametres : $1 chemin.
  # Retour : ecrit uid:gid.
  local directory_path="$1"

  if stat -c '%u:%g' "$directory_path" >/dev/null 2>&1; then
    stat -c '%u:%g' "$directory_path"
  else
    printf '%s:%s\n' "$(stat -f '%u' "$directory_path")" "$(stat -f '%g' "$directory_path")"
  fi
}

directory_mode() {
  # Description : retourne le mode octal portable d'un repertoire.
  # Parametres : $1 chemin.
  # Retour : ecrit le mode octal.
  local directory_path="$1"

  if stat -c '%a' "$directory_path" >/dev/null 2>&1; then
    stat -c '%a' "$directory_path"
  else
    stat -f '%Lp' "$directory_path"
  fi
}

runtime_can_write_directory() {
  # Description : indique si RUNTIME_UID:RUNTIME_GID peut ecrire dans un repertoire.
  # Parametres : $1 chemin.
  # Retour : 0 si writable, 1 sinon.
  local directory_path="$1"
  local owner
  local owner_uid
  local owner_gid
  local mode
  local owner_permissions
  local group_permissions
  local other_permissions

  owner="$(directory_owner "$directory_path")"
  owner_uid="${owner%%:*}"
  owner_gid="${owner##*:}"
  mode="$(directory_mode "$directory_path")"
  mode="${mode: -3}"
  owner_permissions="${mode:0:1}"
  group_permissions="${mode:1:1}"
  other_permissions="${mode:2:1}"

  if [ "$owner_uid" = "$RUNTIME_UID" ] && [ $((owner_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  if [ "$owner_gid" = "$RUNTIME_GID" ] && [ $((group_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  if [ $((other_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  return 1
}

ensure_directory() {
  # Description : cree un repertoire et verifie son proprietaire si necessaire.
  # Parametres : $1 libelle, $2 chemin configure, $3 true si writable par runtime.
  # Retour : void.
  local label="$1"
  local configured_path="$2"
  local runtime_writable="$3"
  local resolved_path
  local owner
  local expected_owner

  require_absolute_path "$label" "$configured_path"
  resolved_path="$(resolve_host_path "$configured_path")"

  if [ -z "$resolved_path" ]; then
    echo "${label} ne doit pas etre vide."
    exit 1
  fi

  mkdir -p "$resolved_path"

  if [ "$DEPLOY_ENV" = "online" ] && [ "$runtime_writable" = "true" ]; then
    expected_owner="${RUNTIME_UID}:${RUNTIME_GID}"
    if [ "$(id -u)" -eq 0 ]; then
      chown -R "$expected_owner" "$resolved_path"
    fi
    if ! runtime_can_write_directory "$resolved_path"; then
      owner="$(directory_owner "$resolved_path")"
      echo "${label} doit etre accessible en ecriture par ${expected_owner}, proprietaire actuel: ${owner}, mode: $(directory_mode "$resolved_path")."
      echo "Relancez le demarrage avec des droits permettant le chown, ou corrigez le proprietaire et les permissions du repertoire."
      exit 1
    fi
  fi

  echo "Repertoire pret: ${label} -> ${resolved_path}"
}

if [ "$DEPLOY_ENV" = "online" ]; then
  default_application_workdir="/var/lib/cloudcollectionapp"
else
  default_application_workdir="../runtime-data"
fi

APPLICATION_WORKDIR="$(env_value "APPLICATION_WORKDIR" "$default_application_workdir")"
RUNTIME_UID="$(env_value "RUNTIME_UID" "10001")"
RUNTIME_GID="$(env_value "RUNTIME_GID" "10001")"

if [ "$DEPLOY_ENV" = "online" ]; then
  require_absolute_path "APPLICATION_WORKDIR" "$APPLICATION_WORKDIR"
fi

ensure_directory "APPLICATION_WORKDIR" "$APPLICATION_WORKDIR" false
ensure_directory "USERS_WORKSPACE" "$(env_value "USERS_WORKSPACE" "${APPLICATION_WORKDIR}/users-workspace")" true
ensure_directory "BACKEND_IMG_HOST_DIR" "$(env_value "BACKEND_IMG_HOST_DIR" "${APPLICATION_WORKDIR}/images")" true
ensure_directory "BACKEND_LOG_HOST_DIR" "$(env_value "BACKEND_LOG_HOST_DIR" "${APPLICATION_WORKDIR}/logs")" true

if [ "$DEPLOY_ENV" = "online" ]; then
  ensure_directory "POSTGRES_DATA_HOST_DIR" "$(env_value "POSTGRES_DATA_HOST_DIR" "${APPLICATION_WORKDIR}/postgres-data")" false
  ensure_directory "TRAEFIK_LETSENCRYPT_HOST_DIR" "$(env_value "TRAEFIK_LETSENCRYPT_HOST_DIR" "${APPLICATION_WORKDIR}/letsencrypt")" false
fi

echo "Arborescence runtime validee."
