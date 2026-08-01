/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-01
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : colonnes de la liste des jeux Bibliotheque selon le profil.
 */

const BASE_LIBRARY_GAME_COLUMNS = ["name", "release_date", "developer", "editor", "platform"];

/**
 * Retourne les colonnes visibles de la liste des jeux Bibliotheque.
 *
 * @param {string} authenticatedProfile - Profil applicatif connecte.
 * @returns {string[]} Colonnes autorisees pour le profil.
 */
function getLibraryGameColumns(authenticatedProfile = "") {
  const normalizedProfile = String(authenticatedProfile || "").trim().toUpperCase();
  return normalizedProfile === "ADMIN"
    ? [...BASE_LIBRARY_GAME_COLUMNS, "status"]
    : [...BASE_LIBRARY_GAME_COLUMNS];
}

/**
 * Retourne les colonnes mobiles visibles selon les colonnes autorisees.
 *
 * @param {string[]} columns - Colonnes autorisees sur desktop.
 * @returns {string[]} Colonnes principales pour mobile.
 */
function getLibraryGameMobileVisibleColumns(columns) {
  return ["name", "release_date"].filter((column) => columns.includes(column));
}

export { getLibraryGameColumns, getLibraryGameMobileVisibleColumns };
