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
class JeuxVideoApi {
  static authTokenStorageKey = "cloudCollectionAccessToken";
  static authTokenExpiresAtStorageKey = "cloudCollectionAccessTokenExpiresAt";
  static authChangeEventName = "cloudcollectionauthchange";
  static sessionExpiredEventName = "cloudcollectionsessionexpired";
  static expiredSessionQuery = "session-expired";
  static hasNotifiedExpiredSession = false;

  /**
   * Demande un token Bearer au backend avec les identifiants fournis.
   *
   * @param {string} username - Identifiant d'authentification.
   * @param {string} password - Mot de passe d'authentification.
   * @returns {Promise<Object>} Reponse OAuth2 contenant le token.
   */
  static async authenticate(username, password) {
    const data = await this.fetchJson("/auth/token", "Authentification impossible.", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });
    this.storeAccessToken(data.access_token || "", data.expires_in || null);
    return data;
  }

  /**
   * Charge le catalogue des routes accessibles expose par le backend.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Objet contenant `routes`.
   */
  static async fetchRoutes() {
    return this.fetchJson("/api/routes", "Impossible de recuperer les routes backend.");
  }

  /**
   * Charge les statistiques d'accueil.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Donnees du tableau de bord.
   */
  static async fetchHomeStats() {
    return this.fetchJson("/collections/JeuxVideo/home", "Impossible de recuperer l'accueil.");
  }

  /**
   * Charge la liste des plateformes.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Objet contenant `platforms`.
   */
  static async fetchPlatforms() {
    return this.fetchJson(
      "/collections/JeuxVideo/platforms",
      "Impossible de recuperer les plateformes."
    );
  }

  /**
   * Charge les jeux d'une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS a lire.
   * @returns {Promise<Array>} Liste des jeux de la plateforme.
   */
  static async fetchGames(platform) {
    return this.fetchJson(
      `/collections/JeuxVideo/search?platform=${encodeURIComponent(platform)}`,
      "Impossible de recuperer les jeux video."
    );
  }

  /**
   * Charge les valeurs distinctes de colonnes pour une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS a analyser.
   * @returns {Promise<Object>} Objet contenant `values_by_column`.
   */
  static async fetchColumnValues(platform) {
    return this.fetchJson(
      `/collections/JeuxVideo/column-values?platform=${encodeURIComponent(platform)}`,
      "Impossible de recuperer les valeurs de colonnes."
    );
  }

  /**
   * Ajoute un jeu au fichier ODS.
   *
   * @param {Object} gameForm - Donnees du formulaire d'ajout.
   * @returns {Promise<Object>} Objet contenant le jeu ajoute.
   */
  static async addGame(gameForm) {
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible d'ajouter le jeu.", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthorizationHeaders(),
      },
      body: JSON.stringify(gameForm),
    });
  }

  /**
   * Supprime un jeu d'une plateforme.
   *
   * @param {Object} game - Jeu identifie par sa plateforme et son nom.
   * @returns {Promise<Object>} Objet contenant le jeu supprime.
   */
  static async deleteGame(game) {
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible de supprimer le jeu.", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthorizationHeaders(),
      },
      body: JSON.stringify(game),
    });
  }

  /**
   * Modifie un jeu d'une plateforme.
   *
   * @param {Object} payload - Donnees contenant plateforme, jeu original et jeu modifie.
   * @returns {Promise<Object>} Objet contenant le jeu modifie.
   */
  static async updateGame(payload) {
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible de modifier le jeu.", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthorizationHeaders(),
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Supprime un jeu de la liste de souhaits.
   *
   * @param {Object} game - Jeu wishlist identifie par son nom et sa console.
   * @returns {Promise<Object>} Objet contenant le jeu supprime.
   */
  static async deleteWishlistGame(game) {
    return this.fetchJson(
      "/collections/JeuxVideo/wishlist/games",
      "Impossible de supprimer le jeu de la liste de souhaits.",
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          ...this.getAuthorizationHeaders(),
        },
        body: JSON.stringify({
          "Nom du jeu": game["Nom du jeu"],
          Console: game.Console || game.Plateforme,
        }),
      }
    );
  }

  /**
   * Modifie un jeu de la liste de souhaits.
   *
   * @param {Object} payload - Donnees contenant jeu original et jeu modifie.
   * @returns {Promise<Object>} Objet contenant le jeu wishlist modifie.
   */
  static async updateWishlistGame(payload) {
    return this.fetchJson(
      "/collections/JeuxVideo/wishlist/games",
      "Impossible de modifier le jeu de la liste de souhaits.",
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...this.getAuthorizationHeaders(),
        },
        body: JSON.stringify(payload),
      }
    );
  }

  /**
   * Recherche un jeu par nom dans toutes les plateformes.
   *
   * @param {string} query - Texte recherche dans le nom du jeu.
   * @returns {Promise<Object>} Objet contenant les resultats.
   */
  static async searchGamesByName(query) {
    return this.fetchJson(
      `/collections/JeuxVideo/game-search?q=${encodeURIComponent(query)}`,
      "Impossible de rechercher les jeux."
    );
  }

  /**
   * Reinitialise le cache backend du fichier ODS.
   *
   * @param {void} Aucun - Appelle l'endpoint de reset.
   * @returns {Promise<Object>} Resultat de reinitialisation du cache.
   */
  static async resetCache() {
    return this.fetchJson("/collections/JeuxVideo/cache/reset", "Impossible de reinitialiser le cache.", {
      method: "POST",
      headers: this.getAuthorizationHeaders(),
    });
  }

  /**
   * Telecharge le fichier ODS de la collection.
   *
   * @param {void} Aucun - Appelle l'endpoint protege de telechargement.
   * @returns {Promise<void>} Declenche le telechargement du fichier.
   */
  static async downloadOdsFile() {
    const requestOptions = {
      headers: this.getAuthorizationHeaders(),
    };
    const response = await fetch("/collections/JeuxVideo/ods/download", requestOptions);
    if (!response.ok) {
      const data = await this.parseJsonResponse(response, "Impossible de telecharger le fichier ODS.");
      if (this.isExpiredAuthenticatedResponse(response, requestOptions)) {
        this.handleExpiredSession();
      }
      throw new Error(data.error || "Impossible de telecharger le fichier ODS.");
    }
    const blob = await response.blob();
    const filename = this.getDownloadFilename(response) || "JeuxVideo.ods";
    this.saveBlob(blob, filename);
  }

  /**
   * Extrait le nom de fichier depuis l'en-tete de telechargement.
   *
   * @param {Response} response - Reponse HTTP de telechargement.
   * @returns {string} Nom de fichier extrait, ou chaine vide.
   */
  static getDownloadFilename(response) {
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^"]+)"?/);
    return match ? match[1] : "";
  }

  /**
   * Sauvegarde un Blob via un lien temporaire.
   *
   * @param {Blob} blob - Contenu binaire a sauvegarder.
   * @param {string} filename - Nom de fichier propose.
   * @returns {void} Declenche le telechargement navigateur.
   */
  static saveBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  /**
   * Retourne le token Bearer stocke cote navigateur.
   *
   * @param {void} Aucun - Lit `localStorage` si disponible.
   * @returns {string} Token d'acces ou chaine vide.
   */
  static getAccessToken() {
    if (typeof window === "undefined" || !window.localStorage) {
      return "";
    }
    return window.localStorage.getItem(this.authTokenStorageKey) || "";
  }

  /**
   * Decode le payload JSON du token Bearer courant.
   *
   * @param {void} Aucun - Utilise le token stocke cote navigateur.
   * @returns {Object} Payload du token ou objet vide.
   */
  static getAccessTokenPayload() {
    const accessToken = this.getAccessToken();
    const payloadSegment = accessToken.split(".")[0] || "";
    if (!payloadSegment) {
      return {};
    }

    try {
      const normalizedPayload = payloadSegment.replace(/-/g, "+").replace(/_/g, "/");
      const paddedPayload = normalizedPayload.padEnd(
        normalizedPayload.length + ((4 - (normalizedPayload.length % 4)) % 4),
        "="
      );
      return JSON.parse(window.atob(paddedPayload));
    } catch (error) {
      return {};
    }
  }

  /**
   * Retourne le nom de l'utilisateur authentifie depuis le token.
   *
   * @param {void} Aucun - Lit le champ `sub` du token courant.
   * @returns {string} Nom utilisateur connecte ou chaine vide.
   */
  static getAuthenticatedUsername() {
    return String(this.getAccessTokenPayload().sub || "");
  }

  /**
   * Stocke le token Bearer et notifie l'application.
   *
   * @param {string} accessToken - Token a stocker.
   * @param {number|null} expiresInSeconds - Duree de vie du token en secondes.
   * @returns {void} Met a jour `localStorage`.
   */
  static storeAccessToken(accessToken, expiresInSeconds = null) {
    if (typeof window === "undefined" || !window.localStorage) {
      return;
    }
    window.localStorage.setItem(this.authTokenStorageKey, accessToken);
    this.storeAccessTokenExpiration(expiresInSeconds);
    this.hasNotifiedExpiredSession = false;
    window.dispatchEvent(new Event(this.authChangeEventName));
  }

  /**
   * Stocke l'heure d'expiration du token Bearer.
   *
   * @param {number|null} expiresInSeconds - Duree de vie du token en secondes.
   * @returns {void} Met a jour l'expiration locale du token.
   */
  static storeAccessTokenExpiration(expiresInSeconds) {
    if (!expiresInSeconds) {
      window.localStorage.removeItem(this.authTokenExpiresAtStorageKey);
      return;
    }
    const expiresAt = Date.now() + Number(expiresInSeconds) * 1000;
    window.localStorage.setItem(this.authTokenExpiresAtStorageKey, String(expiresAt));
  }

  /**
   * Supprime le token Bearer et notifie l'application.
   *
   * @param {void} Aucun - Modifie `localStorage`.
   * @returns {void} Supprime le token courant.
   */
  static clearAccessToken() {
    if (typeof window === "undefined" || !window.localStorage) {
      return;
    }
    window.localStorage.removeItem(this.authTokenStorageKey);
    window.localStorage.removeItem(this.authTokenExpiresAtStorageKey);
    window.dispatchEvent(new Event(this.authChangeEventName));
  }

  /**
   * Retourne l'heure d'expiration locale du token courant.
   *
   * @param {void} Aucun - Lit `localStorage`.
   * @returns {number} Timestamp epoch millisecondes ou zero.
   */
  static getAccessTokenExpiresAt() {
    if (typeof window === "undefined" || !window.localStorage) {
      return 0;
    }
    return Number(window.localStorage.getItem(this.authTokenExpiresAtStorageKey) || 0);
  }

  /**
   * Calcule le temps restant avant expiration du token courant.
   *
   * @param {void} Aucun - Utilise l'heure locale et l'expiration stockee.
   * @returns {number} Millisecondes restantes, zero si expire ou inconnu.
   */
  static getAccessTokenTimeToLiveMs() {
    const expiresAt = this.getAccessTokenExpiresAt();
    return expiresAt ? Math.max(0, expiresAt - Date.now()) : 0;
  }

  /**
   * Confirme la deconnexion puis supprime le token local.
   *
   * @param {void} Aucun - Utilise `window.confirm`.
   * @returns {void} Supprime le token si l'utilisateur confirme.
   */
  static confirmAndClearAccessToken() {
    if (window.confirm("Confirmer la deconnexion ?")) {
      JeuxVideoApi.clearAccessToken();
    }
  }

  /**
   * Construit les en-tetes d'autorisation si un token existe.
   *
   * @param {void} Aucun - Utilise le token stocke.
   * @returns {Object} En-tetes HTTP d'authentification.
   */
  static getAuthorizationHeaders() {
    const accessToken = this.getAccessToken();
    if (!accessToken) {
      return {};
    }
    return { Authorization: `Bearer ${accessToken}` };
  }

  /**
   * Indique si une requete transportait un token Bearer.
   *
   * @param {RequestInit} options - Options de requete transmises a `fetch`.
   * @returns {boolean} `true` si un header Authorization Bearer existe.
   */
  static hasBearerAuthorization(options = {}) {
    const headers = options.headers || {};
    if (headers instanceof Headers) {
      return String(headers.get("Authorization") || "").startsWith("Bearer ");
    }
    return Object.entries(headers).some(
      ([key, value]) => key.toLowerCase() === "authorization" && String(value).startsWith("Bearer ")
    );
  }

  /**
   * Verifie si la reponse signale une session frontend expiree.
   *
   * @param {Response} response - Reponse HTTP retournee par le backend.
   * @param {RequestInit} options - Options de requete transmises a `fetch`.
   * @returns {boolean} `true` si le backend refuse un token Bearer envoye.
   */
  static isExpiredAuthenticatedResponse(response, options = {}) {
    return response.status === 401 && this.hasBearerAuthorization(options);
  }

  /**
   * Supprime le token expire et notifie l'application pour ouvrir la modale.
   *
   * @param {void} Aucun - Utilise `localStorage` et les evenements navigateur.
   * @returns {void} Declenche l'affichage global de reconnexion.
   */
  static handleExpiredSession() {
    if (this.hasNotifiedExpiredSession) {
      return;
    }
    this.hasNotifiedExpiredSession = true;
    this.clearAccessToken();
    window.dispatchEvent(new Event(this.sessionExpiredEventName));
  }

  /**
   * Execute une requete JSON et normalise les erreurs.
   *
   * @param {string} url - URL appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @param {RequestInit} options - Options transmises a `fetch`.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   */
  static async fetchJson(url, fallbackMessage, options = {}) {
    const response = await fetch(url, options);
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
      if (this.isExpiredAuthenticatedResponse(response, options)) {
        this.handleExpiredSession();
      }
      throw new Error(data.error || fallbackMessage);
    }
    return data;
  }

  /**
   * Decode une reponse JSON et protege contre les reponses HTML de proxy.
   *
   * @param {Response} response - Reponse HTTP retournee par `fetch`.
   * @param {string} fallbackMessage - Message d'erreur si le JSON est absent.
   * @returns {Promise<Object>} Corps JSON decode.
   */
  static async parseJsonResponse(response, fallbackMessage) {
    try {
      return await response.json();
    } catch (error) {
      throw new Error(fallbackMessage);
    }
  }
}

export default JeuxVideoApi;
