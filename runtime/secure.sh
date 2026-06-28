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
SECURE_IMAGE_NAME="${SECURE_IMAGE_NAME:-cloudcollectionapp-age-secrets:latest}"
SECURE_DOCKERFILE="${PROJECT_ROOT}/docker/age-secrets.Dockerfile"
DEFAULT_ARCHIVE_FILE="${RUNTIME_DIR}/secrets.tar.gz.age"

TEMP_DIRECTORIES=()

show_usage() {
  # Description : affiche l'aide du script.
  # Parametres : aucun.
  # Retour : void, ecrit l'aide sur stdout.
  cat <<'USAGE'
Usage:
  ./runtime/secure.sh build
  ./runtime/secure.sh encrypt --source-dir <dossier> --archive <archive.age> --recipient <age1...> [--recipient <age1...>]
  ./runtime/secure.sh decrypt --archive <archive.age> --output-dir <dossier> --identity <identity.txt>
  ./runtime/secure.sh read --archive <archive.age> --name <SECRET_NAME> --identity <identity.txt>
  ./runtime/secure.sh set --archive <archive.age> --name <SECRET_NAME> --value <valeur> --identity <identity.txt> --recipient <age1...>
  ./runtime/secure.sh set --archive <archive.age> --name <SECRET_NAME> --value-file <fichier> --identity <identity.txt> --recipient <age1...>

Options communes:
  --archive <archive.age>       Archive age cible. Defaut: runtime/secrets.tar.gz.age.
  --identity <identity.txt>     Cle privee age pour dechiffrer.
  --recipient <age1...>         Destinataire age utilise au chiffrement. Repetable.
  --build                       Reconstruit l'image utilitaire avant l'action.

Secrets attendus par ./runtime/start.sh -p:
  AUTH_ENV_ENCRYPTION_KEY
  AUTH_PASSWORD_ENCRYPTED
  AUTH_SECRET_KEY_ENCRYPTED
  POSTGRES_PASSWORD
  SMTP_PASSWORD
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

resolve_path() {
  # Description : resout un chemin relatif depuis la racine du projet.
  # Parametres : $1 chemin absolu ou relatif.
  # Retour : ecrit le chemin absolu sur stdout.
  local path_value="$1"

  if [[ "$path_value" = /* ]]; then
    printf '%s\n' "$path_value"
  else
    printf '%s\n' "${PROJECT_ROOT}/${path_value#./}"
  fi
}

ensure_secure_image() {
  # Description : construit l'image age si elle est absente ou demandee.
  # Parametres : $1 `true` pour forcer la reconstruction.
  # Retour : void.
  local force_build="$1"

  if [ "$force_build" = "true" ] || ! docker image inspect "$SECURE_IMAGE_NAME" >/dev/null 2>&1; then
    docker build -f "$SECURE_DOCKERFILE" -t "$SECURE_IMAGE_NAME" "$PROJECT_ROOT"
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

encrypt_directory() {
  # Description : chiffre un dossier de secrets en archive tar.gz age.
  # Parametres : dossier source, archive cible, destinataires age.
  # Retour : void.
  local source_dir="$1"
  local archive_file="$2"
  shift 2
  local recipients=("$@")
  local recipient_args=()
  local recipient
  local container_archive_file
  local container_source_dir

  [ -d "$source_dir" ] || abort_secure_action "Dossier source introuvable: ${source_dir}"
  [ "${#recipients[@]}" -gt 0 ] || abort_secure_action "Au moins un destinataire age est requis."

  for recipient in "${recipients[@]}"; do
    recipient_args+=("-r" "$recipient")
  done

  mkdir -p "$(dirname "$archive_file")"
  container_source_dir="$(container_path_for "$source_dir")"
  container_archive_file="$(container_path_for "$archive_file")"
  run_age_container -lc 'set -euo pipefail; tar -czf - -C "$1" . | age "${@:3}" -o "$2"' \
    -- "$container_source_dir" "$container_archive_file" "${recipient_args[@]}"
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
  # Parametres : archive, nom, valeur, fichier valeur, identite, destinataires age.
  # Retour : void.
  local archive_file="$1"
  local secret_name="$2"
  local secret_value="$3"
  local secret_value_file="$4"
  local identity_file="$5"
  shift 5
  local recipients=("$@")
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

  encrypt_directory "$temp_dir" "$archive_file" "${recipients[@]}"
}

command_name="${1:-}"
if [ -z "$command_name" ] || [ "$command_name" = "-h" ] || [ "$command_name" = "--help" ]; then
  show_usage
  exit 0
fi
shift

force_build="false"
archive_file="$DEFAULT_ARCHIVE_FILE"
source_dir=""
output_dir=""
identity_file=""
secret_name=""
secret_value=""
secret_value_file=""
secret_value_was_provided="false"
secret_value_file_was_provided="false"
recipients=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --archive)
      archive_file="$(resolve_path "${2:-}")"
      shift 2
      ;;
    --source-dir)
      source_dir="$(resolve_path "${2:-}")"
      shift 2
      ;;
    --output-dir)
      output_dir="$(resolve_path "${2:-}")"
      shift 2
      ;;
    --identity)
      identity_file="$(resolve_path "${2:-}")"
      shift 2
      ;;
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
      secret_value_file="$(resolve_path "${2:-}")"
      secret_value_file_was_provided="true"
      shift 2
      ;;
    --recipient)
      recipients+=("${2:-}")
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

archive_file="$(resolve_path "$archive_file")"

if [ "$command_name" != "build" ]; then
  ensure_secure_image "$force_build"
fi

case "$command_name" in
  build)
    ensure_secure_image "true"
    ;;
  encrypt)
    [ -n "$source_dir" ] || abort_secure_action "--source-dir est requis."
    encrypt_directory "$source_dir" "$archive_file" "${recipients[@]}"
    ;;
  decrypt)
    [ -n "$output_dir" ] || abort_secure_action "--output-dir est requis."
    [ -n "$identity_file" ] || abort_secure_action "--identity est requis."
    decrypt_archive "$archive_file" "$output_dir" "$identity_file"
    ;;
  read)
    [ -n "$secret_name" ] || abort_secure_action "--name est requis."
    [ -n "$identity_file" ] || abort_secure_action "--identity est requis."
    read_secret "$archive_file" "$secret_name" "$identity_file"
    ;;
  set)
    [ -n "$secret_name" ] || abort_secure_action "--name est requis."
    [ -n "$identity_file" ] || abort_secure_action "--identity est requis."
    if [ "$secret_value_was_provided" = "true" ] && [ "$secret_value_file_was_provided" = "true" ]; then
      abort_secure_action "--value et --value-file sont exclusifs."
    fi
    if [ "$secret_value_was_provided" = "false" ] && [ "$secret_value_file_was_provided" = "false" ]; then
      abort_secure_action "--value ou --value-file est requis."
    fi
    set_secret "$archive_file" "$secret_name" "$secret_value" "$secret_value_file" "$identity_file" "${recipients[@]}"
    ;;
  *)
    abort_secure_action "Commande inconnue: ${command_name}"
    ;;
esac
