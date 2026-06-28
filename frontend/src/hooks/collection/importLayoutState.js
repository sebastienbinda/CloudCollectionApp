/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : mutations de layout frontend pour l'import de collection.
 */

import { applyDataRangeDefaults } from "./importSpreadsheetColumnTools.js";

/**
 * Met a jour un layout et applique les colonnes deduites si la plage change.
 *
 * @param {Object} layout - Layout courant.
 * @param {string} fieldName - Champ modifie.
 * @param {string} value - Nouvelle valeur.
 * @param {string[]} columnFields - Champs colonnes a pre-remplir.
 * @returns {Object} Layout mis a jour.
 */
function updatedLayoutValue(layout, fieldName, value, columnFields) {
  if (fieldName === "dataRange") {
    return applyDataRangeDefaults(layout, value, columnFields);
  }
  return {
    ...layout,
    [fieldName]: value,
  };
}

export default updatedLayoutValue;
