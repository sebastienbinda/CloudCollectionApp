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
# Description : utilitaire de test du score de matching utilise par l'import.

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
  scripts/matching_score.sh [--text] [--normalize] <nom_1> <nom_2>

Options:
  --text       Utilise le score texte generique au lieu du score metier jeu.
  --normalize  Normalise les deux valeurs avant le score texte generique.
               Le score metier jeu normalise toujours comme l'import.

Exemples:
  scripts/matching_score.sh "Final X" "Final X-2"
  scripts/matching_score.sh "legend of zelda" "the legend of zelda"
  scripts/matching_score.sh --text --normalize "  École du Jeu  " "ecole du jeu"
USAGE
}

normalize_values="false"
score_mode="game"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  show_usage
  exit 0
fi

while [ "$#" -gt 0 ]; do
  case "${1:-}" in
    --text)
      score_mode="text"
      shift
      ;;
    --normalize)
      normalize_values="true"
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -ne 2 ]; then
  show_usage >&2
  exit 1
fi

"$PYTHON_BIN" - "$BACKEND_DIR" "$score_mode" "$normalize_values" "$1" "$2" <<'PY'
import sys
import unicodedata
from pathlib import Path

backend_dir = Path(sys.argv[1])
matching_dir = backend_dir / "services" / "matching"
sys.path.insert(0, str(matching_dir))
score_mode = sys.argv[2]
normalize_values = sys.argv[3] == "true"
first_value = sys.argv[4]
second_value = sys.argv[5]


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
    matching_dir / "string_similarity.py",
)

if score_mode == "game":
    first_key = comparison_key(first_value)
    second_key = comparison_key(second_value)
    result = matching_module.explain_game_name_matching(first_key, second_key)
    score = result.score
    decision = result.decision.value
    rule = result.rule
    reason = result.reason
elif normalize_values:
    first_key = comparison_key(first_value)
    second_key = comparison_key(second_value)
    score = matching_module.matching_score(first_key, second_key)
    decision = "scored"
    rule = "text_similarity"
    reason = "Score de similarite textuelle generique."
else:
    first_key = first_value
    second_key = second_value
    score = matching_module.matching_score(first_key, second_key)
    decision = "scored"
    rule = "text_similarity"
    reason = "Score de similarite textuelle generique."

print(f"mode={score_mode}")
print(f"cle_1={first_key}")
print(f"cle_2={second_key}")
print(f"score={score}")
print(f"decision={decision}")
print(f"rule={rule}")
print(f"reason={reason}")
PY
