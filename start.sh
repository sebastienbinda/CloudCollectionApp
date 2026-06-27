#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
BACKEND_PORT="${BACKEND_PORT:-7777}"
FRONTEND_PORT="${FRONTEND_PORT:-7778}"
WEB_PORT="${WEB_PORT:-8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_LOCAL_FILE="${SCRIPT_DIR}/docker/docker-compose.local.yml"
DOCKER_COMPOSE_ONLINE_FILE="${SCRIPT_DIR}/docker/docker-compose.online.yml"
ENV_EXAMPLE_FILE="${SCRIPT_DIR}/docker/.env.example"
ENV_FILE="${SCRIPT_DIR}/docker/.env"

START_MODE="local"
DEPLOY_ENV="local"
RECREATE_DOCKER_STACK=false

print_usage() {
  echo "Usage: ./start.sh [-d] [-p] [-r]"
  echo "  -d  Demarre la stack Docker locale."
  echo "  -p  Demarre la stack Docker de production online."
  echo "  -r  Reconstruit les images Docker et force la recreation des conteneurs."
}

while getopts "dprh" option; do
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

start_local() {
  # Description : demarre le backend Flask et le frontend Vite en local.
  # Parametres : aucun.
  # Retour : void, lance les processus en arriere-plan.
  echo "Starting backend..."

  cd "${SCRIPT_DIR}/backend"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  BACKEND_PORT="$BACKEND_PORT" python app.py &

  echo "Starting frontend..."
  cd "${SCRIPT_DIR}/frontend"
  npm install
  BACKEND_PORT="$BACKEND_PORT" FRONTEND_PORT="$FRONTEND_PORT" npm run dev &
  cd "$SCRIPT_DIR"
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
    echo "Starting online Docker stack..."
    docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_ONLINE_FILE" up -d "${docker_options[@]}"
  else
    echo "Starting local Docker stack on web port ${WEB_PORT}..."
    WEB_PORT="$WEB_PORT" docker compose --env-file "$ENV_FILE" -f "$DOCKER_COMPOSE_LOCAL_FILE" up -d "${docker_options[@]}"
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

update_repository_before_docker_start() {
  # Description : synchronise le depot Git avant le demarrage Docker.
  # Parametres : aucun.
  # Retour : void, annule le demarrage si un merge est necessaire.
  local upstream_ref
  local local_revision
  local remote_revision
  local common_revision

  echo "Verification du depot Git..."

  if ! git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    abort_start "Le repertoire courant n'est pas un depot Git valide."
  fi

  upstream_ref="$(git -C "$SCRIPT_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null)"
  if [ -z "$upstream_ref" ]; then
    abort_start "Aucune branche distante de suivi n'est configuree. Impossible de faire le pull avant Docker."
  fi

  echo "Recuperation des dernieres informations depuis ${upstream_ref}..."
  if ! git -C "$SCRIPT_DIR" fetch --prune; then
    abort_start "La recuperation du depot distant a echoue. Verifiez le reseau ou vos droits Git."
  fi

  local_revision="$(git -C "$SCRIPT_DIR" rev-parse HEAD)"
  remote_revision="$(git -C "$SCRIPT_DIR" rev-parse '@{u}')"
  common_revision="$(git -C "$SCRIPT_DIR" merge-base HEAD '@{u}')"

  if [ "$local_revision" = "$remote_revision" ]; then
    echo "Depot Git deja a jour."
    return
  fi

  if [ "$local_revision" = "$common_revision" ]; then
    echo "Mise a jour du depot par fast-forward..."
    if ! git -C "$SCRIPT_DIR" pull --ff-only; then
      abort_start "Le pull fast-forward a echoue. Verifiez les modifications locales avant de relancer."
    fi
    echo "Depot Git mis a jour."
    return
  fi

  if [ "$remote_revision" = "$common_revision" ]; then
    echo "La branche locale contient des commits non presents sur le distant. Aucun pull necessaire."
    return
  fi

  abort_start "La branche locale et ${upstream_ref} ont diverge. Un merge ou rebase manuel est necessaire."
}

env_variable_exists() {
  # Description : indique si une variable est deja presente dans docker/.env.
  # Parametres : $1 nom de variable.
  # Retour : 0 si presente, 1 sinon.
  local variable_name="$1"
  if [ ! -f "$ENV_FILE" ]; then
    return 1
  fi
  grep -Eq "^[[:space:]]*${variable_name}=" "$ENV_FILE"
}

env_variable_value() {
  # Description : retourne la valeur courante d'une variable de docker/.env.
  # Parametres : $1 nom de variable.
  # Retour : ecrit la valeur sur stdout.
  local variable_name="$1"
  local current_line

  current_line="$(grep -E "^[[:space:]]*${variable_name}=" "$ENV_FILE" 2>/dev/null | tail -n 1)"
  printf '%s\n' "${current_line#*=}"
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

validate_production_environment_before_docker_start() {
  # Description : restructure docker/.env depuis l'exemple et ajoute les variables absentes.
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
    if [[ "$line" == "# ============================================================================="* ]]; then
      section_buffer="${line}"$'\n'
      section_capture_remaining=2
      section_title_line=""
      pending_comments=""
      continue
    fi

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
      if env_variable_exists "$variable_name"; then
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

if [ "$START_MODE" = "docker" ]; then
  if [ "$DEPLOY_ENV" = "online" ]; then
    update_repository_before_docker_start
    validate_production_environment_before_docker_start
  fi
  start_docker
else
  start_local
fi
