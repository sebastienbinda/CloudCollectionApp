/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
const dateFormatter = new Intl.DateTimeFormat("fr-FR");
const monthYearFormatter = new Intl.DateTimeFormat("fr-FR", {
  month: "2-digit",
  year: "numeric",
});

/**
 * Detecte si une colonne contient une date.
 *
 * @param {string} column - Nom de colonne a analyser.
 * @returns {boolean} `true` si le nom contient `date`, sinon `false`.
 */
export const isDateColumn = (column) => column.toLowerCase().includes("date");

/**
 * Detecte si une colonne represente un studio/developpeur.
 *
 * @param {string} column - Nom de colonne a analyser.
 * @returns {boolean} `true` si la colonne concerne un studio ou developpeur.
 */
export const isDeveloperColumn = (column) => {
  const normalized = column.toLowerCase();
  return normalized.includes("studio") || normalized.includes("develop");
};

/**
 * Indique si une colonne doit utiliser un filtre select.
 *
 * @param {string} column - Nom de colonne a analyser.
 * @returns {boolean} `true` pour les colonnes a valeurs discretes.
 */
export const isSelectFilterColumn = (column) =>
  isDeveloperColumn(column) || column === "Version";

/**
 * Retourne la classe CSS de largeur/format pour une colonne.
 *
 * @param {string} column - Nom de colonne du tableau.
 * @returns {string} Classe CSS a appliquer, ou chaine vide.
 */
export const getColumnClassName = (column) => {
  if (column === "Nom du jeu" || column === "name") {
    return "gameNameColumn";
  }
  if (isDateColumn(column)) {
    return "dateColumn";
  }
  if (["Note", "Version"].includes(column)) {
    return "compactColumn";
  }
  if (column === "Prix d'achat") {
    return "priceColumn";
  }
  return "";
};

/**
 * Formate une valeur de cellule pour l'affichage.
 *
 * @param {string} column - Nom de colonne, utilise pour detecter les dates.
 * @param {unknown} value - Valeur brute de la cellule.
 * @returns {string} Texte affiche dans le tableau ou les cartes.
 */
export const formatCellValue = (column, value) => {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (isDateColumn(column)) {
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) {
      return dateFormatter.format(parsed);
    }
  }

  return String(value);
};

/**
 * Formate une valeur de date en mois/annee pour les affichages compacts.
 *
 * @param {unknown} value - Date ISO, date courte ou texte a convertir.
 * @returns {string} Date au format `MM/YYYY`, ou `-` si la valeur est vide.
 */
export const formatMonthYearValue = (value) => {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return monthYearFormatter.format(parsed);
  }

  return String(value);
};

/**
 * Extrait une annee depuis une date ou un texte.
 *
 * @param {unknown} value - Date ISO, date courte ou texte contenant une annee.
 * @returns {number|null} Annee extraite, ou `null` si aucune annee fiable n'est trouvee.
 */
export const extractYear = (value) => {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const parsedDate = new Date(value);
  if (!Number.isNaN(parsedDate.getTime())) {
    return parsedDate.getFullYear();
  }

  const text = String(value).trim();
  const fourDigitYearMatch = text.match(/(19|20)\d{2}/);
  if (fourDigitYearMatch) {
    return Number.parseInt(fourDigitYearMatch[0], 10);
  }

  const shortDateMatch = text.match(/^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{2})$/);
  if (shortDateMatch) {
    const year = Number.parseInt(shortDateMatch[3], 10);
    return year >= 70 ? 1900 + year : 2000 + year;
  }

  return null;
};

/**
 * Construit les options d'annees disponibles pour un filtre de date.
 *
 * @param {Record<string, unknown[]>} valuesByColumn - Valeurs distinctes par colonne.
 * @param {string} column - Nom de colonne date.
 * @returns {number[]} Annees uniques triees de la plus recente a la plus ancienne.
 */
export const getDateYearOptions = (valuesByColumn, column) => {
  const years = new Set();

  (valuesByColumn[column] || []).forEach((value) => {
    const year = extractYear(value);
    if (year !== null) {
      years.add(year);
    }
  });

  return Array.from(years).sort((a, b) => b - a);
};

/**
 * Filtre une liste de jeux selon les filtres de colonnes actifs.
 *
 * @param {Record<string, unknown>[]} games - Jeux bruts charges depuis l'API.
 * @param {string[]} columns - Colonnes visibles du tableau.
 * @param {Record<string, unknown>} columnFilters - Filtres saisis par colonne.
 * @returns {Record<string, unknown>[]} Jeux correspondant aux filtres.
 */
export const filterGames = (games, columns, columnFilters) =>
  games.filter((game) =>
    columns.every((column) => {
      if (isDateColumn(column)) {
        const dateFilter = columnFilters[column];
        if (!dateFilter || !dateFilter.year) {
          return true;
        }

        const gameYear = extractYear(game[column]);
        if (gameYear === null) {
          return false;
        }

        const selectedYear = Number.parseInt(dateFilter.year, 10);

        if (Number.isNaN(selectedYear)) {
          return true;
        }

        if (dateFilter.operator === ">") {
          return gameYear > selectedYear;
        }

        if (dateFilter.operator === "=") {
          return gameYear === selectedYear;
        }

        return gameYear < selectedYear;
      }

      const filterValue = (columnFilters[column] || "").trim().toLowerCase();
      if (!filterValue) {
        return true;
      }
      const cellValue = game[column] === null ? "" : String(game[column]).toLowerCase();
      return cellValue.includes(filterValue);
    })
  );

/**
 * Formate un nombre selon la locale francaise.
 *
 * @param {number|string|null|undefined} value - Nombre ou valeur vide.
 * @returns {string} Nombre formate ou `-`.
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numericValue = Number.parseFloat(String(value).replace(",", "."));
  if (Number.isNaN(numericValue)) {
    return "-";
  }
  return new Intl.NumberFormat("fr-FR").format(numericValue);
};

/**
 * Formate un montant en euros.
 *
 * @param {number|string|null|undefined} value - Montant brut ou valeur vide.
 * @returns {string} Montant formate en EUR ou `-`.
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numericValue = Number.parseFloat(String(value).replace(",", "."));
  if (Number.isNaN(numericValue)) {
    return "-";
  }
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(numericValue);
};

/**
 * Compte les studios distincts dans une liste de jeux.
 *
 * @param {Record<string, unknown>[]} games - Jeux d'une plateforme.
 * @returns {number} Nombre de studios uniques non vides.
 */
export const getStudioCount = (games) =>
  new Set(
    games
      .map((game) => game.Studio)
      .filter((studio) => studio !== null && studio !== undefined && String(studio).trim() !== "")
      .map((studio) => String(studio).trim().toLowerCase())
  ).size;
