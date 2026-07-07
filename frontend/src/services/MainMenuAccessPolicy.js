/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-25
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : politique d'acces aux entrees du menu principal.
 */

/**
 * Centralise les droits effectifs des entrees du menu principal.
 *
 * @param {Object} options - Etat de session, droits de consultation et callbacks disponibles.
 * @returns {Object} Droits de navigation effectifs pour le menu.
 * @throws {void} Ne leve pas d'exception.
 */
function resolveMainMenuAccess(options = {}) {
  const isAuthenticated = options.isAuthenticated === true;
  return Object.freeze({
    canOpenConfiguration: (
      isAuthenticated &&
      options.canAccessConfiguration === true &&
      typeof options.onOpenConfiguration === "function"
    ),
    canOpenWishlist: (
      isAuthenticated &&
      options.canViewWishlist === true &&
      typeof options.onOpenWishlist === "function"
    ),
    canOpenHome: (
      isAuthenticated &&
      options.canViewCollection === true &&
      typeof options.onOpenHome === "function"
    ),
    canOpenStatistics: (
      isAuthenticated &&
      options.canViewStatistics === true &&
      typeof options.onOpenStatistics === "function"
    ),
  });
}

export default resolveMainMenuAccess;
