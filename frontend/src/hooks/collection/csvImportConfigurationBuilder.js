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
 * Description : construction frontend de la configuration d'import CSV.
 */

const REQUIRED_CSV_FIELDS = Object.freeze(["name", "platform"]);
const OPTIONAL_CSV_FIELDS = Object.freeze([
  "studio", "release_date", "purchase_price", "buy_location", "buy_date", "grade",
  "condition", "has_manual", "is_collector", "has_steelbook", "is_digital",
  "region", "description",
]);

/**
 * Construit le mapping CSV par defaut.
 *
 * @returns {Object} Mapping CSV initial.
 */
function createDefaultCsvMapping() {
  return Object.fromEntries(
    [...REQUIRED_CSV_FIELDS, ...OPTIONAL_CSV_FIELDS, "wishlist"].map((field) => [field, ""])
  );
}

/**
 * Convertit une description CSV sauvegardee en configuration frontend.
 *
 * @param {Object} description - Description backend sauvegardee.
 * @param {Object} defaultConfiguration - Configuration frontend par defaut.
 * @param {Object} wishlist - Configuration wishlist frontend.
 * @returns {Object} Configuration frontend CSV.
 */
function buildFrontendCsvConfiguration(description, defaultConfiguration, wishlist) {
  const mapping = description.mapping || {};
  return {
    ...defaultConfiguration,
    fileType: "csv",
    priceUnit: description.price_unit || defaultConfiguration.priceUnit,
    multipleSheets: false,
    wishlist: {
      ...wishlist,
      mode: wishlist.mode === "sheet" ? "none" : wishlist.mode,
    },
    csvMapping: {
      ...defaultConfiguration.csvMapping,
      ...Object.fromEntries(
        Object.entries(mapping).map(([fieldName, columnName]) => [
          fieldName,
          String(columnName || ""),
        ])
      ),
    },
  };
}

/**
 * Construit la description JSON CSV attendue par le backend.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @returns {{description: Object|null, errors: string[]}} Description ou erreurs UX.
 */
function buildCsvImportConfigurationDescription(configuration) {
  const errors = [];
  const wishlist = buildCsvWishlistConfiguration(configuration, errors);
  const mapping = buildCsvMapping(configuration.csvMapping, wishlist.mode, errors);
  return {
    description: errors.length ? null : {
      file_type: "csv",
      price_unit: configuration.priceUnit,
      wishlist,
      mapping,
    },
    errors,
  };
}

/**
 * Construit la configuration wishlist compatible CSV.
 *
 * @param {Object} configuration - Etat frontend de configuration.
 * @param {string[]} errors - Erreurs UX a enrichir.
 * @returns {Object} Configuration wishlist serialisable.
 */
function buildCsvWishlistConfiguration(configuration, errors) {
  const mode = configuration.wishlist?.mode || "none";
  if (mode === "none" || mode === "column") {
    return { mode };
  }
  errors.push("Le CSV accepte uniquement une wishlist absente ou portee par une colonne.");
  return { mode: "none" };
}

/**
 * Construit le mapping CSV serialisable.
 *
 * @param {Object} csvMapping - Mapping frontend courant.
 * @param {string} wishlistMode - Mode wishlist selectionne.
 * @param {string[]} errors - Erreurs UX a enrichir.
 * @returns {Object} Mapping backend.
 */
function buildCsvMapping(csvMapping, wishlistMode, errors) {
  const requiredFields = new Set(REQUIRED_CSV_FIELDS);
  if (wishlistMode === "column") {
    requiredFields.add("wishlist");
  }
  const mapping = {};
  [...requiredFields].forEach((field) => {
    const columnName = String(csvMapping?.[field] || "").trim();
    if (!columnName) {
      errors.push(`Renseignez la colonne ${field}.`);
      return;
    }
    mapping[field] = columnName;
  });
  OPTIONAL_CSV_FIELDS.forEach((field) => {
    const columnName = String(csvMapping?.[field] || "").trim();
    if (columnName) {
      mapping[field] = columnName;
    }
  });
  return mapping;
}

export {
  OPTIONAL_CSV_FIELDS,
  REQUIRED_CSV_FIELDS,
  buildCsvImportConfigurationDescription,
  buildFrontendCsvConfiguration,
  createDefaultCsvMapping,
};
