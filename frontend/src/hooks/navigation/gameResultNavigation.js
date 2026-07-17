/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : helpers purs de navigation entre jeux issus d'une liste.
 */

const DEFAULT_CONTEXT = Object.freeze({
  rows: [],
  page: 0,
  size: 0,
  totalElements: 0,
});

/**
 * Extrait l'identifiant stable d'un jeu de liste ou de detail.
 *
 * @param {Object|string|number|null} game - Jeu ou identifiant brut.
 * @returns {string} Identifiant normalise, ou chaine vide.
 */
function getGameNavigationId(game) {
  if (game === null || game === undefined) {
    return "";
  }
  const rawId = typeof game === "object" ? game.id : game;
  return rawId === null || rawId === undefined ? "" : String(rawId);
}

/**
 * Normalise un contexte de liste pour la navigation precedent/suivant.
 *
 * @param {Object|null} context - Contexte fourni par une page de liste.
 * @returns {Object} Contexte utilisable par le hook de navigation.
 */
function normalizeGameResultContext(context) {
  if (!context || typeof context !== "object") {
    return DEFAULT_CONTEXT;
  }
  const rows = Array.isArray(context.rows)
    ? context.rows.filter((row) => getGameNavigationId(row))
    : [];
  const size = Number.isFinite(context.size) && Number(context.size) > 0
    ? Number(context.size)
    : rows.length;
  const page = Number.isFinite(context.page) && Number(context.page) >= 0
    ? Number(context.page)
    : 0;
  const totalElements = Number.isFinite(context.totalElements)
    ? Number(context.totalElements)
    : rows.length;

  return {
    ...context,
    rows,
    page,
    size,
    totalElements: Math.max(totalElements, rows.length),
  };
}

/**
 * Trouve la position du jeu courant dans la page de resultats chargee.
 *
 * @param {Object} context - Contexte de navigation normalise.
 * @param {string|number} gameId - Identifiant du jeu courant.
 * @returns {number} Index local, ou `-1` si le jeu est absent.
 */
function findCurrentGameIndex(context, gameId) {
  const normalizedGameId = getGameNavigationId(gameId);
  return (context?.rows || []).findIndex((row) => getGameNavigationId(row) === normalizedGameId);
}

/**
 * Calcule les informations d'etat disponibles pour un jeu courant.
 *
 * @param {Object} context - Contexte de navigation normalise.
 * @param {string|number} gameId - Identifiant du jeu courant.
 * @returns {Object} Etat de navigation precedent/suivant.
 */
function buildGameResultNavigationState(context, gameId) {
  const resolvedContext = normalizeGameResultContext(context);
  const currentIndex = findCurrentGameIndex(resolvedContext, gameId);
  if (currentIndex < 0) {
    return {
      canOpenPreviousGame: false,
      canOpenNextGame: false,
      positionLabel: "",
    };
  }

  const absoluteIndex = (resolvedContext.page * resolvedContext.size) + currentIndex;
  const totalElements = resolvedContext.totalElements;
  return {
    canOpenPreviousGame: absoluteIndex > 0,
    canOpenNextGame: absoluteIndex < totalElements - 1,
    positionLabel: totalElements > 1 ? `${absoluteIndex + 1} / ${totalElements}` : "",
  };
}

/**
 * Retourne le jeu adjacent dans la page courante si disponible.
 *
 * @param {Object} context - Contexte de navigation normalise.
 * @param {string|number} gameId - Identifiant du jeu courant.
 * @param {"previous"|"next"} direction - Sens de navigation demande.
 * @returns {Object|null} Jeu adjacent ou absence.
 */
function findAdjacentGameInCurrentRows(context, gameId, direction) {
  const currentIndex = findCurrentGameIndex(context, gameId);
  if (currentIndex < 0) {
    return null;
  }
  const offset = direction === "previous" ? -1 : 1;
  return context.rows[currentIndex + offset] || null;
}

/**
 * Determine la page voisine a charger quand le jeu adjacent n'est pas local.
 *
 * @param {Object} context - Contexte de navigation normalise.
 * @param {string|number} gameId - Identifiant du jeu courant.
 * @param {"previous"|"next"} direction - Sens de navigation demande.
 * @returns {number|null} Numero de page a charger ou absence.
 */
function getAdjacentPageToLoad(context, gameId, direction) {
  const currentIndex = findCurrentGameIndex(context, gameId);
  if (currentIndex < 0 || !context.size) {
    return null;
  }
  if (direction === "previous" && currentIndex === 0 && context.page > 0) {
    return context.page - 1;
  }
  const isLastLocalRow = currentIndex === context.rows.length - 1;
  const hasFollowingPage = ((context.page + 1) * context.size) < context.totalElements;
  if (direction === "next" && isLastLocalRow && hasFollowingPage) {
    return context.page + 1;
  }
  return null;
}

/**
 * Selectionne le jeu cible dans une page chargee selon le sens de navigation.
 *
 * @param {Array<Object>} rows - Jeux de la page chargee.
 * @param {"previous"|"next"} direction - Sens de navigation demande.
 * @returns {Object|null} Jeu cible ou absence.
 */
function selectAdjacentGameFromLoadedPage(rows, direction) {
  const normalizedRows = Array.isArray(rows)
    ? rows.filter((row) => getGameNavigationId(row))
    : [];
  if (!normalizedRows.length) {
    return null;
  }
  return direction === "previous"
    ? normalizedRows[normalizedRows.length - 1]
    : normalizedRows[0];
}

export {
  buildGameResultNavigationState,
  findAdjacentGameInCurrentRows,
  getAdjacentPageToLoad,
  getGameNavigationId,
  normalizeGameResultContext,
  selectAdjacentGameFromLoadedPage,
};
