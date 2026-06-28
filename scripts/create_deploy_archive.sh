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
# Description : genere l'archive minimale de deploiement production.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_FILE="${1:-${PROJECT_ROOT}/cloud-application-deploy.zip}"
if [[ "$OUTPUT_FILE" != /* ]]; then
  OUTPUT_FILE="$(pwd)/${OUTPUT_FILE#./}"
fi
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
OUTPUT_NAME="$(basename "$OUTPUT_FILE")"
TEMP_DIR="$(mktemp -d)"
PACKAGE_DIR="${TEMP_DIR}/cloud-application-deploy"
TEMP_OUTPUT_FILE="${TEMP_DIR}/${OUTPUT_NAME}"

cleanup() {
  rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

mkdir -p "$OUTPUT_DIR"
mkdir -p "${PACKAGE_DIR}/runtime"

install -m 0755 "${PROJECT_ROOT}/runtime/start.sh" "${PACKAGE_DIR}/runtime/start.sh"
install -m 0755 "${PROJECT_ROOT}/runtime/stop.sh" "${PACKAGE_DIR}/runtime/stop.sh"
install -m 0755 "${PROJECT_ROOT}/runtime/secure.sh" "${PACKAGE_DIR}/runtime/secure.sh"
install -m 0755 "${PROJECT_ROOT}/runtime/prepare_directories.sh" "${PACKAGE_DIR}/runtime/prepare_directories.sh"
install -m 0644 "${PROJECT_ROOT}/runtime/docker-compose.online.yml" "${PACKAGE_DIR}/runtime/docker-compose.online.yml"
install -m 0644 "${PROJECT_ROOT}/runtime/.env.production.example" "${PACKAGE_DIR}/runtime/.env.production.example"

(
  cd "$TEMP_DIR"
  zip -qr "$TEMP_OUTPUT_FILE" cloud-application-deploy
)

mv "$TEMP_OUTPUT_FILE" "${OUTPUT_DIR}/${OUTPUT_NAME}"

echo "Archive de deploiement generee: ${OUTPUT_DIR}/${OUTPUT_NAME}"
