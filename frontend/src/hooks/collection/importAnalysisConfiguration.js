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
 * Description : preconfiguration frontend apres analyse d'un fichier d'import.
 */

import { normalizeImportFileType } from "./importFileTypeTools";

/**
 * Construit la configuration d'import apres analyse des onglets ou colonnes.
 *
 * @param {Object} currentConfiguration - Configuration courante du formulaire.
 * @param {string[]} sheetNames - Onglets ou colonnes detectes par le backend.
 * @param {string} analyzedFileType - Type de fichier analyse.
 * @returns {Object} Nouvelle configuration frontend.
 * @throws {void} Ne leve pas d'exception.
 */
function buildImportConfigurationAfterAnalysis(
  currentConfiguration,
  sheetNames,
  analyzedFileType
) {
  const fileType = normalizeImportFileType(analyzedFileType || currentConfiguration.fileType);
  if (fileType === "csv") {
    return {
      ...currentConfiguration,
      fileType,
      multipleSheets: false,
    };
  }
  if (sheetNames.length <= 1) {
    return {
      ...currentConfiguration,
      fileType,
      multipleSheets: false,
      sharedSheetLayout: {
        ...currentConfiguration.sharedSheetLayout,
        includedSheets: "",
        excludedSheets: "",
      },
    };
  }
  return {
    ...currentConfiguration,
    fileType,
    multipleSheets: true,
    sharedLayout: true,
    sharedSheetLayout: {
      ...currentConfiguration.sharedSheetLayout,
      sheetSelectionMode: "included",
      includedSheets: sheetNames,
      excludedSheets: [],
    },
  };
}

export default buildImportConfigurationAfterAnalysis;
