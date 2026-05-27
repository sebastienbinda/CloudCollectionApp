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
    singleSheetLayout: createDefaultLayout(true),
    sharedSheetLayout: {
      ...createDefaultLayout(false),
      includedSheets: "",
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
  if (!configuration.multipleSheets) {
    const layout = buildLayout(configuration.singleSheetLayout, REQUIRED_FIELDS, errors);
    return {
      description: errors.length ? null : { file_type: fileType, single_sheet_conf: layout },
      errors,
    };
  }
  if (configuration.sharedLayout) {
    const requiredFields = REQUIRED_FIELDS.filter((field) => field !== SHEET_INFORMATION);
    const layout = buildLayout(configuration.sharedSheetLayout, requiredFields, errors);
    const includedSheets = splitSheetNames(configuration.sharedSheetLayout.includedSheets);
    if (includedSheets.length) {
      layout.included_sheets = includedSheets;
    }
    return {
      description: errors.length ? null : {
        file_type: fileType,
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
    const requiredFields = REQUIRED_FIELDS.filter((field) => field !== SHEET_INFORMATION);
    return {
      sheet_name: sheetName,
      sheet_information: SHEET_INFORMATION,
      ...buildLayout(sheet.layout, requiredFields, errors),
    };
  });
  return {
    description: errors.length ? null : {
      file_type: fileType,
      multiple_sheets_conf: { sheets },
    },
    errors,
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
  return String(value || "")
    .split(/[\n,]/)
    .map((sheetName) => sheetName.trim())
    .filter(Boolean);
}

export {
  REQUIRED_FIELDS,
  createDefaultImportConfiguration,
  buildImportConfigurationDescription,
};
