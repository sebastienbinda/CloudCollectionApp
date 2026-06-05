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

const REQUIRED_FIELDS = Object.freeze(["name", "platform", "studio", "release_date"]);
const SHEET_INFORMATION = "platform";

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
      sheetSelectionMode: "included",
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
 * Construit la description JSON attendue par le backend.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @returns {{description: Object|null, errors: string[]}} Description ou erreurs UX.
 */
function buildImportConfigurationDescription(configuration) {
  const errors = [];
  const fileType = "libreoffice_ods";
  const wishlist = buildWishlistConfiguration(configuration, errors);
  if (!configuration.multipleSheets) {
    const layout = buildLayout(
      configuration.singleSheetLayout,
      collectionRequiredFields(configuration, true),
      errors
    );
    return {
      description: errors.length ? null : {
        file_type: fileType,
        wishlist,
        single_sheet_conf: layout,
      },
      errors,
    };
  }
  if (configuration.sharedLayout) {
    const requiredFields = collectionRequiredFields(configuration, false);
    const layout = buildLayout(configuration.sharedSheetLayout, requiredFields, errors);
    const selectionMode = configuration.sharedSheetLayout.sheetSelectionMode;
    if (selectionMode === "excluded") {
      const excludedSheets = splitSheetNames(configuration.sharedSheetLayout.excludedSheets);
      if (excludedSheets.length) {
        layout.excluded_sheets = excludedSheets;
      }
    } else {
      const includedSheets = splitSheetNames(configuration.sharedSheetLayout.includedSheets);
      if (includedSheets.length) {
        layout.included_sheets = includedSheets;
      }
    }
    return {
      description: errors.length ? null : {
        file_type: fileType,
        wishlist,
        multiple_sheets_conf: {
          sheet_information: SHEET_INFORMATION,
          shared_layout: layout,
        },
      },
      errors,
    };
  }
  const sheets = configuration.sheets.map((sheet, index) => {
    const sheetName = String(sheet.sheetName || "").trim();
    if (!sheetName) {
      errors.push(`Renseignez le nom de l'onglet ${index + 1}.`);
    }
    const requiredFields = collectionRequiredFields(configuration, false);
    return {
      sheet_name: sheetName,
      sheet_information: SHEET_INFORMATION,
      ...buildLayout(sheet.layout, requiredFields, errors),
    };
  });
  return {
    description: errors.length ? null : {
      file_type: fileType,
      wishlist,
      multiple_sheets_conf: { sheets },
    },
    errors,
  };
}

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
    errors.push("Selectionnez un mode wishlist valide.");
    return { mode: "none" };
  }
  const sheetName = String(configuration.wishlist.sheetName || "").trim();
  if (!sheetName) {
    errors.push("Renseignez l'onglet wishlist.");
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
    errors.push("Renseignez la plage de donnees.");
  }
  if (!Number.isInteger(headerRow) || headerRow < 1) {
    errors.push("Renseignez une ligne d'en-tete valide.");
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

/**
 * Applique les valeurs deduites d'une plage tableur a un layout.
 *
 * @param {Object} layout - Layout courant.
 * @param {string} dataRange - Plage saisie.
 * @param {string[]} columnFields - Champs a pre-remplir dans l'ordre.
 * @returns {Object} Layout enrichi.
 */
function applyDataRangeDefaults(layout, dataRange, columnFields) {
  const parsedRange = parseDataRange(dataRange);
  if (!parsedRange) {
    return { ...layout, dataRange };
  }
  const nextColumns = { ...layout.columns };
  parsedRange.columns.slice(0, columnFields.length).forEach((column, index) => {
    nextColumns[columnFields[index]] = column;
  });
  return {
    ...layout,
    dataRange,
    headerRow: String(parsedRange.headerRow),
    columns: nextColumns,
  };
}

/**
 * Parse une plage simple de type `A1:D200`.
 *
 * @param {string} dataRange - Plage saisie.
 * @returns {{headerRow: number, columns: string[]}|null} Details deduits.
 */
function parseDataRange(dataRange) {
  const match = String(dataRange || "").trim().toUpperCase().match(/^([A-Z]+)(\d+):([A-Z]+)(\d+)$/);
  if (!match) {
    return null;
  }
  const startColumnIndex = columnNameToIndex(match[1]);
  const endColumnIndex = columnNameToIndex(match[3]);
  if (startColumnIndex > endColumnIndex) {
    return null;
  }
  return {
    headerRow: Number.parseInt(match[2], 10),
    columns: Array.from(
      { length: endColumnIndex - startColumnIndex + 1 },
      (_, index) => columnIndexToName(startColumnIndex + index)
    ),
  };
}

/**
 * Convertit une colonne tableur en index.
 *
 * @param {string} columnName - Nom de colonne.
 * @returns {number} Index base 1.
 */
function columnNameToIndex(columnName) {
  return columnName.split("").reduce((total, character) => (
    total * 26 + character.charCodeAt(0) - 64
  ), 0);
}

/**
 * Convertit un index en colonne tableur.
 *
 * @param {number} index - Index base 1.
 * @returns {string} Nom de colonne.
 */
function columnIndexToName(index) {
  let value = index;
  let columnName = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    columnName = String.fromCharCode(65 + remainder) + columnName;
    value = Math.floor((value - 1) / 26);
  }
  return columnName;
}

export {
  REQUIRED_FIELDS,
  applyDataRangeDefaults,
  collectionRequiredFields,
  createDefaultImportConfiguration,
  buildImportConfigurationDescription,
};
