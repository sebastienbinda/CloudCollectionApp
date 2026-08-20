/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-20
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : definitions des champs tableur configurables pour l'import.
 */

const REQUIRED_FIELDS = Object.freeze(["name", "platform"]);
const REFERENCE_OPTIONAL_FIELDS = Object.freeze(["studio", "release_date"]);
const PRIVATE_INFORMATION_FIELDS = Object.freeze([
  "purchase_price", "buy_location", "buy_date", "grade", "condition",
  "has_manual", "is_collector", "has_steelbook", "is_digital", "region", "description",
]);
const OPTIONAL_FIELDS = Object.freeze([
  ...REFERENCE_OPTIONAL_FIELDS,
  ...PRIVATE_INFORMATION_FIELDS,
]);
const SHEET_INFORMATION = "platform";

/**
 * Retourne les champs requis pour les layouts collection.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @param {boolean} includePlatformColumn - Indique si le layout porte la plateforme.
 * @returns {string[]} Champs requis dans `column_information`.
 */
function collectionRequiredFields(configuration, includePlatformColumn) {
  const fields = includePlatformColumn
    ? [...REQUIRED_FIELDS]
    : REQUIRED_FIELDS.filter((field) => field !== SHEET_INFORMATION);
  if (configuration.wishlist.mode === "column") {
    fields.push("wishlist");
  }
  return fields;
}

/**
 * Retourne les champs colonne a afficher pour un layout de collection ODS.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @param {boolean} includePlatformColumn - Indique si la plateforme est une colonne.
 * @returns {string[]} Champs colonnes configurables.
 */
function collectionColumnFields(configuration, includePlatformColumn) {
  const mustIncludePlatformColumn = includePlatformColumn
    || configuration.sheetInformation !== SHEET_INFORMATION;
  const fields = mustIncludePlatformColumn
    ? [...REQUIRED_FIELDS, ...REFERENCE_OPTIONAL_FIELDS]
    : [
      ...REQUIRED_FIELDS.filter((field) => field !== SHEET_INFORMATION),
      ...REFERENCE_OPTIONAL_FIELDS,
    ];
  if (configuration.wishlist.mode === "column") {
    fields.push("wishlist");
  }
  fields.push(...PRIVATE_INFORMATION_FIELDS);
  return fields;
}

/**
 * Retourne les champs colonne a afficher pour l'onglet wishlist dedie.
 *
 * @returns {string[]} Champs wishlist configurables.
 */
function wishlistSheetColumnFields() {
  return [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS];
}

export {
  OPTIONAL_FIELDS,
  PRIVATE_INFORMATION_FIELDS,
  REQUIRED_FIELDS,
  SHEET_INFORMATION,
  collectionColumnFields,
  collectionRequiredFields,
  wishlistSheetColumnFields,
};
