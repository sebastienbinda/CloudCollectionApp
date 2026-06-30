#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-29
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : fonctions de detection Docker userns-remap pour le runtime.

docker_userns_remap_enabled() {
  # Description : indique si le daemon Docker annonce userns-remap.
  # Parametres : aucun.
  # Retour : 0 si userns-remap est actif, 1 sinon.
  if ! command -v docker >/dev/null 2>&1; then
    return 1
  fi

  docker info --format '{{range .SecurityOptions}}{{println .}}{{end}}' 2>/dev/null | grep -Eq '(^|=)userns($|,)'
}

configured_userns_remap_user() {
  # Description : retourne l'utilisateur hote configure pour userns-remap.
  # Parametres : aucun.
  # Retour : ecrit le nom utilisateur, ou rien si non determine.
  local daemon_config="/etc/docker/daemon.json"
  local configured_value

  if [ -r "$daemon_config" ]; then
    configured_value="$(sed -n 's/.*"userns-remap"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$daemon_config" | head -n 1)"
    configured_value="${configured_value%%:*}"
    if [ "$configured_value" = "default" ]; then
      printf '%s\n' "dockremap"
      return
    fi
    if [ -n "$configured_value" ]; then
      printf '%s\n' "$configured_value"
      return
    fi
  fi

  if grep -q '^dockremap:' /etc/subuid 2>/dev/null; then
    printf '%s\n' "dockremap"
  fi
}

subordinate_range_start() {
  # Description : retourne le debut de plage subordinate pour un utilisateur.
  # Parametres : $1 fichier /etc/subuid ou /etc/subgid, $2 utilisateur.
  # Retour : ecrit le premier identifiant hote de la plage, ou rien.
  local range_file="$1"
  local range_user="$2"

  awk -F: -v user="$range_user" '$1 == user { print $2; exit }' "$range_file" 2>/dev/null
}

validate_userns_remap_directory_owners() {
  # Description : verifie que les proprietaires hotes configures correspondent au remap Docker.
  # Parametres : aucun.
  # Retour : void.
  local remap_user
  local subuid_start
  local subgid_start
  local expected_runtime_host_uid
  local expected_runtime_host_gid

  if [ "$DEPLOY_ENV" != "online" ] || ! docker_userns_remap_enabled; then
    return
  fi

  remap_user="$(configured_userns_remap_user)"
  if [ -z "$remap_user" ]; then
    echo "Docker userns-remap est actif, mais l'utilisateur de remap n'a pas pu etre determine."
    echo "Verifiez /etc/docker/daemon.json, /etc/subuid et /etc/subgid, puis renseignez RUNTIME_HOST_UID/GID et POSTGRES_HOST_ROOT_UID/GID."
    return
  fi

  subuid_start="$(subordinate_range_start /etc/subuid "$remap_user")"
  subgid_start="$(subordinate_range_start /etc/subgid "$remap_user")"
  if [ -z "$subuid_start" ] || [ -z "$subgid_start" ]; then
    echo "Docker userns-remap est actif pour ${remap_user}, mais les plages /etc/subuid ou /etc/subgid sont introuvables."
    echo "Renseignez manuellement RUNTIME_HOST_UID/GID et POSTGRES_HOST_ROOT_UID/GID avec les identifiants hotes remappes."
    return
  fi

  expected_runtime_host_uid=$((subuid_start + RUNTIME_UID))
  expected_runtime_host_gid=$((subgid_start + RUNTIME_GID))

  if [ "$RUNTIME_HOST_UID" != "$expected_runtime_host_uid" ] || [ "$RUNTIME_HOST_GID" != "$expected_runtime_host_gid" ]; then
    echo "Configuration userns-remap incoherente pour les repertoires backend."
    echo "Docker remappe l'utilisateur conteneur ${RUNTIME_UID}:${RUNTIME_GID} vers l'hote ${expected_runtime_host_uid}:${expected_runtime_host_gid}."
    echo "Valeurs actuelles: RUNTIME_HOST_UID=${RUNTIME_HOST_UID}, RUNTIME_HOST_GID=${RUNTIME_HOST_GID}."
    echo "Corrigez runtime/.env avec RUNTIME_HOST_UID=${expected_runtime_host_uid} et RUNTIME_HOST_GID=${expected_runtime_host_gid}."
    exit 1
  fi

  if [ "$POSTGRES_HOST_ROOT_UID" != "$subuid_start" ] || [ "$POSTGRES_HOST_ROOT_GID" != "$subgid_start" ]; then
    echo "Configuration userns-remap incoherente pour PostgreSQL."
    echo "Docker remappe le root conteneur vers l'hote ${subuid_start}:${subgid_start}."
    echo "Valeurs actuelles: POSTGRES_HOST_ROOT_UID=${POSTGRES_HOST_ROOT_UID}, POSTGRES_HOST_ROOT_GID=${POSTGRES_HOST_ROOT_GID}."
    echo "Corrigez runtime/.env avec POSTGRES_HOST_ROOT_UID=${subuid_start} et POSTGRES_HOST_ROOT_GID=${subgid_start}."
    exit 1
  fi
}
