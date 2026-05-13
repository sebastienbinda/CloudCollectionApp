#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-13
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lance un email de test dans le conteneur backend deja demarre.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker/docker-compose.local.yml"
RECIPIENT_EMAIL=""
EMAIL_SUBJECT="Test email CloudCollectionApp"
EMAIL_BODY=""
USE_ONLINE_STACK=false

print_usage() {
  echo "Usage: ./test_email.sh --to adresse@example.com [-p] [--subject 'Sujet'] [--body 'Message']"
  echo "  --to       Adresse destinataire de l'email de test."
  echo "  -p        Utilise la stack Docker online au lieu de la stack locale."
  echo "  --subject Sujet optionnel de l'email."
  echo "  --body    Corps optionnel de l'email."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --to)
      RECIPIENT_EMAIL="${2:-}"
      shift 2
      ;;
    --subject)
      EMAIL_SUBJECT="${2:-}"
      shift 2
      ;;
    --body)
      EMAIL_BODY="${2:-}"
      shift 2
      ;;
    -p|--production)
      USE_ONLINE_STACK=true
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Argument inconnu: $1" >&2
      print_usage
      exit 1
      ;;
  esac
done

if [ -z "$RECIPIENT_EMAIL" ]; then
  echo "Le parametre --to est obligatoire." >&2
  print_usage
  exit 1
fi

if [ "$USE_ONLINE_STACK" = true ]; then
  COMPOSE_FILE="${SCRIPT_DIR}/docker/docker-compose.online.yml"
fi

if ! docker compose -f "$COMPOSE_FILE" ps --status running backend >/dev/null 2>&1; then
  echo "Le conteneur backend ne semble pas demarre pour ${COMPOSE_FILE}." >&2
  echo "Demarrez-le avec ./start.sh -d ou ./start.sh -p." >&2
  exit 1
fi

command_args=(
  python
  -
  --to "$RECIPIENT_EMAIL"
  --subject "$EMAIL_SUBJECT"
)

if [ -n "$EMAIL_BODY" ]; then
  command_args+=(--body "$EMAIL_BODY")
fi

docker compose -f "$COMPOSE_FILE" exec -T backend "${command_args[@]}" \
  < "${SCRIPT_DIR}/backend/scripts/send_test_email.py"
