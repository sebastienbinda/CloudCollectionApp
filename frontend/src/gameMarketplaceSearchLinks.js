/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-09
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : construction des liens de recherche marchande pour un jeu.
 */

const STANDARD_PURCHASE_SEARCH_TARGETS = [
  {
    key: "leboncoin",
    label: "leboncoin",
    baseUrl: "https://www.leboncoin.fr/recherche",
    iconUrl: "https://www.leboncoin.fr/favicon.ico",
    queryParameter: "text",
  },
  {
    key: "ebay",
    label: "eBay",
    baseUrl: "https://www.ebay.fr/sch/i.html",
    iconUrl: "https://www.ebay.fr/favicon.ico",
    queryParameter: "_nkw",
  },
];

const RECENT_PLATFORM_PURCHASE_SEARCH_TARGETS = [
  {
    key: "amazon",
    label: "Amazon",
    baseUrl: "https://www.amazon.fr/s",
    iconUrl: "https://www.amazon.fr/favicon.ico",
    queryParameter: "k",
  },
  {
    key: "fnac",
    label: "fnac.com",
    baseUrl: "https://www.fnac.com/SearchResult/ResultList.aspx",
    iconUrl: "https://www.fnac.com/favicon.ico",
    queryParameter: "Search",
  },
];

/**
 * Construit les liens de recherche externes pour un jeu.
 *
 * @param {string} gameName - Nom du jeu a rechercher.
 * @param {string} platformName - Nom optionnel de la plateforme.
 * @param {string} platformEndDate - Date de fin optionnelle de la plateforme.
 * @param {Date} referenceDate - Date de reference pour la regle des dix ans.
 * @returns {Array<Object>} Liens de recherche prets a afficher.
 * @throws {TypeError} Ne leve pas d'exception volontairement.
 */
export function buildGameMarketplaceSearchLinks(
  gameName,
  platformName = "",
  platformEndDate = "",
  referenceDate = new Date(),
  region = ""
) {
  const searchQuery = buildMarketplaceSearchQuery(gameName, platformName, region);
  if (!searchQuery) {
    return [];
  }

  const targets = [...STANDARD_PURCHASE_SEARCH_TARGETS];
  if (wasPlatformActiveTenYearsBefore(platformEndDate, referenceDate)) {
    targets.push(...RECENT_PLATFORM_PURCHASE_SEARCH_TARGETS);
  }

  return targets.map((target) => ({
    iconUrl: target.iconUrl,
    key: target.key,
    label: target.label,
    url: buildMarketplaceUrl(target.baseUrl, target.queryParameter, searchQuery),
  }));
}

/**
 * Construit la requete de recherche lisible par les places de marche.
 *
 * @param {string} gameName - Nom du jeu.
 * @param {string} platformName - Nom de la plateforme.
 * @param {string} region - Region optionnelle du jeu.
 * @returns {string} Requete normalisee.
 * @throws {TypeError} Ne leve pas d'exception volontairement.
 */
export function buildMarketplaceSearchQuery(gameName, platformName = "", region = "") {
  return [gameName, platformName, normalizeMarketplaceSearchRegion(region)]
    .map((value) => String(value || "").trim())
    .filter(Boolean)
    .join(" ");
}

/**
 * Indique si la plateforme etait encore active dix ans avant la date donnee.
 *
 * @param {string} platformEndDate - Date de fin de plateforme au format ISO.
 * @param {Date} referenceDate - Date de reference courante.
 * @returns {boolean} `true` si Amazon et Fnac doivent etre affiches.
 * @throws {TypeError} Ne leve pas d'exception volontairement.
 */
export function wasPlatformActiveTenYearsBefore(platformEndDate, referenceDate = new Date()) {
  const normalizedEndDate = String(platformEndDate || "").trim();
  if (!normalizedEndDate) {
    return true;
  }

  const endDate = parseIsoDate(normalizedEndDate);
  if (!endDate) {
    return false;
  }

  return endDate >= buildTenYearsBeforeDate(referenceDate);
}

function buildMarketplaceUrl(baseUrl, queryParameter, searchQuery) {
  const parameters = new URLSearchParams({ [queryParameter]: searchQuery });
  return `${baseUrl}?${parameters.toString()}`;
}

function normalizeMarketplaceSearchRegion(region) {
  const normalizedRegion = String(region || "").trim();
  const comparableRegion = normalizedRegion.toUpperCase().replace(/\s+/g, "");
  if (!comparableRegion || ["EU-FR", "EUR-FR", "FR"].includes(comparableRegion)) {
    return "";
  }
  return normalizedRegion;
}

function buildTenYearsBeforeDate(referenceDate) {
  const threshold = new Date(Date.UTC(
    referenceDate.getUTCFullYear(),
    referenceDate.getUTCMonth(),
    referenceDate.getUTCDate()
  ));
  threshold.setUTCFullYear(threshold.getUTCFullYear() - 10);
  return threshold;
}

function parseIsoDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (!match) {
    return null;
  }
  const year = Number(match[1]);
  const monthIndex = Number(match[2]) - 1;
  const day = Number(match[3]);
  const parsedDate = new Date(Date.UTC(year, monthIndex, day));
  if (
    parsedDate.getUTCFullYear() !== year ||
    parsedDate.getUTCMonth() !== monthIndex ||
    parsedDate.getUTCDate() !== day
  ) {
    return null;
  }
  return parsedDate;
}
