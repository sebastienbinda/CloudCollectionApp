/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-05
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : service objet evaluant les actions frontend autorisees par les routes backend.
 */

class BackendRouteAccessService {
  /**
   * Retourne les permissions par defaut avant chargement du backend.
   *
   * @param {boolean} isAuthenticated - Etat de session a exposer au frontend.
   * @returns {Object} Permissions refusees par defaut.
   */
  static getDefaultActionPermissions(isAuthenticated = false) {
    return {
      canAddGame: false,
      canEditGame: false,
      canDeleteGame: false,
      canDownloadOds: false,
      canResetLibrary: false,
      canSyncPlatformCatalog: false,
      canModeratePlatformImages: false,
      canUpdatePlatformImageStatus: false,
      canUpdatePlatformImageType: false,
      canReinitializeCollection: false,
      canSearchUsers: false,
      canDeleteUser: false,
      canLockUser: false,
      canUnlockUser: false,
      canValidateUser: false,
      canManageCollectionShares: false,
      isAuthenticated,
    };
  }

  /**
   * Retourne les permissions de repli basees sur le token local.
   *
   * @param {string} accessToken - Token Bearer actuellement stocke cote frontend.
   * @returns {Object} Permissions refusees avec un etat de session coherent.
   */
  static getFallbackActionPermissions(accessToken = "") {
    return this.getDefaultActionPermissions(String(accessToken || "").trim().length > 0);
  }

  /**
   * Charge les routes backend et calcule les permissions du frontend.
   *
   * @param {Object} apiClient - Client API exposant `fetchRoutes` et `getAccessToken`.
   * @returns {Promise<Object>} Permissions applicatives calculees.
   */
  static async loadActionPermissions(apiClient) {
    const data = await apiClient.fetchRoutes();
    const service = new BackendRouteAccessService(
      data.routes || [],
      apiClient.getAccessToken(),
      apiClient.getAuthenticatedProfile ? apiClient.getAuthenticatedProfile() : "USER"
    );
    return service.getActionPermissions();
  }

  /**
   * Initialise le service avec les routes et le token courant.
   *
   * @param {Array<Object>} routes - Routes retournees par `/api/routes`.
   * @param {string} accessToken - Token Bearer disponible cote frontend.
   * @param {string} userProfile - Profil applicatif porte par le token courant.
   * @returns {void} Le constructeur ne retourne aucune valeur.
   */
  constructor(routes = [], accessToken = "", userProfile = "USER") {
    this.routes = Array.isArray(routes) ? routes : [];
    this.accessToken = accessToken || "";
    this.userProfile = this.normalizeProfile(userProfile);
  }

  /**
   * Indique si une route backend peut etre appelee.
   *
   * @param {string} method - Methode HTTP de l'action.
   * @param {string} path - Chemin exact expose par le backend.
   * @returns {boolean} `true` si la route est publique ou autorisee par profil.
   */
  canAccess(method, path) {
    const route = this.findRoute(method, path);
    if (!route) {
      return false;
    }
    return !route.requires_auth || (this.hasToken() && this.hasRequiredProfile(route));
  }

  /**
   * Cherche une route par methode et chemin.
   *
   * @param {string} method - Methode HTTP recherchee.
   * @param {string} path - Chemin exact recherche.
   * @returns {Object|null} Route trouvee ou `null`.
   */
  findRoute(method, path) {
    const normalizedMethod = String(method || "").toUpperCase();
    return (
      this.routes.find(
        (route) =>
          route.path === path &&
          Array.isArray(route.methods) &&
          route.methods.includes(normalizedMethod)
      ) || null
    );
  }

  /**
   * Indique si le frontend dispose d'un token Bearer.
   *
   * @param {void} Aucun - Utilise le token fourni au constructeur.
   * @returns {boolean} `true` si un token non vide est disponible.
   */
  hasToken() {
    return this.accessToken.trim().length > 0;
  }

  /**
   * Normalise un profil applicatif frontend.
   *
   * @param {string} profile - Profil brut a normaliser.
   * @returns {string} Profil reconnu par le frontend.
   */
  normalizeProfile(profile) {
    const normalizedProfile = String(profile || "USER").trim().toUpperCase();
    return ["GUEST", "USER", "ADMIN"].includes(normalizedProfile) ? normalizedProfile : "USER";
  }

  /**
   * Indique si le profil courant satisfait une route.
   *
   * @param {Object} route - Route retournee par le catalogue backend.
   * @returns {boolean} `true` si le profil courant est autorise.
   */
  hasRequiredProfile(route) {
    const requiredProfiles = Array.isArray(route.required_profiles)
      ? route.required_profiles.map((profile) => this.normalizeProfile(profile))
      : ["USER", "ADMIN"];
    return requiredProfiles.includes(this.userProfile)
      || (this.userProfile === "ADMIN" && requiredProfiles.includes("USER"));
  }

  /**
   * Retourne les permissions utiles aux vues React.
   *
   * @param {void} Aucun - Utilise le catalogue de routes charge.
   * @returns {Object} Drapeaux booleens par action applicative.
   */
  getActionPermissions() {
    return {
      ...BackendRouteAccessService.getDefaultActionPermissions(this.hasToken()),
      canAddGame: false,
      canEditGame: false,
      canDeleteGame: false,
      canDownloadOds: this.canAccess("GET", "/collections/videogames/download"),
      canResetLibrary: this.canAccess("POST", "/api/library/reset"),
      canSyncPlatformCatalog: this.canAccess("POST", "/api/library/platform-catalog/sync"),
      canModeratePlatformImages: this.canAccess("GET", "/api/library/platforms/images"),
      canUpdatePlatformImageStatus: this.canAccess(
        "PUT",
        "/api/library/platforms/<int:platform_id>/image/<int:image_id>/status/<status>"
      ),
      canUpdatePlatformImageType: this.canAccess(
        "PUT",
        "/api/library/platforms/<int:platform_id>/image/<int:image_id>/type/<image_type>"
      ),
      canReinitializeCollection: this.canAccess("POST", "/api/users/collection/reinit"),
      canSearchUsers: this.canAccess("GET", "/api/users"),
      canDeleteUser: this.canAccess("DELETE", "/api/users/<int:user_id>"),
      canLockUser: this.canAccess("POST", "/api/users/<int:user_id>/lock"),
      canUnlockUser: this.canAccess("POST", "/api/users/<int:user_id>/unlock"),
      canValidateUser: this.canAccess("POST", "/api/users/<int:user_id>/validate"),
      canManageCollectionShares: (
        this.canAccess("GET", "/api/collection-shares") &&
        this.canAccess("POST", "/api/collection-shares") &&
        this.canAccess("DELETE", "/api/collection-shares/<int:share_id>")
      ),
    };
  }
}

export default BackendRouteAccessService;
