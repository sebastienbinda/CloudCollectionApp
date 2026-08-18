/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-18
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : selection des onglets de collection pour l'import utilisateur.
 */

/**
 * Decoupe une saisie d'onglets libre.
 *
 * @param {string|string[]} value - Valeur source.
 * @returns {string[]} Noms d'onglets non vides.
 * @throws {void} Ne leve pas d'exception.
 */
function splitImportSheetNames(value) {
  if (Array.isArray(value)) {
    return value.map((sheetName) => String(sheetName).trim()).filter(Boolean);
  }
  return String(value || "")
    .split(/[\n,]/)
    .map((sheetName) => sheetName.trim())
    .filter(Boolean);
}

/**
 * Déduit les onglets de collection depuis le mode inclus/exclus.
 *
 * @param {string[]} availableSheetNames - Onglets détectés dans le fichier.
 * @param {Object} sharedSheetLayout - Configuration de sélection d'onglets.
 * @returns {string[]} Onglets contenant les jeux de collection.
 * @throws {void} Ne leve pas d'exception.
 */
function resolveCollectionSheetNames(availableSheetNames, sharedSheetLayout) {
  const detectedSheetNames = Array.isArray(availableSheetNames) ? availableSheetNames : [];
  if (sharedSheetLayout?.sheetSelectionMode === "excluded") {
    const excludedSheets = new Set(splitImportSheetNames(sharedSheetLayout.excludedSheets));
    return detectedSheetNames.filter((sheetName) => !excludedSheets.has(sheetName));
  }
  return splitImportSheetNames(sharedSheetLayout?.includedSheets);
}

/**
 * Synchronise les configurations par onglet avec la selection d'onglets de collection.
 *
 * @param {Object} configuration - Configuration courante.
 * @param {string[]} availableSheetNames - Onglets detectes dans le fichier.
 * @param {Object} defaultSheetConfiguration - Configuration par defaut d'un onglet.
 * @returns {Object} Configuration avec onglets par feuille synchronises.
 * @throws {void} Ne leve pas d'exception.
 */
function synchronizePerSheetConfigurations(
  configuration,
  availableSheetNames,
  defaultSheetConfiguration
) {
  const sheetNames = resolveCollectionSheetNames(
    availableSheetNames,
    configuration.sharedSheetLayout
  );
  if (!sheetNames.length) {
    return configuration;
  }
  const existingSheetsByName = new Map(
    configuration.sheets.map((sheet) => [String(sheet.sheetName || ""), sheet])
  );
  return {
    ...configuration,
    sheets: sheetNames.map((sheetName) => ({
      ...defaultSheetConfiguration,
      ...existingSheetsByName.get(sheetName),
      sheetName,
    })),
  };
}

export {
  resolveCollectionSheetNames,
  splitImportSheetNames,
  synchronizePerSheetConfigurations,
};
