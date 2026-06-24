/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : politique de presentation des sessions GUEST derivee du token signe.
 */

/**
 * Centralise les permissions visuelles d'une session de partage.
 */
class GuestSessionViewPolicy {
  /**
   * Construit la politique depuis les claims du Bearer courant.
   *
   * @param {Object} payload - Claims signes du token d'acces.
   * @returns {GuestSessionViewPolicy} Politique de presentation courante.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor(payload = {}) {
    this.payload = payload || {};
    this.profile = String(this.payload.profile || "").trim().toUpperCase();
    this.isGuest = this.profile === "GUEST";
    this.ownerPseudonym = this.isGuest
      ? String(this.payload.owner_pseudonym || this.payload.display_name || "").trim()
      : "";
    const permissions = this.payload.permissions || {};
    this.canViewCollection = !this.isGuest || permissions.collection === true;
    this.canViewWishlist = !this.isGuest || permissions.wishlist === true;
    this.canViewPrices = !this.isGuest || permissions.prices === true;
    this.canAccessConfiguration = !this.isGuest;
    this.canMutate = !this.isGuest;
  }

  /**
   * Retourne l'identite a afficher dans le menu partage.
   *
   * @param {string} defaultIdentity - Identite USER ou ADMIN habituelle.
   * @returns {string} Identite standard ou `Invite de <pseudonyme>`.
   * @throws {void} Ne leve pas d'exception.
   */
  getIdentityLabel(defaultIdentity = "") {
    if (!this.isGuest) {
      return String(defaultIdentity || "");
    }
    return `Invité de ${this.ownerPseudonym || "l'utilisateur"}`;
  }

  /**
   * Retourne le libelle GUEST associe a une categorie partagee.
   *
   * @param {"collection"|"wishlist"} category - Categorie de page affichee.
   * @returns {string} Sous-titre personnalise ou chaine vide hors GUEST.
   * @throws {void} Ne leve pas d'exception.
   */
  getSharedCollectionLabel(category) {
    if (!this.isGuest) {
      return "";
    }
    const prefix = category === "wishlist" ? "Liste de souhaits de" : "Collection de";
    return `${prefix} ${this.ownerPseudonym || "l'utilisateur"}`;
  }

  /**
   * Expose un objet immutable directement consommable par React.
   *
   * @param {string} defaultIdentity - Identite standard avant adaptation GUEST.
   * @returns {Object} Permissions, pseudonyme et libelles de presentation.
   * @throws {void} Ne leve pas d'exception.
   */
  toViewModel(defaultIdentity = "") {
    return Object.freeze({
      isGuest: this.isGuest,
      ownerPseudonym: this.ownerPseudonym,
      identityLabel: this.getIdentityLabel(defaultIdentity),
      collectionLabel: this.getSharedCollectionLabel("collection"),
      wishlistLabel: this.getSharedCollectionLabel("wishlist"),
      canViewCollection: this.canViewCollection,
      canViewWishlist: this.canViewWishlist,
      canViewPrices: this.canViewPrices,
      canAccessConfiguration: this.canAccessConfiguration,
      canMutate: this.canMutate,
    });
  }
}

export default GuestSessionViewPolicy;
