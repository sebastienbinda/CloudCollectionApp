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
 * Description : outils frontend de colonnes tableur pour l'import.
 */

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

export { applyDataRangeDefaults };
