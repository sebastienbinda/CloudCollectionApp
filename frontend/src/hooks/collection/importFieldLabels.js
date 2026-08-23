/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : libelles centralises des champs configurables d'import.
 */

const IMPORT_FIELD_LABELS = Object.freeze({
  name: "Nom du jeu",
  platform: "Plateforme",
  studio: "Studio",
  release_date: "Date de sortie",
  wishlist: "Liste de souhaits",
  purchase_price: "Prix d'achat",
  buy_location: "Lieu d'achat",
  buy_date: "Date d'achat",
  grade: "Note",
  condition: "État",
  has_manual: "Notice",
  is_collector: "Collector",
  has_steelbook: "Steelbook",
  is_digital: "Version dématérialisée",
  region: "Région",
  description: "Description",
});

/**
 * Retourne le libelle utilisateur d'un champ d'import.
 *
 * @param {string} fieldName - Nom technique du champ d'import.
 * @returns {string} Libelle affiche dans la configuration et les resumes.
 * @throws {void} Ne leve pas d'exception.
 */
function getImportFieldLabel(fieldName) {
  return IMPORT_FIELD_LABELS[fieldName] || fieldName || "";
}

export { IMPORT_FIELD_LABELS, getImportFieldLabel };
