#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-04
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : utilitaire de preparation de l'environnement Python backend et lancement des tests.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
VENV_DIR="${BACKEND_DIR}/.venv"
REQUIREMENTS_FILE="${BACKEND_DIR}/requirements.txt"
REQUIREMENTS_STAMP="${VENV_DIR}/.requirements.sha256"
REQUIRED_PYTHON_VERSION="3.12"
PYTHON_BIN="${PYTHON_BIN:-}"

# Verifie que les fichiers backend requis existent.
#
# @param {void} Aucun - Utilise les chemins globaux du script.
# @returns {void} Termine le script avec une erreur si un fichier manque.
check_backend_files() {
  if [ ! -d "$BACKEND_DIR" ]; then
    echo "Dossier backend introuvable: ${BACKEND_DIR}" >&2
    exit 1
  fi

  if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Fichier requirements introuvable: ${REQUIREMENTS_FILE}" >&2
    exit 1
  fi

}

# Trouve un interpreteur Python compatible avec la version backend supportee.
#
# @param {void} Aucun - Utilise `PYTHON_BIN`, Homebrew puis le PATH.
# @returns {string} Chemin de l'interpreteur Python 3.12.
find_python_bin() {
  if [ -n "$PYTHON_BIN" ] && [ -x "$PYTHON_BIN" ]; then
    echo "$PYTHON_BIN"
    return
  fi

  for candidate in \
    "/opt/homebrew/opt/python@3.12/bin/python3.12" \
    "/usr/local/opt/python@3.12/bin/python3.12" \
    "python3.12"
  do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return
    fi
  done

  echo "Python ${REQUIRED_PYTHON_VERSION} est requis pour les tests backend." >&2
  echo "Installez-le avec: brew install python@3.12" >&2
  exit 1
}

# Retourne la version majeure.mineure d'un interpreteur Python.
#
# @param {string} $1 - Chemin de l'interpreteur Python.
# @returns {string} Version au format `major.minor`.
get_python_minor_version() {
  "$1" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

# Cree l'environnement virtuel Python s'il n'existe pas encore.
#
# @param {void} Aucun - Utilise Python 3.12 et le chemin global `VENV_DIR`.
# @returns {void} Cree le dossier de virtualenv si necessaire.
ensure_virtualenv() {
  local python_bin
  local python_version
  local venv_version

  python_bin="$(find_python_bin)"
  python_version="$(get_python_minor_version "$python_bin")"
  if [ "$python_version" != "$REQUIRED_PYTHON_VERSION" ]; then
    echo "Version Python invalide: ${python_version}. Version requise: ${REQUIRED_PYTHON_VERSION}." >&2
    exit 1
  fi

  if [ -x "${VENV_DIR}/bin/python" ]; then
    venv_version="$(get_python_minor_version "${VENV_DIR}/bin/python")"
    if [ "$venv_version" != "$REQUIRED_PYTHON_VERSION" ]; then
      echo "Recreation du virtualenv backend en Python ${REQUIRED_PYTHON_VERSION}..."
      rm -rf "$VENV_DIR"
    fi
  fi

  if [ ! -x "${VENV_DIR}/bin/python" ]; then
    echo "Creation du virtualenv backend..."
    "$python_bin" -m venv "$VENV_DIR"
  fi
}

# Calcule l'empreinte sha256 du fichier de dependances.
#
# @param {void} Aucun - Utilise le fichier global `REQUIREMENTS_FILE`.
# @returns {string} Empreinte sha256 de `requirements.txt`.
get_requirements_hash() {
  shasum -a 256 "$REQUIREMENTS_FILE" | awk '{print $1}'
}

# Installe les dependances Python si le virtualenv n'est pas synchronise.
#
# @param {void} Aucun - Compare `requirements.txt` avec l'empreinte stockee.
# @returns {void} Installe les dependances et met a jour l'empreinte si besoin.
ensure_dependencies() {
  local current_hash
  local installed_hash

  current_hash="$(get_requirements_hash)"
  installed_hash=""

  if [ -f "$REQUIREMENTS_STAMP" ]; then
    installed_hash="$(cat "$REQUIREMENTS_STAMP")"
  fi

  if [ "$current_hash" != "$installed_hash" ]; then
    echo "Installation des dependances backend..."
    "${VENV_DIR}/bin/pip" install -r "$REQUIREMENTS_FILE"
    echo "$current_hash" > "$REQUIREMENTS_STAMP"
  else
    echo "Dependances backend deja a jour."
  fi
}

# Lance les tests unitaires backend.
#
# @param {void} Aucun - Execute `unittest discover` depuis le dossier backend.
# @returns {void} Retourne le code de sortie de la suite de tests.
run_backend_tests() {
  echo "Lancement des tests backend..."
  cd "$BACKEND_DIR"
  "${VENV_DIR}/bin/python" -m unittest discover -s tests
}

check_backend_files
ensure_virtualenv
ensure_dependencies
run_backend_tests
