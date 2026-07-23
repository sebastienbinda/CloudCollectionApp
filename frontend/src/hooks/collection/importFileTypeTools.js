/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : utilitaires frontend des types de fichiers d'import.
 */

/**
 * Normalise le type de fichier d'import pour comparer deux configurations.
 *
 * @param {string} fileType - Type de fichier brut.
 * @returns {string} Type reconnu par le frontend.
 * @throws {void} Ne leve pas d'exception.
 */
function normalizeImportFileType(fileType) {
  const normalizedFileType = String(fileType || "").trim();
  return normalizedFileType || "libreoffice_ods";
}

/**
 * Deduit le type d'import a partir du fichier choisi, avec repli sur le formulaire.
 *
 * @param {File} collectionFile - Fichier selectionne par l'utilisateur.
 * @param {string} selectedFileType - Type actuellement selectionne dans le formulaire.
 * @returns {string} Type d'import a utiliser pour l'upload et l'analyse.
 * @throws {void} Ne leve pas d'exception.
 */
function resolveImportFileType(collectionFile, selectedFileType) {
  const filename = String(collectionFile?.name || "").trim().toLowerCase();
  if (filename.endsWith(".xlsx")) {
    return "excel_xlsx";
  }
  if (filename.endsWith(".csv")) {
    return "csv";
  }
  if (filename.endsWith(".ods")) {
    return "libreoffice_ods";
  }
  return normalizeImportFileType(selectedFileType);
}

/**
 * Construit le message de refus d'une configuration sauvegardee incompatible.
 *
 * @param {string} savedFileType - Format de la configuration sauvegardee.
 * @param {string} selectedFileType - Format du fichier en cours.
 * @returns {string} Message affiche a l'utilisateur.
 * @throws {void} Ne leve pas d'exception.
 */
function buildIncompatibleSavedConfigurationMessage(savedFileType, selectedFileType) {
  return (
    "La configuration d'import sauvegardee est au format " +
    `${formatImportFileType(savedFileType)} et ne peut pas etre reutilisee ` +
    `avec un fichier ${formatImportFileType(selectedFileType)}. ` +
    "Renseignez une nouvelle configuration pour ce fichier."
  );
}

/**
 * Retourne un libelle lisible pour un type de fichier d'import.
 *
 * @param {string} fileType - Type technique de fichier.
 * @returns {string} Libelle utilisateur.
 * @throws {void} Ne leve pas d'exception.
 */
function formatImportFileType(fileType) {
  if (fileType === "csv") {
    return "CSV";
  }
  if (fileType === "excel_xlsx") {
    return "Excel";
  }
  return "LibreOffice ODS";
}

export {
  buildIncompatibleSavedConfigurationMessage,
  formatImportFileType,
  normalizeImportFileType,
  resolveImportFileType,
};
