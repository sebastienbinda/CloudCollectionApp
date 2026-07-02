#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : point d'entree de demarrage et d'arret des environnements.

set -o pipefail

BACKEND_PORT="${BACKEND_PORT:-7777}"
FRONTEND_PORT="${FRONTEND_PORT:-7778}"
WEB_PORT="${WEB_PORT:-8080}"
RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${RUNTIME_DIR}/.." && pwd)"
START_WORKDIR="$(pwd)"
DOCKER_COMPOSE_LOCAL_FILE="${PROJECT_ROOT}/docker/docker-compose.local.yml"
DOCKER_COMPOSE_ONLINE_FILE="${RUNTIME_DIR}/docker-compose.online.yml"
ENV_LOCAL_EXAMPLE_FILE="${RUNTIME_DIR}/.env.local.example"
ENV_PRODUCTION_EXAMPLE_FILE="${RUNTIME_DIR}/.env.production.example"
ENV_EXAMPLE_FILE="$ENV_LOCAL_EXAMPLE_FILE"
ENV_FILE="${RUNTIME_DIR}/.env"
ENV_DIRECTORY=""
PREPARE_DIRECTORIES_SCRIPT="${RUNTIME_DIR}/prepare_directories.sh"
AGE_IDENTITY_CLEANUP_SCRIPT="${RUNTIME_DIR}/age_identity_cleanup.sh"
AGE_SECRETS_ARCHIVE_FILE="${RUNTIME_DIR}/env/secrets.tar.gz.age"
AGE_SECRETS_IDENTITY_FILE="${RUNTIME_DIR}/.age/identity.txt"
AGE_SECRETS_IMAGE="${AGE_SECRETS_IMAGE:-ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest}"
PRODUCTION_SECRETS_TMP_PARENT="${PRODUCTION_SECRETS_TMP_PARENT:-}"
PRODUCTION_SECRETS_DIR=""

START_MODE="local"
DEPLOY_ACTION="start"
DEPLOY_ENV="local"
RECREATE_DOCKER_STACK=false

cleanup_production_secrets() {
  # Description : supprime les fichiers de secrets dechiffres temporaires.
  # Parametres : aucun.
  # Retour : void.
  if [ -n "$PRODUCTION_SECRETS_DIR" ] && [[ "$PRODUCTION_SECRETS_DIR" == "$PRODUCTION_SECRETS_TMP_PARENT"/cloudcollectionapp-secrets.* ]]; then
    rm -rf "$PRODUCTION_SECRETS_DIR"
    PRODUCTION_SECRETS_DIR=""
  fi
}

trap cleanup_production_secrets EXIT

print_usage() {
  echo "Usage: ./runtime/deploy.sh [-d] [-p] [-r] [-s] [-e <env-directory>]"
  echo "  -d  Demarre la stack Docker locale."
  echo "  -p  Demarre la stack Docker de production online."
  echo "  -r  Reconstruit les images Docker et force la recreation des conteneurs."
  echo "  -s  Arrete la cible selectionnee au lieu de la demarrer."
  echo "  -e  Utilise un repertoire d'environnement contenant .env, identity.txt et secrets.tar.gz.age."
}

while getopts "dprse:h" option; do
  case "$option" in
    d)
      START_MODE="docker"
      ;;
    p)
      START_MODE="docker"
      DEPLOY_ENV="online"
      ;;
    r)
      RECREATE_DOCKER_STACK=true
      ;;
    s)
      DEPLOY_ACTION="stop"
      ;;
    e)
      ENV_DIRECTORY="$OPTARG"
      ;;
    h)
      print_usage
      exit 0
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
done

resolve_environment_directory() {
  # Description : resout un repertoire d'environnement passe a deploy.sh -e.
  # Parametres : $1 chemin du repertoire d'environnement.
  # Retour : ecrit un chemin absolu.
  local configured_directory="$1"

  if [ -z "$configured_directory" ]; then
    abort_start "Le repertoire d'environnement passe avec -e ne doit pas etre vide."
  fi

  if [[ "$configured_directory" = /* ]]; then
    printf '%s\n' "$configured_directory"
  else
    printf '%s\n' "${START_WORKDIR}/${configured_directory#./}"
  fi
}

configure_environment_directory() {
  # Description : configure les chemins .env et age depuis un repertoire optionnel.
  # Parametres : aucun.
  # Retour : void.
  if [ -z "$ENV_DIRECTORY" ]; then
    return
  fi

  ENV_DIRECTORY="$(resolve_environment_directory "$ENV_DIRECTORY")"
  if [ ! -d "$ENV_DIRECTORY" ]; then
    abort_start "Le repertoire d'environnement est introuvable: ${ENV_DIRECTORY}"
  fi

  ENV_FILE="${ENV_DIRECTORY}/.env"
  AGE_SECRETS_ARCHIVE_FILE="${ENV_DIRECTORY}/secrets.tar.gz.age"
  AGE_SECRETS_IDENTITY_FILE="${ENV_DIRECTORY}/identity.txt"
}

if [ "$DEPLOY_ENV" = "online" ]; then
  ENV_EXAMPLE_FILE="$ENV_PRODUCTION_EXAMPLE_FILE"
else
  ENV_EXAMPLE_FILE="$ENV_LOCAL_EXAMPLE_FILE"
fi

start_local() {
  # Description : demarre le backend Flask et le frontend Vite en local.
  # Parametres : aucun.
  # Retour : void, lance les processus en arriere-plan.
  echo "Starting backend..."

  cd "${PROJECT_ROOT}/backend"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  BACKEND_PORT="$BACKEND_PORT" python app.py &

  echo "Starting frontend..."
  cd "${PROJECT_ROOT}/frontend"
  npm install
  BACKEND_PORT="$BACKEND_PORT" FRONTEND_PORT="$FRONTEND_PORT" npm run dev &
  cd "$PROJECT_ROOT"
}

start_docker() {
  # Description : demarre les conteneurs Docker Compose et supprime les orphelins.
  # Parametres : aucun, utilise WEB_PORT et les variables Docker Compose existantes.
  # Retour : void, demarre la stack Docker Compose.
  local docker_options=("--remove-orphans")

  if [ "$RECREATE_DOCKER_STACK" = true ]; then
    docker_options+=("--build" "--force-recreate")
  fi

  if [ "$DEPLOY_ENV" = "online" ]; then
    docker_options+=("--force-recreate")
    echo "Starting online Docker stack..."
    if [ "$RECREATE_DOCKER_STACK" = true ]; then
      echo "Pulling online Docker images..."
      if ! DOCKER_SECRETS_DIR="$PRODUCTION_SECRETS_DIR" docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_ONLINE_FILE" pull backend web; then
        cleanup_production_secrets
        abort_start "Le telechargement des images Docker de production a echoue."
      fi
    fi
    if ! DOCKER_SECRETS_DIR="$PRODUCTION_SECRETS_DIR" docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_ONLINE_FILE" up -d "${docker_options[@]}"; then
      cleanup_production_secrets
      abort_start "Le demarrage Docker Compose de production a echoue."
    fi
    cleanup_production_secrets
    prompt_remove_age_identity_after_start "$AGE_SECRETS_IDENTITY_FILE"
  else
    echo "Starting local Docker stack on web port ${WEB_PORT}..."
    WEB_PORT="$WEB_PORT" docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_LOCAL_FILE" up -d "${docker_options[@]}"
  fi
}

stop_local() {
  # Description : arrete les processus locaux ecouteurs des ports backend et frontend.
  # Parametres : aucun.
  # Retour : void, termine les processus detectes.
  local backend_pids
  local frontend_pids

  echo "Stopping backend (port ${BACKEND_PORT})..."
  backend_pids="$(lsof -ti :"$BACKEND_PORT")"
  if [ -n "$backend_pids" ]; then
    echo "$backend_pids" | xargs kill
    echo "Backend stopped."
  else
    echo "No backend process found on port ${BACKEND_PORT}."
  fi

  echo "Stopping frontend (port ${FRONTEND_PORT})..."
  frontend_pids="$(lsof -ti :"$FRONTEND_PORT")"
  if [ -n "$frontend_pids" ]; then
    echo "$frontend_pids" | xargs kill
    echo "Frontend stopped."
  else
    echo "No frontend process found on port ${FRONTEND_PORT}."
  fi
}

stop_docker() {
  # Description : arrete et supprime les conteneurs Docker Compose du projet.
  # Parametres : aucun.
  # Retour : void, arrete la stack Docker Compose.
  local production_secrets_placeholder="${PRODUCTION_SECRETS_TMP_PARENT:-/dev/shm}/cloudcollectionapp-secrets-placeholder"

  if [ "$DEPLOY_ENV" = "online" ]; then
    echo "Stopping online Docker stack..."
    DOCKER_SECRETS_DIR="$production_secrets_placeholder" docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_ONLINE_FILE" down --remove-orphans
  else
    echo "Stopping local Docker stack..."
    docker compose -f "$DOCKER_COMPOSE_LOCAL_FILE" down --remove-orphans
  fi
}

abort_start() {
  # Description : affiche un message d'arret explicite et annule le lancement.
  # Parametres : $1 message utilisateur.
  # Retour : quitte le script en erreur.
  echo ""
  echo "Demarrage annule."
  echo "$1"
  exit 1
}

configure_environment_directory

if [ ! -f "$AGE_IDENTITY_CLEANUP_SCRIPT" ]; then
  abort_start "Le script ${AGE_IDENTITY_CLEANUP_SCRIPT} est introuvable."
fi
source "$AGE_IDENTITY_CLEANUP_SCRIPT"

env_variable_exists() {
  # Description : indique si une variable est deja presente dans le fichier d'environnement.
  # Parametres : $1 nom de variable.
  # Retour : 0 si presente, 1 sinon.
  local variable_name="$1"
  if [ ! -f "$ENV_FILE" ]; then
    return 1
  fi
  grep -Eq "^[[:space:]]*(export[[:space:]]+)?${variable_name}[[:space:]]*=" "$ENV_FILE"
}

env_variable_value() {
  # Description : retourne la valeur courante d'une variable du fichier d'environnement.
  # Parametres : $1 nom de variable.
  # Retour : ecrit la valeur sur stdout.
  local variable_name="$1"
  local current_line

  current_line="$(
    grep -E "^[[:space:]]*(export[[:space:]]+)?${variable_name}[[:space:]]*=" "$ENV_FILE" 2>/dev/null \
      | tail -n 1 \
      | sed -E "s/^[[:space:]]*(export[[:space:]]+)?${variable_name}[[:space:]]*=[[:space:]]*//"
  )"
  printf '%s\n' "$current_line"
}

shell_env_variable_exists() {
  # Description : indique si une variable est definie dans l'environnement shell.
  # Parametres : $1 nom de variable.
  # Retour : 0 si definie, 1 sinon.
  local variable_name="$1"

  [ "${!variable_name+x}" = "x" ]
}

prompt_missing_env_value() {
  # Description : demande une valeur pour une variable manquante si le terminal le permet.
  # Parametres : $1 nom de variable, $2 valeur exemple.
  # Retour : ecrit la valeur retenue sur stdout.
  local variable_name="$1"
  local default_value="$2"
  local entered_value=""
  local default_label="$default_value"

  if [ -z "$default_label" ]; then
    default_label="vide"
  fi

  if [ -r /dev/tty ]; then
    if [[ "$variable_name" == *PASSWORD* || "$variable_name" == *SECRET* || "$variable_name" == *KEY* ]]; then
      read -r -s -p "Valeur pour ${variable_name} (entree vide = valeur exemple) : " entered_value </dev/tty
      echo "" >/dev/tty
    else
      read -r -p "Valeur pour ${variable_name} [${default_label}] : " entered_value </dev/tty
    fi
  fi

  if [ -n "$entered_value" ]; then
    printf '%s\n' "$entered_value"
  else
    printf '%s\n' "$default_value"
  fi
}

section_title_from_header() {
  # Description : extrait le titre lisible d'un en-tete de section .env.
  # Parametres : $1 ligne de titre commentee.
  # Retour : ecrit le titre sur stdout.
  local title_line="$1"

  title_line="${title_line#\# }"
  title_line="${title_line#\#}"
  printf '%s\n' "$title_line"
}

is_omitted_production_section() {
  # Description : indique si une section de l'exemple doit etre omise en production.
  # Parametres : $1 titre de section.
  # Retour : 0 si la section est omise, 1 sinon.
  local section_title="$1"

  [ "$section_title" = "EMAIL LOCAL AVEC MAILPIT" ]
}

is_omitted_production_variable() {
  # Description : indique si une variable sensible doit etre absente de runtime/.env en production.
  # Parametres : $1 nom de variable.
  # Retour : 0 si la variable est omise, 1 sinon.
  local variable_name="$1"

  case "$variable_name" in
    AUTH_ENV_ENCRYPTION_KEY | \
      AUTH_PASSWORD_ENCRYPTED | \
      AUTH_SECRET_KEY_ENCRYPTED | \
      POSTGRES_PASSWORD | \
      POSTGRES_PASSWORD_ENCRYPTED | \
      SMTP_PASSWORD)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

read_env_value_or_default() {
  # Description : retourne une valeur d'environnement, puis runtime/.env, puis une valeur par defaut.
  # Parametres : $1 nom de variable, $2 valeur par defaut.
  # Retour : ecrit la valeur retenue sur stdout.
  local variable_name="$1"
  local default_value="$2"
  local shell_value="${!variable_name:-}"

  if [ -n "$shell_value" ]; then
    printf '%s\n' "$shell_value"
    return
  fi

  if env_variable_exists "$variable_name"; then
    env_variable_value "$variable_name"
    return
  fi

  printf '%s\n' "$default_value"
}

read_required_secret_file() {
  # Description : lit un fichier de secret prepare depuis l'archive age.
  # Parametres : $1 nom du fichier secret.
  # Retour : ecrit la valeur du fichier sans retour ligne final.
  local secret_name="$1"
  local secret_file="${PRODUCTION_SECRETS_DIR}/${secret_name}"
  local secret_value

  if [ ! -f "$secret_file" ]; then
    abort_start "Le secret ${secret_name} est absent de l'archive age."
  fi

  secret_value="$(<"$secret_file")"
  printf '%s' "$secret_value"
}

validate_runtime_user() {
  # Description : valide les UID/GID utilises par les conteneurs et les bind mounts hotes.
  # Parametres : aucun.
  # Retour : void, annule si les valeurs ne sont pas numeriques.
  local runtime_uid
  local runtime_gid
  local runtime_host_uid
  local runtime_host_gid

  runtime_uid="$(read_env_value_or_default "RUNTIME_UID" "10001")"
  runtime_gid="$(read_env_value_or_default "RUNTIME_GID" "10001")"
  runtime_host_uid="$(read_env_value_or_default "RUNTIME_HOST_UID" "$runtime_uid")"
  runtime_host_gid="$(read_env_value_or_default "RUNTIME_HOST_GID" "$runtime_gid")"

  if [[ ! "$runtime_uid" =~ ^[0-9]+$ ]] || [[ ! "$runtime_gid" =~ ^[0-9]+$ ]]; then
    abort_start "RUNTIME_UID et RUNTIME_GID doivent etre des identifiants numeriques."
  fi

  if [[ ! "$runtime_host_uid" =~ ^[0-9]+$ ]] || [[ ! "$runtime_host_gid" =~ ^[0-9]+$ ]]; then
    abort_start "RUNTIME_HOST_UID et RUNTIME_HOST_GID doivent etre des identifiants numeriques."
  fi
}

prepare_runtime_directories() {
  # Description : prepare les repertoires hotes necessaires au demarrage Docker.
  # Parametres : aucun.
  # Retour : void, annule si l'arborescence n'est pas valide.
  if [ ! -x "$PREPARE_DIRECTORIES_SCRIPT" ]; then
    abort_start "Le script ${PREPARE_DIRECTORIES_SCRIPT} est introuvable ou non executable."
  fi

  if [ -n "$ENV_DIRECTORY" ]; then
    if ! "$PREPARE_DIRECTORIES_SCRIPT" --env-directory "$ENV_DIRECTORY" --mode "$DEPLOY_ENV"; then
      abort_start "La preparation de l'arborescence runtime a echoue."
    fi
    return
  fi

  if ! "$PREPARE_DIRECTORIES_SCRIPT" --env-file "$ENV_FILE" --mode "$DEPLOY_ENV"; then
    abort_start "La preparation de l'arborescence runtime a echoue."
  fi
}

container_path_for_age_secret() {
  # Description : convertit un chemin hote en chemin visible par le conteneur age.
  # Parametres : $1 chemin hote absolu.
  # Retour : ecrit le chemin conteneur sur stdout.
  local host_path="$1"

  if [[ "$host_path" == "$PROJECT_ROOT" ]]; then
    printf '/workspace\n'
    return
  fi

  if [[ "$host_path" == "$PROJECT_ROOT"/* ]]; then
    printf '/workspace/%s\n' "${host_path#"$PROJECT_ROOT"/}"
    return
  fi

  if [ -n "$ENV_DIRECTORY" ] && [[ "$host_path" == "$ENV_DIRECTORY" ]]; then
    printf '/env-directory\n'
    return
  fi

  if [ -n "$ENV_DIRECTORY" ] && [[ "$host_path" == "$ENV_DIRECTORY"/* ]]; then
    printf '/env-directory/%s\n' "${host_path#"$ENV_DIRECTORY"/}"
    return
  fi

  if [[ "$host_path" == "$PRODUCTION_SECRETS_TMP_PARENT"/* ]]; then
    printf '%s\n' "$host_path"
    return
  fi

  abort_start "Chemin non accessible depuis le conteneur age: ${host_path}"
}

ensure_age_secrets_image() {
  # Description : verifie que l'image age est disponible localement ou la telecharge.
  # Parametres : aucun.
  # Retour : void.
  if ! docker image inspect "$AGE_SECRETS_IMAGE" >/dev/null 2>&1; then
    echo "Telechargement de l'image age: ${AGE_SECRETS_IMAGE}"
    if ! docker pull "$AGE_SECRETS_IMAGE"; then
      abort_start "Impossible de telecharger l'image age ${AGE_SECRETS_IMAGE}."
    fi
  fi
}

docker_can_bind_file_from_directory() {
  # Description : indique si le daemon Docker voit un fichier hote depuis un repertoire.
  # Parametres : $1 repertoire parent teste.
  # Retour : 0 si Docker peut monter le fichier, 1 sinon.
  local parent_directory="$1"
  local test_directory
  local test_file
  local can_bind=false

  if [ ! -d "$parent_directory" ]; then
    return 1
  fi

  test_directory="$(mktemp -d "${parent_directory}/cloudcollectionapp-docker-bind-test.XXXXXX" 2>/dev/null)" || return 1
  test_file="${test_directory}/secret-test"
  printf 'ok\n' >"$test_file" || {
    rm -rf "$test_directory"
    return 1
  }
  chmod 444 "$test_file"

  if docker run --rm \
    --volume "${test_file}:/secret-test:ro" \
    "$AGE_SECRETS_IMAGE" \
    -lc 'test -f /secret-test && test "$(cat /secret-test)" = "ok"' >/dev/null 2>&1; then
    can_bind=true
  fi

  rm -rf "$test_directory"
  [ "$can_bind" = true ]
}

select_production_secrets_tmp_parent() {
  # Description : choisit un repertoire temporaire visible par le daemon Docker.
  # Parametres : aucun.
  # Retour : void, definit PRODUCTION_SECRETS_TMP_PARENT.
  local configured_parent="$PRODUCTION_SECRETS_TMP_PARENT"

  if [ -n "$configured_parent" ]; then
    if ! docker_can_bind_file_from_directory "$configured_parent"; then
      abort_start "Le daemon Docker ne peut pas monter les secrets depuis PRODUCTION_SECRETS_TMP_PARENT=${configured_parent}."
    fi
    return
  fi

  if docker_can_bind_file_from_directory "/tmp"; then
    PRODUCTION_SECRETS_TMP_PARENT="/tmp"
    echo "Utilisation temporaire de /tmp pour les secrets Docker."
    return
  fi

  if docker_can_bind_file_from_directory "/dev/shm"; then
    PRODUCTION_SECRETS_TMP_PARENT="/dev/shm"
    echo "Utilisation temporaire de /dev/shm pour les secrets Docker."
    return
  fi

  abort_start "Aucun repertoire temporaire compatible Docker trouve pour preparer les secrets."
}

decrypt_age_secrets_archive() {
  # Description : dechiffre l'archive age dans un repertoire temporaire de secrets.
  # Parametres : aucun.
  # Retour : void, prepare les fichiers de secrets pour Docker Compose.
  local container_archive_file
  local container_identity_file
  local environment_volume_options=()

  if [ ! -f "$AGE_SECRETS_ARCHIVE_FILE" ]; then
    abort_start "Archive de secrets age introuvable: ${AGE_SECRETS_ARCHIVE_FILE}"
  fi

  if [ ! -f "$AGE_SECRETS_IDENTITY_FILE" ]; then
    abort_start "Cle privee age introuvable: ${AGE_SECRETS_IDENTITY_FILE}"
  fi

  ensure_age_secrets_image
  select_production_secrets_tmp_parent
  PRODUCTION_SECRETS_DIR="$(mktemp -d "${PRODUCTION_SECRETS_TMP_PARENT}/cloudcollectionapp-secrets.XXXXXX")"
  chmod 700 "$PRODUCTION_SECRETS_DIR"
  container_archive_file="$(container_path_for_age_secret "$AGE_SECRETS_ARCHIVE_FILE")"
  container_identity_file="$(container_path_for_age_secret "$AGE_SECRETS_IDENTITY_FILE")"
  if [ -n "$ENV_DIRECTORY" ]; then
    environment_volume_options=("--volume" "${ENV_DIRECTORY}:/env-directory:ro")
  fi

  if ! docker run --rm \
    --user "$(id -u):$(id -g)" \
    --workdir /workspace \
    --volume "${PROJECT_ROOT}:/workspace:ro" \
    "${environment_volume_options[@]}" \
    "$AGE_SECRETS_IMAGE" \
    -lc 'set -euo pipefail; age --decrypt --identity "$2" "$1"' \
    -- "$container_archive_file" "$container_identity_file" \
    | tar -xzf - -C "$PRODUCTION_SECRETS_DIR"; then
    abort_start "Le dechiffrement ou l'extraction de l'archive de secrets a echoue."
  fi

  chmod 444 "$PRODUCTION_SECRETS_DIR"/* 2>/dev/null || true
}

prepare_production_docker_secrets() {
  # Description : prepare les secrets Docker Compose depuis l'archive age dechiffree.
  # Parametres : aucun.
  # Retour : void, cree aussi le secret DATABASE_URL derive du mot de passe PostgreSQL.
  local postgres_user
  local postgres_db
  local postgres_password
  local required_secret
  local required_secrets=(
    "AUTH_ENV_ENCRYPTION_KEY"
    "AUTH_PASSWORD_ENCRYPTED"
    "AUTH_SECRET_KEY_ENCRYPTED"
    "POSTGRES_PASSWORD"
    "SMTP_PASSWORD"
  )

  echo "Preparation des secrets Docker de production..."
  decrypt_age_secrets_archive

  for required_secret in "${required_secrets[@]}"; do
    if [ ! -f "${PRODUCTION_SECRETS_DIR}/${required_secret}" ]; then
      abort_start "Le secret ${required_secret} est absent de l'archive age."
    fi
  done

  postgres_user="$(read_env_value_or_default "POSTGRES_USER" "cloudcollectionapp")"
  postgres_db="$(read_env_value_or_default "POSTGRES_DB" "cloudcollectionapp")"
  postgres_password="$(read_required_secret_file "POSTGRES_PASSWORD")"
  printf 'postgresql://%s:%s@database:5432/%s\n' "$postgres_user" "$postgres_password" "$postgres_db" \
    >"${PRODUCTION_SECRETS_DIR}/DATABASE_URL"
  chmod 444 "${PRODUCTION_SECRETS_DIR}/DATABASE_URL"

  echo "Secrets Docker de production prets dans un repertoire temporaire en memoire."
}

validate_production_environment_before_docker_start() {
  # Description : restructure runtime/.env depuis l'exemple et ajoute les variables absentes.
  # Parametres : aucun.
  # Retour : void, annule le demarrage quand des variables ont ete ajoutees.
  local current_section=""
  local current_section_title=""
  local section_buffer=""
  local section_title_line=""
  local section_capture_remaining=0
  local section_is_omitted=false
  local pending_comments=""
  local temp_file
  local line
  local variable_name
  local default_value
  local selected_value
  local missing_count=0
  local missing_names=()

  echo "Verification du fichier d'environnement Docker de production..."

  if [ ! -f "$ENV_EXAMPLE_FILE" ]; then
    abort_start "Le fichier modele ${ENV_EXAMPLE_FILE} est introuvable."
  fi

  temp_file="$(mktemp "${ENV_FILE}.tmp.XXXXXX")"

  while IFS= read -r line || [ -n "$line" ]; do
    if [ "$section_capture_remaining" -gt 0 ]; then
      section_buffer+="${line}"$'\n'
      if [ "$section_capture_remaining" -eq 2 ]; then
        section_title_line="$line"
      fi
      section_capture_remaining=$((section_capture_remaining - 1))
      if [ "$section_capture_remaining" -eq 0 ]; then
        current_section="$section_buffer"
        current_section_title="$(section_title_from_header "$section_title_line")"
        if is_omitted_production_section "$current_section_title"; then
          section_is_omitted=true
          echo "Section locale omise en production: ${current_section_title}"
        else
          section_is_omitted=false
          printf '%s' "$current_section" >>"$temp_file"
        fi
      fi
      continue
    fi

    if [[ "$line" == "# ============================================================================="* ]]; then
      section_buffer="${line}"$'\n'
      section_capture_remaining=2
      section_title_line=""
      pending_comments=""
      continue
    fi

    if [ "$section_is_omitted" = true ]; then
      continue
    fi

    if [[ "$line" =~ ^# ]]; then
      pending_comments+="${line}"$'\n'
      continue
    fi

    if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
      variable_name="${line%%=*}"
      default_value="${line#*=}"
      if is_omitted_production_variable "$variable_name"; then
        pending_comments=""
        continue
      fi
      if shell_env_variable_exists "$variable_name"; then
        selected_value="${!variable_name}"
      elif env_variable_exists "$variable_name"; then
        selected_value="$(env_variable_value "$variable_name")"
      else
        selected_value="$(prompt_missing_env_value "$variable_name" "$default_value")"
        missing_names+=("$variable_name")
        missing_count=$((missing_count + 1))
      fi
      printf '%s' "$pending_comments" >>"$temp_file"
      printf '%s=%s\n' "$variable_name" "$selected_value" >>"$temp_file"
      pending_comments=""
      continue
    fi

    if [ -n "$pending_comments" ]; then
      printf '%s' "$pending_comments" >>"$temp_file"
      pending_comments=""
    fi
    printf '%s\n' "$line" >>"$temp_file"
    pending_comments=""
  done <"$ENV_EXAMPLE_FILE"

  mv "$temp_file" "$ENV_FILE"
  echo "Structure de ${ENV_FILE} alignee sur ${ENV_EXAMPLE_FILE} pour la production."

  if [ "$missing_count" -gt 0 ]; then
    echo ""
    echo "Variables ajoutees ou initialisees dans ${ENV_FILE}:"
    printf '  - %s\n' "${missing_names[@]}"
    abort_start "Configurez et verifiez les nouvelles variables avant de lancer les conteneurs."
  fi

  echo "Fichier d'environnement Docker de production complet."
}

if [ "$DEPLOY_ACTION" = "stop" ]; then
  if [ "$START_MODE" = "docker" ]; then
    stop_docker
  else
    stop_local
  fi
else
  if [ "$START_MODE" = "docker" ]; then
    if [ "$DEPLOY_ENV" = "online" ]; then
      validate_production_environment_before_docker_start
      validate_runtime_user
      prepare_runtime_directories
      prepare_production_docker_secrets
    else
      prepare_runtime_directories
    fi
    start_docker
  else
    start_local
  fi
fi
