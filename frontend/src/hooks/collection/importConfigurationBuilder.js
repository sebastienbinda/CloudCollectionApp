/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-27
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : construction frontend de la description d'import de collection.
 */

import { hasSpreadsheetImportColumn } from "./importGlobalOptionsVisibility.js";
import { applyDataRangeDefaults } from "./importSpreadsheetColumnTools.js";
import {
  buildCsvImportConfigurationDescription,
  buildFrontendCsvConfiguration,
  createDefaultCsvMapping,
} from "./csvImportConfigurationBuilder.js";
import {
  OPTIONAL_FIELDS,
  PRIVATE_INFORMATION_FIELDS,
  REQUIRED_FIELDS,
  SHEET_INFORMATION,
  collectionColumnFields,
  collectionRequiredFields,
  wishlistSheetColumnFields,
} from "./importSpreadsheetFieldDefinitions.js";

/**
 * Construit un layout d'import par defaut.
 *
 * @param {boolean} includePlatformColumn - Indique si la plateforme est portee par une colonne.
 * @returns {Object} Layout formulaire initial.
 */
function createDefaultLayout(includePlatformColumn = true) {
  return {
    dataRange: "A1:D200",
    headerRow: "1",
    columns: {
      name: "A",
      platform: includePlatformColumn ? "B" : "",
      studio: includePlatformColumn ? "C" : "B",
      release_date: includePlatformColumn ? "D" : "C",
      ...Object.fromEntries(PRIVATE_INFORMATION_FIELDS.map((field) => [field, ""])),
    },
  };
}

/**
 * Construit l'etat initial du formulaire de configuration.
 *
 * @returns {Object} Etat frontend initial de configuration.
 */
function createDefaultImportConfiguration() {
  return {
    fileType: "libreoffice_ods",
    priceUnit: "EUR",
    ratingBase: "10",
    csvMapping: createDefaultCsvMapping(),
    multipleSheets: false,
    sharedLayout: true,
    sheetInformation: SHEET_INFORMATION,
    wishlist: {
      mode: "none",
      sheetName: "",
      layout: createDefaultLayout(true),
    },
    singleSheetLayout: createDefaultLayout(true),
    sharedSheetLayout: {
      ...createDefaultLayout(false),
      sheetSelectionMode: "all",
      includedSheets: "",
      excludedSheets: "",
    },
    sheets: [
      {
        sheetName: "",
        sheetInformation: SHEET_INFORMATION,
        layout: createDefaultLayout(false),
      },
    ],
  };
}

/**
 * Convertit une description backend sauvegardee en etat de formulaire.
 *
 * @param {Object} description - Description d'import retournee par le backend.
 * @returns {Object} Etat frontend de configuration d'import.
 */
function createImportConfigurationFromDescription(description) {
  const defaultConfiguration = createDefaultImportConfiguration();
  if (!description || typeof description !== "object") {
    return defaultConfiguration;
  }

  const wishlist = buildFrontendWishlistConfiguration(
    description.wishlist,
    defaultConfiguration.wishlist
  );
  if (description.file_type === "csv") {
    return buildFrontendCsvConfiguration(description, defaultConfiguration, wishlist);
  }
  if (description.single_sheet_conf) {
    return {
      ...defaultConfiguration,
      fileType: description.file_type || defaultConfiguration.fileType,
      priceUnit: description.price_unit || defaultConfiguration.priceUnit,
      ratingBase: String(description.rating_base || defaultConfiguration.ratingBase),
      multipleSheets: false,
      wishlist,
      singleSheetLayout: buildFrontendLayout(
        description.single_sheet_conf,
        defaultConfiguration.singleSheetLayout
      ),
    };
  }

  const multipleSheetsConfiguration = description.multiple_sheets_conf || {};
  if (multipleSheetsConfiguration.shared_layout) {
    return {
      ...defaultConfiguration,
      fileType: description.file_type || defaultConfiguration.fileType,
      priceUnit: description.price_unit || defaultConfiguration.priceUnit,
      ratingBase: String(description.rating_base || defaultConfiguration.ratingBase),
      multipleSheets: true,
      sharedLayout: true,
      sheetInformation: multipleSheetsConfiguration.sheet_information || "",
      wishlist,
      sharedSheetLayout: buildFrontendSharedLayout(
        multipleSheetsConfiguration.shared_layout,
        defaultConfiguration.sharedSheetLayout
      ),
    };
  }

  const sheets = Array.isArray(multipleSheetsConfiguration.sheets)
    ? multipleSheetsConfiguration.sheets
    : [];
  if (sheets.length) {
    return {
      ...defaultConfiguration,
      fileType: description.file_type || defaultConfiguration.fileType,
      priceUnit: description.price_unit || defaultConfiguration.priceUnit,
      ratingBase: String(description.rating_base || defaultConfiguration.ratingBase),
      multipleSheets: true,
      sharedLayout: false,
      sheetInformation: multipleSheetsConfiguration.sheet_information || sheets[0]?.sheet_information || "",
      wishlist,
      sheets: sheets.map((sheet) => ({
        sheetName: sheet.sheet_name || "",
        sheetInformation: sheet.sheet_information || "",
        layout: buildFrontendLayout(sheet, defaultConfiguration.sheets[0].layout),
      })),
    };
  }

  return {
    ...defaultConfiguration,
    fileType: description.file_type || defaultConfiguration.fileType,
    priceUnit: description.price_unit || defaultConfiguration.priceUnit,
    ratingBase: String(description.rating_base || defaultConfiguration.ratingBase),
    wishlist,
  };
}

/**
 * Convertit la configuration wishlist backend en etat de formulaire.
 *
 * @param {Object} wishlistDescription - Description wishlist backend.
 * @param {Object} defaultWishlist - Valeurs frontend par defaut.
 * @returns {Object} Configuration wishlist frontend.
 */
function buildFrontendWishlistConfiguration(wishlistDescription, defaultWishlist) {
  const mode = wishlistDescription?.mode || "none";
  if (mode !== "sheet") {
    return {
      ...defaultWishlist,
      mode,
    };
  }
  return {
    ...defaultWishlist,
    mode,
    sheetName: wishlistDescription.sheet_name || "",
    layout: buildFrontendLayout(wishlistDescription, defaultWishlist.layout),
  };
}

/**
 * Convertit un layout backend en layout de formulaire.
 *
 * @param {Object} layoutDescription - Layout backend.
 * @param {Object} defaultLayout - Layout frontend de secours.
 * @returns {Object} Layout frontend.
 */
function buildFrontendLayout(layoutDescription, defaultLayout) {
  const columnInformation = layoutDescription?.column_information || {};
  return {
    ...defaultLayout,
    dataRange: layoutDescription?.data_range || defaultLayout.dataRange,
    headerRow: String(layoutDescription?.header_row || defaultLayout.headerRow),
    columns: {
      ...defaultLayout.columns,
      ...Object.fromEntries(
        Object.entries(columnInformation).map(([fieldName, columnName]) => [
          fieldName,
          String(columnName || "").toUpperCase(),
        ])
      ),
    },
  };
}

/**
 * Convertit un layout partage backend en layout partage de formulaire.
 *
 * @param {Object} layoutDescription - Layout partage backend.
 * @param {Object} defaultLayout - Layout partage frontend de secours.
 * @returns {Object} Layout partage frontend.
 */
function buildFrontendSharedLayout(layoutDescription, defaultLayout) {
  const baseLayout = buildFrontendLayout(layoutDescription, defaultLayout);
  if (Array.isArray(layoutDescription.excluded_sheets)) {
    return {
      ...baseLayout,
      sheetSelectionMode: "excluded",
      excludedSheets: layoutDescription.excluded_sheets,
      includedSheets: "",
    };
  }
  if (!Array.isArray(layoutDescription.included_sheets)) {
    return {
      ...baseLayout,
      sheetSelectionMode: "all",
      includedSheets: "",
      excludedSheets: "",
    };
  }
  return {
    ...baseLayout,
    sheetSelectionMode: "included",
    includedSheets: layoutDescription.included_sheets,
    excludedSheets: "",
  };
}

/**
 * Construit la description JSON attendue par le backend.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @returns {{description: Object|null, errors: string[]}} Description ou erreurs UX.
 */
function buildImportConfigurationDescription(configuration) {
  const errors = [];
  if (configuration.fileType === "csv") {
    return buildCsvImportConfigurationDescription(configuration);
  }
  const fileType = normalizeSpreadsheetFileType(configuration.fileType);
  const wishlist = buildWishlistConfiguration(configuration, errors);
  const ratingBase = buildRatingBase(configuration, errors);
  if (!configuration.multipleSheets) {
    const layout = buildLayout(
      configuration.singleSheetLayout,
      collectionRequiredFields(configuration, true),
      errors
    );
    return {
      description: errors.length ? null : {
        file_type: fileType,
        price_unit: configuration.priceUnit,
        rating_base: ratingBase,
        wishlist,
        single_sheet_conf: layout,
      },
      errors,
    };
  }
  if (configuration.sharedLayout) {
    const requiredFields = collectionRequiredFields(
      configuration,
      configuration.sheetInformation !== SHEET_INFORMATION
    );
    const layout = buildLayout(configuration.sharedSheetLayout, requiredFields, errors);
    const selectionMode = configuration.sharedSheetLayout.sheetSelectionMode;
    if (selectionMode === "excluded") {
      const excludedSheets = splitSheetNames(configuration.sharedSheetLayout.excludedSheets);
      if (excludedSheets.length) {
        layout.excluded_sheets = excludedSheets;
      }
    } else if (selectionMode === "included") {
      const includedSheets = splitSheetNames(configuration.sharedSheetLayout.includedSheets);
      if (includedSheets.length) {
        layout.included_sheets = includedSheets;
      }
    }
    const multipleSheetsConf = { shared_layout: layout };
    if (configuration.sheetInformation) {
      multipleSheetsConf.sheet_information = configuration.sheetInformation;
    }
    return {
      description: errors.length ? null : {
        file_type: fileType,
        price_unit: configuration.priceUnit,
        rating_base: ratingBase,
        wishlist,
        multiple_sheets_conf: multipleSheetsConf,
      },
      errors,
    };
  }
  const sheets = configuration.sheets.map((sheet, index) => {
    const sheetName = String(sheet.sheetName || "").trim();
    if (!sheetName) {
      errors.push(`Renseignez le nom de l'onglet ${index + 1}.`);
    }
    const requiredFields = collectionRequiredFields(
      configuration,
      configuration.sheetInformation !== SHEET_INFORMATION
    );
    const sheetDescription = {
      sheet_name: sheetName,
      ...buildLayout(sheet.layout, requiredFields, errors),
    };
    if (configuration.sheetInformation) {
      sheetDescription.sheet_information = configuration.sheetInformation;
    }
    return sheetDescription;
  });
  return {
    description: errors.length ? null : {
      file_type: fileType,
      price_unit: configuration.priceUnit,
      rating_base: ratingBase,
      wishlist,
      multiple_sheets_conf: { sheets },
    },
    errors,
  };
}

/**
 * Indique si la configuration courante peut etre soumise au backend.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @returns {boolean} Vrai quand les champs obligatoires sont remplis.
 */
function canSubmitImportConfiguration(configuration) {
  const { description, errors } = buildImportConfigurationDescription(configuration);
  return Boolean(description) && errors.length === 0;
}

/**
 * Normalise le type de fichier tableur pour la description backend.
 *
 * @param {string} fileType - Type selectionne dans le formulaire.
 * @returns {string} Type backend tableur reconnu.
 */
function normalizeSpreadsheetFileType(fileType) {
  return fileType === "excel_xlsx" ? "excel_xlsx" : "libreoffice_ods";
}

/**
 * Construit la base globale de notation.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @param {string[]} errors - Erreurs UX a enrichir.
 * @returns {number} Base de notation.
 */
function buildRatingBase(configuration, errors) {
  if (!hasSpreadsheetImportColumn(configuration, "grade")) return 10;
  const ratingBase = Number.parseInt(configuration.ratingBase, 10);
  if (!Number.isInteger(ratingBase) || ratingBase <= 0) {
    errors.push("Renseignez une base de notation valide.");
    return 10;
  }
  return ratingBase;
}

/**
 * Construit la section wishlist du contrat backend.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @param {string[]} errors - Erreurs UX a enrichir.
 * @returns {Object} Configuration wishlist serialisable.
 */
function buildWishlistConfiguration(configuration, errors) {
  const mode = configuration.wishlist?.mode || "none";
  if (mode === "none" || mode === "column") {
    return { mode };
  }
  if (mode !== "sheet") {
    errors.push("Sélectionnez un mode de liste de souhaits valide.");
    return { mode: "none" };
  }
  const sheetName = String(configuration.wishlist.sheetName || "").trim();
  if (!sheetName) {
    errors.push("Renseignez l'onglet de liste de souhaits.");
  }
  return {
    mode,
    sheet_name: sheetName,
    ...buildLayout(configuration.wishlist.layout, REQUIRED_FIELDS, errors),
  };
}

/**
 * Construit un layout JSON depuis un layout formulaire.
 *
 * @param {Object} layout - Layout formulaire.
 * @param {string[]} requiredFields - Champs requis dans `column_information`.
 * @param {string[]} errors - Erreurs UX a enrichir.
 * @returns {Object} Layout conforme au contrat backend.
 */
function buildLayout(layout, requiredFields, errors) {
  const dataRange = String(layout.dataRange || "").trim().toUpperCase();
  const headerRow = Number.parseInt(layout.headerRow, 10);
  if (!dataRange) {
    errors.push("Renseignez la plage de données.");
  }
  if (!Number.isInteger(headerRow) || headerRow < 1) {
    errors.push("Renseignez une ligne d'en-tête valide.");
  }
  const columnInformation = {};
  requiredFields.forEach((field) => {
    const column = String(layout.columns?.[field] || "").trim().toUpperCase();
    if (!column) {
      errors.push(`Renseignez la colonne ${field}.`);
      return;
    }
    columnInformation[field] = column;
  });
  OPTIONAL_FIELDS.forEach((field) => {
    const column = String(layout.columns?.[field] || "").trim().toUpperCase();
    if (column) {
      columnInformation[field] = column;
    }
  });
  return {
    data_range: dataRange,
    header_row: Number.isInteger(headerRow) ? headerRow : 1,
    column_information: columnInformation,
  };
}

/**
 * Decoupe une saisie d'onglets optionnels.
 *
 * @param {string} value - Saisie utilisateur separee par virgules ou retours ligne.
 * @returns {string[]} Noms d'onglets non vides.
 */
function splitSheetNames(value) {
  if (Array.isArray(value)) {
    return value.map((sheetName) => String(sheetName).trim()).filter(Boolean);
  }
  return String(value || "")
    .split(/[\n,]/)
    .map((sheetName) => sheetName.trim())
    .filter(Boolean);
}

export {
  OPTIONAL_FIELDS,
  REQUIRED_FIELDS,
  applyDataRangeDefaults,
  collectionColumnFields,
  collectionRequiredFields,
  createImportConfigurationFromDescription,
  createDefaultImportConfiguration,
  canSubmitImportConfiguration,
  buildImportConfigurationDescription,
  wishlistSheetColumnFields,
};
