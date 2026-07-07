/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : politique de navigation des sessions de partage GUEST.
 */

/**
 * Centralise les redirections imposees par les permissions d'un partage.
 */
class GuestNavigationPolicy {
  /**
   * Construit une politique de navigation GUEST.
   *
   * @param {Object} permissions - Permissions de consultation du partage.
   * @returns {GuestNavigationPolicy} Politique de navigation configuree.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor({ canViewCollection = false, canViewWishlist = false } = {}) {
    this.canViewCollection = canViewCollection === true;
    this.canViewWishlist = canViewWishlist === true;
  }

  /**
   * Retourne la premiere destination autorisee pour la session GUEST.
   *
   * @returns {{view: string, path: string}} Destination React et URL correspondante.
   * @throws {void} Ne leve pas d'exception.
   */
  getFallbackDestination() {
    if (this.canViewCollection) return { view: "home", path: "/collection" };
    if (this.canViewWishlist) return { view: "wishlist", path: "/wishlist" };
    return { view: "about", path: "/about" };
  }

  /**
   * Indique si une vue demandee doit etre remplacee pour un profil GUEST.
   *
   * @param {string} view - Vue React demandee.
   * @returns {boolean} `true` lorsque la vue n'est pas autorisee.
   * @throws {void} Ne leve pas d'exception.
   */
  isViewBlocked(view) {
    if ([
      "configuration",
      "adminLibraryImport",
      "collectionShares",
      "platformImageModeration",
      "users",
      "addGame",
      "collectionOnboarding",
    ].includes(view)) return true;
    if (["home", "games", "statistics"].includes(view)) return !this.canViewCollection;
    if (view === "wishlist") return !this.canViewWishlist;
    return false;
  }
}

export default GuestNavigationPolicy;
