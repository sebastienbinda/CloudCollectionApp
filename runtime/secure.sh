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
# Description : gestion de l'archive age des secrets Docker de production.

set -euo pipefail

RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${RUNTIME_DIR}/.." && pwd)"
SECURE_IMAGE_NAME="${SECURE_IMAGE_NAME:-ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest}"
SECURE_DOCKERFILE="${PROJECT_ROOT}/docker/age-secrets.Dockerfile"
AGE_DIRECTORY="${RUNTIME_DIR}/.age"
ENV_DIRECTORY="${RUNTIME_DIR}/env"
IDENTITY_FILE="${AGE_DIRECTORY}/identity.txt"
ARCHIVE_FILE="${ENV_DIRECTORY}/secrets.tar.gz.age"
REQUIRED_SECRETS=(
  "AUTH_ENV_ENCRYPTION_KEY"
  "AUTH_PASSWORD_ENCRYPTED"
  "AUTH_SECRET_KEY_ENCRYPTED"
  "POSTGRES_PASSWORD"
  "SMTP_PASSWORD"
  "GITHUB_FEEDBACK_TOKEN"
)

TEMP_DIRECTORIES=()

show_usage() {
  # Description : affiche l'aide du script.
  # Parametres : aucun.
  # Retour : void, ecrit l'aide sur stdout.
  cat <<'USAGE'
Usage:
  ./runtime/secure.sh build
  ./runtime/secure.sh bootstrap
  ./runtime/secure.sh keygen
  ./runtime/secure.sh encrypt
  ./runtime/secure.sh decrypt
  ./runtime/secure.sh read --name <SECRET_NAME>
  ./runtime/secure.sh set --name <SECRET_NAME> --value <valeur>
  ./runtime/secure.sh set --name <SECRET_NAME> --value-file <fichier>

Chemins fixes:
  Cle privee age:              runtime/.age/identity.txt
  Dossier des secrets:         runtime/env/
  Archive age:                 runtime/env/secrets.tar.gz.age

Options:
  --name <SECRET_NAME>          Nom du secret a lire ou modifier.
  --value <valeur>              Valeur du secret a enregistrer.
  --value-file <fichier>        Fichier contenant la valeur du secret.
  --build                       Reconstruit l'image utilitaire avant l'action.

Secrets attendus par ./runtime/deploy.sh -p:
  AUTH_ENV_ENCRYPTION_KEY
  AUTH_PASSWORD_ENCRYPTED
  AUTH_SECRET_KEY_ENCRYPTED
  POSTGRES_PASSWORD
  SMTP_PASSWORD
  GITHUB_FEEDBACK_TOKEN
USAGE
}

abort_secure_action() {
  # Description : affiche une erreur et arrete le script.
  # Parametres : $1 message d'erreur.
  # Retour : quitte le script en erreur.
  echo "Erreur: $1" >&2
  exit 1
}

cleanup_temp_directories() {
  # Description : supprime les dossiers temporaires crees par le script.
  # Parametres : aucun.
  # Retour : void.
  local directory_path

  for directory_path in "${TEMP_DIRECTORIES[@]:-}"; do
    if [ -n "$directory_path" ] && [[ "$directory_path" == /tmp/cloudcollectionapp-secure.* ]]; then
      rm -rf "$directory_path"
    fi
  done
}

trap cleanup_temp_directories EXIT

create_temp_directory() {
  # Description : cree un dossier temporaire suivi pour nettoyage.
  # Parametres : aucun.
  # Retour : ecrit le chemin cree sur stdout.
  local directory_path

  directory_path="$(mktemp -d /tmp/cloudcollectionapp-secure.XXXXXX)"
  TEMP_DIRECTORIES+=("$directory_path")
  printf '%s\n' "$directory_path"
}

create_secure_workspace() {
  # Description : cree un dossier temporaire prive suivi pour nettoyage.
  # Parametres : aucun.
  # Retour : ecrit le chemin cree sur stdout.
  local directory_path

  directory_path="$(create_temp_directory)"
  chmod 700 "$directory_path"
  printf '%s\n' "$directory_path"
}

ensure_secure_image() {
  # Description : construit l'image age si elle est absente ou demandee.
  # Parametres : $1 `true` pour forcer la reconstruction.
  # Retour : void.
  local force_build="$1"

  if [ "$force_build" = "true" ] && [ -f "$SECURE_DOCKERFILE" ]; then
    docker build -f "$SECURE_DOCKERFILE" -t "$SECURE_IMAGE_NAME" "$PROJECT_ROOT"
    return
  fi

  if ! docker image inspect "$SECURE_IMAGE_NAME" >/dev/null 2>&1; then
    docker pull "$SECURE_IMAGE_NAME"
  fi
}

run_age_container() {
  # Description : execute une commande bash dans l'image utilitaire age.
  # Parametres : commande bash et arguments.
  # Retour : code de sortie de la commande Docker.
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    --workdir /workspace \
    --volume "${PROJECT_ROOT}:/workspace" \
    --volume "/tmp:/tmp" \
    --volume "/private/tmp:/private/tmp" \
    "$SECURE_IMAGE_NAME" "$@"
}

container_path_for() {
  # Description : convertit un chemin hote en chemin visible par le conteneur.
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

  if [[ "$host_path" == /tmp/* ]] || [[ "$host_path" == /private/tmp/* ]]; then
    printf '%s\n' "$host_path"
    return
  fi

  abort_secure_action "Chemin non accessible depuis le conteneur: ${host_path}"
}

validate_secret_name() {
  # Description : valide un nom de fichier secret autorise dans l'archive.
  # Parametres : $1 nom de secret.
  # Retour : void, echoue si le nom est dangereux.
  local secret_name="$1"

  if [[ ! "$secret_name" =~ ^[A-Z][A-Z0-9_]*$ ]]; then
    abort_secure_action "Nom de secret invalide: ${secret_name}"
  fi
}

validate_required_secret_files() {
  # Description : verifie que les secrets requis sont presents avant chiffrement.
  # Parametres : $1 dossier contenant les fichiers de secrets.
  # Retour : void, echoue si un secret obligatoire manque.
  local source_dir="$1"
  local required_secret

  for required_secret in "${REQUIRED_SECRETS[@]}"; do
    [ -f "${source_dir}/${required_secret}" ] || abort_secure_action "Secret obligatoire absent: ${source_dir}/${required_secret}"
  done
}

ensure_identity_file() {
  # Description : verifie que l'identite age fixe existe.
  # Parametres : aucun.
  # Retour : void, echoue si la cle privee est absente.
  [ -f "$IDENTITY_FILE" ] || abort_secure_action "Cle privee age introuvable: ${IDENTITY_FILE}. Lancez ./runtime/secure.sh keygen."
}

age_recipient_from_identity() {
  # Description : extrait le destinataire age public depuis l'identite fixe.
  # Parametres : aucun.
  # Retour : ecrit le destinataire age sur stdout.
  local container_identity_file

  ensure_identity_file
  container_identity_file="$(container_path_for "$IDENTITY_FILE")"
  run_age_container -lc 'set -euo pipefail; age-keygen -y "$1"' -- "$container_identity_file"
}

encrypt_directory() {
  # Description : chiffre un dossier de secrets en archive tar.gz age.
  # Parametres : dossier source, archive cible, destinataire age.
  # Retour : void.
  local source_dir="$1"
  local archive_file="$2"
  local recipient="$3"
  local container_archive_file
  local container_source_dir
  local excluded_archive_name

  [ -d "$source_dir" ] || abort_secure_action "Dossier source introuvable: ${source_dir}"

  mkdir -p "$(dirname "$archive_file")"
  excluded_archive_name="$(basename "$archive_file")"
  container_source_dir="$(container_path_for "$source_dir")"
  container_archive_file="$(container_path_for "$archive_file")"
  run_age_container -lc 'set -euo pipefail; tar --exclude="./$3" -czf - -C "$1" . | age -r "$4" -o "$2"' \
    -- "$container_source_dir" "$container_archive_file" "$excluded_archive_name" "$recipient"
}

decrypt_archive() {
  # Description : dechiffre une archive age vers un dossier de sortie.
  # Parametres : archive, dossier sortie, identite age.
  # Retour : void.
  local archive_file="$1"
  local output_dir="$2"
  local identity_file="$3"
  local container_archive_file
  local container_identity_file
  local container_output_dir

  [ -f "$archive_file" ] || abort_secure_action "Archive introuvable: ${archive_file}"
  [ -f "$identity_file" ] || abort_secure_action "Identite age introuvable: ${identity_file}"

  mkdir -p "$output_dir"
  container_archive_file="$(container_path_for "$archive_file")"
  container_output_dir="$(container_path_for "$output_dir")"
  container_identity_file="$(container_path_for "$identity_file")"
  run_age_container -lc 'set -euo pipefail; age --decrypt --identity "$3" "$1" | tar -xzf - -C "$2"' \
    -- "$container_archive_file" "$container_output_dir" "$container_identity_file"
}

generate_age_identity() {
  # Description : genere une nouvelle identite age et affiche le destinataire public.
  # Parametres : aucun.
  # Retour : void, ecrit l'identite dans le fichier fixe.
  local container_output_file

  mkdir -p "$AGE_DIRECTORY"
  container_output_file="$(container_path_for "$IDENTITY_FILE")"
  run_age_container -lc 'set -euo pipefail; age-keygen -o "$1"' -- "$container_output_file"
  chmod 600 "$IDENTITY_FILE"
}

prompt_secret_value() {
  # Description : demande interactivement la valeur d'un secret obligatoire.
  # Parametres : $1 nom du secret.
  # Retour : ecrit la valeur saisie sur stdout.
  local secret_name="$1"
  local entered_value=""

  while [ -z "$entered_value" ]; do
    if [ -t 0 ]; then
      read -r -s -p "Valeur pour ${secret_name}: " entered_value </dev/tty
      echo "" >/dev/tty
    else
      printf 'Valeur pour %s: ' "$secret_name" >&2
      read -r entered_value || abort_secure_action "Saisie interrompue pour ${secret_name}."
    fi
    if [ -z "$entered_value" ]; then
      echo "Le secret ${secret_name} est obligatoire." >&2
    fi
  done

  printf '%s\n' "$entered_value"
}

create_interactive_secret_files() {
  # Description : cree les fichiers de secrets depuis une saisie interactive.
  # Parametres : $1 dossier temporaire de creation.
  # Retour : void.
  local output_dir="$1"
  local required_secret
  local secret_value

  for required_secret in "${REQUIRED_SECRETS[@]}"; do
    secret_value="$(prompt_secret_value "$required_secret")"
    printf '%s\n' "$secret_value" >"${output_dir}/${required_secret}"
    chmod 600 "${output_dir}/${required_secret}"
  done
}

bootstrap_secure_archive() {
  # Description : initialise la cle age, les secrets temporaires et l'archive chiffree.
  # Parametres : aucun.
  # Retour : void.
  local temp_secret_dir

  [ ! -e "$IDENTITY_FILE" ] || abort_secure_action "La cle existe deja: ${IDENTITY_FILE}"
  [ ! -e "$ARCHIVE_FILE" ] || abort_secure_action "L'archive existe deja: ${ARCHIVE_FILE}"

  mkdir -p "$AGE_DIRECTORY" "$ENV_DIRECTORY"
  temp_secret_dir="$(create_secure_workspace)"

  echo "Creation de la cle privee age: ${IDENTITY_FILE}"
  generate_age_identity
  echo ""
  echo "Saisie des secrets de production. Les fichiers en clair sont crees uniquement dans: ${temp_secret_dir}"
  create_interactive_secret_files "$temp_secret_dir"
  validate_required_secret_files "$temp_secret_dir"

  echo "Creation de l'archive chiffree: ${ARCHIVE_FILE}"
  encrypt_directory "$temp_secret_dir" "$ARCHIVE_FILE" "$(age_recipient_from_identity)"
  rm -rf "$temp_secret_dir"

  echo ""
  echo "Initialisation terminee."
  echo "A conserver:"
  echo "  - ${IDENTITY_FILE} (cle privee age, hors depot)"
  echo "  - ${ARCHIVE_FILE} (archive chiffree age)"
  echo "A supprimer:"
  echo "  - aucun fichier en clair: le dossier temporaire de creation a ete supprime."
}

read_secret() {
  # Description : lit un secret depuis l'archive sans extraire durablement les autres fichiers.
  # Parametres : archive, nom de secret, identite age.
  # Retour : ecrit la valeur du secret sur stdout.
  local archive_file="$1"
  local secret_name="$2"
  local identity_file="$3"
  local temp_dir

  validate_secret_name "$secret_name"
  temp_dir="$(create_temp_directory)"
  decrypt_archive "$archive_file" "$temp_dir" "$identity_file" >/dev/null
  [ -f "${temp_dir}/${secret_name}" ] || abort_secure_action "Secret absent de l'archive: ${secret_name}"
  cat "${temp_dir}/${secret_name}"
}

set_secret() {
  # Description : modifie ou cree un secret dans l'archive age.
  # Parametres : archive, nom, valeur, fichier valeur, identite, destinataire age.
  # Retour : void.
  local archive_file="$1"
  local secret_name="$2"
  local secret_value="$3"
  local secret_value_file="$4"
  local identity_file="$5"
  local recipient="$6"
  local temp_dir

  validate_secret_name "$secret_name"
  temp_dir="$(create_temp_directory)"
  decrypt_archive "$archive_file" "$temp_dir" "$identity_file" >/dev/null

  if [ -n "$secret_value_file" ]; then
    [ -f "$secret_value_file" ] || abort_secure_action "Fichier de valeur introuvable: ${secret_value_file}"
    cp "$secret_value_file" "${temp_dir}/${secret_name}"
  else
    printf '%s\n' "$secret_value" >"${temp_dir}/${secret_name}"
  fi

  encrypt_directory "$temp_dir" "$archive_file" "$recipient"
}

command_name="${1:-}"
if [ -z "$command_name" ] || [ "$command_name" = "-h" ] || [ "$command_name" = "--help" ]; then
  show_usage
  exit 0
fi
shift

force_build="false"
secret_name=""
secret_value=""
secret_value_file=""
secret_value_was_provided="false"
secret_value_file_was_provided="false"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --name)
      secret_name="${2:-}"
      shift 2
      ;;
    --value)
      secret_value="${2:-}"
      secret_value_was_provided="true"
      shift 2
      ;;
    --value-file)
      secret_value_file="${2:-}"
      secret_value_file_was_provided="true"
      shift 2
      ;;
    --build)
      force_build="true"
      shift
      ;;
    *)
      abort_secure_action "Option inconnue: $1"
      ;;
  esac
done

if [ "$command_name" != "build" ]; then
  ensure_secure_image "$force_build"
fi

case "$command_name" in
  build)
    ensure_secure_image "true"
    ;;
  bootstrap)
    bootstrap_secure_archive
    ;;
  keygen)
    generate_age_identity
    ;;
  encrypt)
    mkdir -p "$ENV_DIRECTORY"
    validate_required_secret_files "$ENV_DIRECTORY"
    encrypt_directory "$ENV_DIRECTORY" "$ARCHIVE_FILE" "$(age_recipient_from_identity)"
    ;;
  decrypt)
    mkdir -p "$ENV_DIRECTORY"
    decrypt_archive "$ARCHIVE_FILE" "$ENV_DIRECTORY" "$IDENTITY_FILE"
    ;;
  read)
    [ -n "$secret_name" ] || abort_secure_action "--name est requis."
    read_secret "$ARCHIVE_FILE" "$secret_name" "$IDENTITY_FILE"
    ;;
  set)
    [ -n "$secret_name" ] || abort_secure_action "--name est requis."
    if [ "$secret_value_was_provided" = "true" ] && [ "$secret_value_file_was_provided" = "true" ]; then
      abort_secure_action "--value et --value-file sont exclusifs."
    fi
    if [ "$secret_value_was_provided" = "false" ] && [ "$secret_value_file_was_provided" = "false" ]; then
      abort_secure_action "--value ou --value-file est requis."
    fi
    set_secret "$ARCHIVE_FILE" "$secret_name" "$secret_value" "$secret_value_file" "$IDENTITY_FILE" "$(age_recipient_from_identity)"
    ;;
  *)
    abort_secure_action "Commande inconnue: ${command_name}"
    ;;
esac
