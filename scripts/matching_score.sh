#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : utilitaire de test du score de similarite utilise par l'import.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# Affiche l'aide de l'utilitaire.
#
# @param {void} Aucun.
# @returns {void} Ecrit l'aide sur la sortie standard.
show_usage() {
  cat <<'USAGE'
Usage:
  scripts/matching_score.sh [--normalize] <cle_1> <cle_2>

Options:
  --normalize  Normalise les deux valeurs comme l'import avant de calculer le score.

Exemples:
  scripts/matching_score.sh "legend of zelda" "the legend of zelda"
  scripts/matching_score.sh --normalize "  École du Jeu  " "ecole du jeu"
USAGE
}

normalize_values="false"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  show_usage
  exit 0
fi

if [ "${1:-}" = "--normalize" ]; then
  normalize_values="true"
  shift
fi

if [ "$#" -ne 2 ]; then
  show_usage >&2
  exit 1
fi

"$PYTHON_BIN" - "$BACKEND_DIR" "$normalize_values" "$1" "$2" <<'PY'
import sys
import unicodedata
from pathlib import Path

backend_dir = Path(sys.argv[1])
normalize_values = sys.argv[2] == "true"
first_value = sys.argv[3]
second_value = sys.argv[4]


def load_matching_module(module_path: Path):
    import importlib.util

    specification = importlib.util.spec_from_file_location(
        "cloudcollection_matching_score",
        module_path,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Module introuvable: {module_path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def comparison_key(value: str) -> str:
    normalized_value = unicodedata.normalize("NFD", value.strip().lower())
    return "".join(
        character for character in normalized_value
        if unicodedata.category(character) != "Mn"
    )


matching_module = load_matching_module(
    backend_dir / "services" / "matching" / "string_similarity.py",
)

if normalize_values:
    first_key = comparison_key(first_value)
    second_key = comparison_key(second_value)
else:
    first_key = first_value
    second_key = second_value

score = matching_module.matching_score(first_key, second_key)
print(f"cle_1={first_key}")
print(f"cle_2={second_key}")
print(f"score={score}")
PY
