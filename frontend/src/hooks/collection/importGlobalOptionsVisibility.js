/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : regles de visibilite des options globales d'import.
 */

/**
 * Indique si une colonne donnee est configuree dans un layout.
 *
 * @param {Object} layout - Layout de formulaire.
 * @param {string} fieldName - Nom de colonne recherche.
 * @returns {boolean} Vrai si le champ contient une colonne.
 * @throws {void} Ne leve pas d'exception.
 */
function hasLayoutColumn(layout, fieldName) {
  return Boolean(String(layout?.columns?.[fieldName] || "").trim());
}

/**
 * Indique si une colonne est configuree dans au moins un layout tableur actif.
 *
 * @param {Object} configuration - Configuration d'import tableur.
 * @param {string} fieldName - Nom de colonne recherche.
 * @returns {boolean} Vrai si la colonne est configuree.
 * @throws {void} Ne leve pas d'exception.
 */
function hasSpreadsheetImportColumn(configuration, fieldName) {
  if (
    configuration.wishlist?.mode === "sheet" &&
    hasLayoutColumn(configuration.wishlist?.layout, fieldName)
  ) {
    return true;
  }
  if (!configuration.multipleSheets) {
    return hasLayoutColumn(configuration.singleSheetLayout, fieldName);
  }
  if (configuration.sharedLayout) {
    return hasLayoutColumn(configuration.sharedSheetLayout, fieldName);
  }
  return (configuration.sheets || []).some((sheet) => hasLayoutColumn(sheet.layout, fieldName));
}

/**
 * Indique si une colonne CSV est mappee.
 *
 * @param {Object} configuration - Configuration d'import CSV.
 * @param {string} fieldName - Nom de colonne recherche.
 * @returns {boolean} Vrai si le mapping CSV contient une colonne.
 * @throws {void} Ne leve pas d'exception.
 */
function hasCsvImportColumn(configuration, fieldName) {
  return Boolean(String(configuration.csvMapping?.[fieldName] || "").trim());
}

export {
  hasCsvImportColumn,
  hasSpreadsheetImportColumn,
};
