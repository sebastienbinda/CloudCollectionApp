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
START_WORKDIR="$(pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
DEPLOY_ENV="local"

# shellcheck source=runtime/userns_remap_detection.sh
source "${SCRIPT_DIR}/userns_remap_detection.sh"

print_usage() {
  echo "Usage: ./runtime/prepare_directories.sh [--env-file <path>] [--env-directory <path>] [--mode local|online]"
}

resolve_environment_directory() {
  # Description : resout un repertoire d'environnement relatif au repertoire courant.
  # Parametres : $1 chemin du repertoire d'environnement.
  # Retour : ecrit un chemin absolu.
  local configured_directory="$1"

  if [ -z "$configured_directory" ]; then
    echo "Le repertoire d'environnement ne doit pas etre vide."
    exit 1
  fi

  if [[ "$configured_directory" = /* ]]; then
    printf '%s\n' "$configured_directory"
  else
    printf '%s\n' "${START_WORKDIR}/${configured_directory#./}"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --env-directory)
      ENV_DIRECTORY="$(resolve_environment_directory "${2:-}")"
      ENV_FILE="${ENV_DIRECTORY}/.env"
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

  line="$(grep -E "^[[:space:]]*(export[[:space:]]+)?${variable_name}[[:space:]]*=" "$ENV_FILE" 2>/dev/null | tail -n 1 || true)"
  if [ -z "$line" ]; then
    printf '%s\n' "$default_value"
    return
  fi

  value="$(printf '%s\n' "$line" | sed -E "s/^[[:space:]]*(export[[:space:]]+)?${variable_name}[[:space:]]*=[[:space:]]*//")"
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

run_privileged_command() {
  # Description : execute une commande avec les privileges necessaires en production.
  # Parametres : commande et arguments a executer.
  # Retour : code retour de la commande executee.
  if [ "$DEPLOY_ENV" = "online" ] && [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
    "$@" 2>/dev/null || sudo "$@"
    return $?
  fi

  "$@"
}

host_runtime_can_write_directory() {
  # Description : indique si l'UID/GID hote du runtime peut ecrire dans un repertoire.
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

  if [ "$owner_uid" = "$RUNTIME_HOST_UID" ] && [ $((owner_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  if [ "$owner_gid" = "$RUNTIME_HOST_GID" ] && [ $((group_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  if [ $((other_permissions & 2)) -ne 0 ]; then
    return 0
  fi

  return 1
}

host_user_can_access_directory() {
  # Description : indique si un UID/GID hote peut lire, ecrire et traverser un repertoire.
  # Parametres : $1 chemin, $2 uid hote, $3 gid hote.
  # Retour : 0 si accessible, 1 sinon.
  local directory_path="$1"
  local expected_uid="$2"
  local expected_gid="$3"
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

  if [ "$owner_uid" = "$expected_uid" ] && [ $((owner_permissions & 7)) -eq 7 ]; then
    return 0
  fi

  if [ "$owner_gid" = "$expected_gid" ] && [ $((group_permissions & 7)) -eq 7 ]; then
    return 0
  fi

  if [ $((other_permissions & 7)) -eq 7 ]; then
    return 0
  fi

  return 1
}

validate_numeric_identifier() {
  # Description : verifie qu'un identifiant Unix est numerique.
  # Parametres : $1 nom de variable, $2 valeur.
  # Retour : void.
  local variable_name="$1"
  local variable_value="$2"

  if [[ ! "$variable_value" =~ ^[0-9]+$ ]]; then
    echo "${variable_name} doit etre un identifiant numerique: ${variable_value}"
    exit 1
  fi
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
  local container_owner

  require_absolute_path "$label" "$configured_path"
  resolved_path="$(resolve_host_path "$configured_path")"

  if [ -z "$resolved_path" ]; then
    echo "${label} ne doit pas etre vide."
    exit 1
  fi

  if ! run_privileged_command mkdir -p "$resolved_path"; then
    echo "Impossible de creer ${label}: ${resolved_path}"
    if [ "$DEPLOY_ENV" = "online" ] && [ "$(id -u)" -ne 0 ]; then
      echo "Ce chemin necessite probablement des privileges administrateur."
      echo "Installez sudo ou creez le repertoire avec un utilisateur autorise, puis relancez ./runtime/deploy.sh -p."
    fi
    exit 1
  fi

  if [ "$DEPLOY_ENV" = "online" ] && [ "$runtime_writable" = "true" ]; then
    expected_owner="${RUNTIME_HOST_UID}:${RUNTIME_HOST_GID}"
    container_owner="${RUNTIME_UID}:${RUNTIME_GID}"
    if ! run_privileged_command chown -R "$expected_owner" "$resolved_path"; then
      echo "${label} doit appartenir a l'identite hote ${expected_owner} correspondant au runtime conteneur ${container_owner}."
      echo "Impossible d'appliquer ce proprietaire automatiquement."
      echo "Relancez le demarrage avec des droits permettant le chown, ou corrigez le proprietaire et les permissions du repertoire."
      exit 1
    fi
    if ! host_runtime_can_write_directory "$resolved_path"; then
      owner="$(directory_owner "$resolved_path")"
      echo "${label} doit etre accessible en ecriture par l'identite hote ${expected_owner} correspondant au runtime conteneur ${container_owner}."
      echo "Proprietaire actuel: ${owner}, mode: $(directory_mode "$resolved_path")."
      echo "Relancez le demarrage avec des droits permettant le chown, ou corrigez le proprietaire et les permissions du repertoire."
      exit 1
    fi
  fi

  echo "Repertoire pret: ${label} -> ${resolved_path}"
}

ensure_postgres_data_directory() {
  # Description : prepare le repertoire persistant PostgreSQL pour le root du conteneur.
  # Parametres : $1 chemin configure.
  # Retour : void.
  local configured_path="$1"
  local resolved_path
  local owner

  require_absolute_path "POSTGRES_DATA_HOST_DIR" "$configured_path"
  resolved_path="$(resolve_host_path "$configured_path")"

  if [ -z "$resolved_path" ]; then
    echo "POSTGRES_DATA_HOST_DIR ne doit pas etre vide."
    exit 1
  fi

  if ! run_privileged_command mkdir -p "$resolved_path"; then
    echo "Impossible de creer POSTGRES_DATA_HOST_DIR: ${resolved_path}"
    if [ "$DEPLOY_ENV" = "online" ] && [ "$(id -u)" -ne 0 ]; then
      echo "Ce chemin necessite probablement des privileges administrateur."
      echo "Installez sudo ou creez le repertoire avec un utilisateur autorise, puis relancez ./runtime/deploy.sh -p."
    fi
    exit 1
  fi

  if [ "$DEPLOY_ENV" = "online" ]; then
    if ! run_privileged_command chown -R "${POSTGRES_HOST_ROOT_UID}:${POSTGRES_HOST_ROOT_GID}" "$resolved_path"; then
      echo "POSTGRES_DATA_HOST_DIR doit appartenir a l'identite hote ${POSTGRES_HOST_ROOT_UID}:${POSTGRES_HOST_ROOT_GID} correspondant au root du conteneur PostgreSQL."
      echo "Impossible d'appliquer ce proprietaire automatiquement."
      echo "Relancez le demarrage avec des droits permettant le chown, ou corrigez le proprietaire et les permissions du repertoire."
      exit 1
    fi
    if ! run_privileged_command chmod 700 "$resolved_path"; then
      echo "Impossible d'appliquer le mode 700 sur POSTGRES_DATA_HOST_DIR: ${resolved_path}"
      exit 1
    fi
    if ! host_user_can_access_directory "$resolved_path" "$POSTGRES_HOST_ROOT_UID" "$POSTGRES_HOST_ROOT_GID"; then
      owner="$(directory_owner "$resolved_path")"
      echo "POSTGRES_DATA_HOST_DIR doit etre accessible par l'identite hote ${POSTGRES_HOST_ROOT_UID}:${POSTGRES_HOST_ROOT_GID} correspondant au root du conteneur PostgreSQL."
      echo "Proprietaire actuel: ${owner}, mode: $(directory_mode "$resolved_path")."
      exit 1
    fi
  fi

  echo "Repertoire pret: POSTGRES_DATA_HOST_DIR -> ${resolved_path}"
}

ensure_shared_memory_directory() {
  # Description : prepare le repertoire tmpfs utilise pour les secrets Docker temporaires.
  # Parametres : aucun.
  # Retour : void.
  local shared_memory_directory="/dev/shm"
  local mode

  if ! run_privileged_command mkdir -p "$shared_memory_directory"; then
    echo "Impossible de creer SHARED_MEMORY_TMPFS: ${shared_memory_directory}"
    echo "Creez ${shared_memory_directory} avec des droits administrateur, puis relancez ./runtime/deploy.sh -p."
    exit 1
  fi

  if ! run_privileged_command chown 0:0 "$shared_memory_directory"; then
    echo "Impossible d'appliquer le proprietaire root:root sur ${shared_memory_directory}."
    echo "Corrigez le proprietaire du repertoire, puis relancez ./runtime/deploy.sh -p."
    exit 1
  fi

  if ! run_privileged_command chmod 1777 "$shared_memory_directory"; then
    echo "Impossible d'appliquer le mode 1777 sur ${shared_memory_directory}."
    echo "Corrigez les permissions du repertoire, puis relancez ./runtime/deploy.sh -p."
    exit 1
  fi

  mode="$(directory_mode "$shared_memory_directory")"
  if [ "${mode: -4}" != "1777" ]; then
    echo "${shared_memory_directory} doit avoir le mode 1777. Mode actuel: ${mode}."
    exit 1
  fi

  echo "Repertoire pret: SHARED_MEMORY_TMPFS -> ${shared_memory_directory}"
}

if [ "$DEPLOY_ENV" = "online" ]; then
  default_application_workdir="/var/lib/cloudcollectionapp"
else
  default_application_workdir="../runtime-data"
fi

APPLICATION_WORKDIR="$(env_value "APPLICATION_WORKDIR" "$default_application_workdir")"
RUNTIME_UID="$(env_value "RUNTIME_UID" "10001")"
RUNTIME_GID="$(env_value "RUNTIME_GID" "10001")"
RUNTIME_HOST_UID="$(env_value "RUNTIME_HOST_UID" "$RUNTIME_UID")"
RUNTIME_HOST_GID="$(env_value "RUNTIME_HOST_GID" "$RUNTIME_GID")"
POSTGRES_HOST_ROOT_UID="$(env_value "POSTGRES_HOST_ROOT_UID" "0")"
POSTGRES_HOST_ROOT_GID="$(env_value "POSTGRES_HOST_ROOT_GID" "0")"

validate_numeric_identifier "RUNTIME_UID" "$RUNTIME_UID"
validate_numeric_identifier "RUNTIME_GID" "$RUNTIME_GID"
validate_numeric_identifier "RUNTIME_HOST_UID" "$RUNTIME_HOST_UID"
validate_numeric_identifier "RUNTIME_HOST_GID" "$RUNTIME_HOST_GID"
validate_numeric_identifier "POSTGRES_HOST_ROOT_UID" "$POSTGRES_HOST_ROOT_UID"
validate_numeric_identifier "POSTGRES_HOST_ROOT_GID" "$POSTGRES_HOST_ROOT_GID"
validate_userns_remap_directory_owners

if [ "$DEPLOY_ENV" = "online" ]; then
  require_absolute_path "APPLICATION_WORKDIR" "$APPLICATION_WORKDIR"
  ensure_shared_memory_directory
fi

ensure_directory "APPLICATION_WORKDIR" "$APPLICATION_WORKDIR" false
ensure_directory "USERS_WORKSPACE" "$(env_value "USERS_WORKSPACE" "${APPLICATION_WORKDIR}/users-workspace")" true
ensure_directory "BACKEND_IMG_HOST_DIR" "$(env_value "BACKEND_IMG_HOST_DIR" "${APPLICATION_WORKDIR}/images")" true
ensure_directory "BACKEND_LOG_HOST_DIR" "$(env_value "BACKEND_LOG_HOST_DIR" "${APPLICATION_WORKDIR}/logs")" true

if [ "$DEPLOY_ENV" = "online" ]; then
  ensure_postgres_data_directory "$(env_value "POSTGRES_DATA_HOST_DIR" "${APPLICATION_WORKDIR}/postgres-data")"
  ensure_directory "TRAEFIK_LETSENCRYPT_HOST_DIR" "$(env_value "TRAEFIK_LETSENCRYPT_HOST_DIR" "${APPLICATION_WORKDIR}/letsencrypt")" false
fi

echo "Arborescence runtime validee."
