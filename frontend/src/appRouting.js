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
class AppRouting {
  /**
   * Cree l'etat initial du formulaire d'ajout de jeu.
   *
   * @param {void} Aucun - Les valeurs par defaut sont statiques.
   * @returns {Object} Formulaire vide pret a etre stocke dans React.
   */
  static createInitialGameForm() {
    return {
      platform: "",
      "Nom du jeu": "",
      Studio: "",
      "Date de sortie": "",
      "Date d'achat": "",
      "Lieu d'achat": "",
      Note: "",
      "Prix d'achat": "",
      Version: "",
    };
  }

  /**
   * Lit l'identifiant de plateforme present dans l'URL courante.
   *
   * @param {void} Aucun - Utilise `window.location.search`.
   * @returns {string} Identifiant issu du parametre `platform_id`, ou chaine vide.
   */
  static getPlatformIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("platform_id") || "";
  }

  /**
   * Lit la plateforme presente dans l'URL courante.
   *
   * @param {void} Aucun - Utilise `window.location.search`.
   * @returns {string} Identifiant de plateforme compatible avec l'ancien appel.
   */
  static getPlatformFromUrl() {
    return AppRouting.getPlatformIdFromUrl();
  }

  /**
   * Indique si un token Bearer est stocke cote navigateur.
   *
   * @param {void} Aucun - Lit le stockage local du navigateur.
   * @returns {boolean} `true` si un token d'acces existe.
   */
  static hasStoredAccessToken() {
    if (typeof window === "undefined" || !window.localStorage) {
      return false;
    }
    return Boolean(window.localStorage.getItem("cloudCollectionAccessToken"));
  }

  /**
   * Indique si le chemin courant est accessible sans session.
   *
   * @param {string} pathname - Chemin d'URL a verifier.
   * @returns {boolean} `true` si le chemin est public.
   */
  static isPublicPath(pathname) {
    return [
      "/about",
      "/auth",
      "/bibliotheque",
      "/bibliotheque/plateformes",
      "/bibliotheque/studios",
      "/bibliotheque/jeux",
    ].includes(pathname);
  }

  /**
   * Deduit la vue active depuis le chemin et les parametres d'URL.
   *
   * @param {void} Aucun - Utilise `window.location`.
   * @returns {"about"|"home"|"games"|"addGame"|"configuration"|"auth"|"users"|"collectionOnboarding"|"library"|"libraryPlatforms"|"libraryStudios"|"libraryGames"} Identifiant de vue.
   */
  static getViewFromUrl() {
    if (window.location.pathname === "/about") {
      return "about";
    }
    if (window.location.pathname === "/auth") {
      return "auth";
    }
    if (window.location.pathname === "/bibliotheque") {
      return "library";
    }
    if (window.location.pathname === "/bibliotheque/plateformes") {
      return "libraryPlatforms";
    }
    if (window.location.pathname === "/bibliotheque/studios") {
      return "libraryStudios";
    }
    if (window.location.pathname === "/bibliotheque/jeux") {
      return "libraryGames";
    }
    if (!AppRouting.hasStoredAccessToken()) {
      return "about";
    }
    if (window.location.pathname === "/collection") {
      return "home";
    }
    if (window.location.pathname === "/add-game") {
      return "addGame";
    }
    if (window.location.pathname === "/configuration") {
      return "configuration";
    }
    if (window.location.pathname === "/users") {
      return "users";
    }
    if (window.location.pathname === "/collection/import") {
      return "collectionOnboarding";
    }
    if (AppRouting.getPlatformIdFromUrl()) {
      return "games";
    }
    return AppRouting.hasStoredAccessToken() ? "home" : "about";
  }
}

export default AppRouting;
