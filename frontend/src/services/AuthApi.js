/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-21
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend dedie a l'authentification et a l'inscription.
 */

/**
 * Regroupe les appels et l'etat frontend lies a l'authentification.
 */
class AuthApi {
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
   * Cree un utilisateur applicatif sans token Bearer.
   *
   * @param {string} email - Adresse email du compte a creer.
   * @param {string} password - Mot de passe brut transmis au backend.
   * @returns {Promise<Object>} Donnees publiques de l'utilisateur cree.
   */
  static async registerUser(email, password) {
    return this.fetchJson("/api/auth/register", "Inscription impossible.", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
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
      AuthApi.clearAccessToken();
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
    return [401, 403].includes(response.status) && this.hasBearerAuthorization(options);
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
   * Execute une requete JSON d'authentification et normalise les erreurs.
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

export default AuthApi;
