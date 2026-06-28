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
# Description : confirmation de suppression de la cle privee age apres demarrage.

prompt_remove_age_identity_after_start() {
  # Description : propose de supprimer la cle age privee apres un demarrage production reussi.
  # Parametres : $1 chemin de la cle age privee.
  # Retour : void.
  local identity_file="$1"
  local answer=""

  if [ ! -f "$identity_file" ]; then
    return
  fi

  echo ""
  echo "La stack de production est demarree."
  echo "Cle age privee encore presente: ${identity_file}"

  if [ -t 0 ]; then
    read -r -p "Supprimer cette cle de ce serveur maintenant ? [y/N] " answer </dev/tty
  else
    echo "Terminal interactif indisponible: cle age conservee."
    return
  fi

  case "$answer" in
    y | Y | yes | YES | oui | OUI)
      rm -f "$identity_file"
      echo "Cle age supprimee: ${identity_file}"
      ;;
    *)
      echo "Cle age conservee. Gardez-la hors depot et protegez son acces."
      ;;
  esac
}
