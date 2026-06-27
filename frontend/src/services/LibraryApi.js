/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend dedie aux endpoints publics Bibliotheque.
 */
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";
import AuthApi from "./AuthApi";

/**
 * Regroupe les appels publics de consultation de la Bibliotheque.
 */
class LibraryApi {
  /**
   * Charge les compteurs globaux des entites Bibliotheque.
   *
   * @returns {Promise<Object>} Compteurs `platforms`, `studios` et `games`.
   */
  static async fetchEntities() {
    return this.fetchJson("/api/library/entities", "Impossible de charger les compteurs Bibliotheque.");
  }

  /**
   * Charge la liste paginee des plateformes publiques.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `platforms`.
   */
  static async fetchPlatforms(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/platforms", criteria),
      "Impossible de charger les plateformes Bibliotheque."
    );
  }

  /**
   * Charge le detail public d'une plateforme.
   *
   * @param {string|number} platformId - Identifiant de la plateforme recherchee.
   * @returns {Promise<Object>} Objet contenant `platform`.
   */
  static async fetchPlatform(platformId) {
    return this.fetchJson(
      `/api/library/platforms/${encodeURIComponent(platformId)}`,
      "Impossible de charger la plateforme Bibliotheque."
    );
  }

  /**
   * Depose une image proposee pour une plateforme.
   *
   * @param {string|number} platformId - Identifiant de la plateforme cible.
   * @param {File} imageFile - Fichier image selectionne.
   * @returns {Promise<Object>} Objet contenant l'image creee.
   */
  static async uploadPlatformImage(platformId, imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);
    const requestOptions = {
      method: "POST",
      headers: AuthApi.getAuthorizationHeaders(),
      body: formData,
    };
    const fallbackMessage = "Impossible d'envoyer l'image de plateforme.";
    const response = await BackendAvailabilityGuard.fetch(
      `/api/library/platforms/${encodeURIComponent(platformId)}/image`,
      requestOptions
    );
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || fallbackMessage);
    }
    return data;
  }

  /**
   * Construit l'URL publique d'une image acceptee.
   *
   * @param {string|number} platformId - Identifiant de plateforme.
   * @param {string|number} imageId - Identifiant d'image.
   * @param {string|number} cacheVersion - Version de cache-busting.
   * @returns {string} URL publique de l'image.
   */
  static buildPlatformImageUrl(platformId, imageId, cacheVersion = "") {
    const baseUrl = `/api/library/platforms/${encodeURIComponent(platformId)}/image/${encodeURIComponent(imageId)}`;
    const version = String(cacheVersion || "").trim();
    return version ? `${baseUrl}?v=${encodeURIComponent(version)}` : baseUrl;
  }

  /**
   * Charge la liste paginee des studios publics.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `studios`.
   */
  static async fetchStudios(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/studios", criteria),
      "Impossible de charger les studios Bibliotheque."
    );
  }

  /**
   * Charge la liste paginee des jeux publics.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `games`.
   */
  static async fetchGames(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/games", criteria),
      "Impossible de charger les jeux Bibliotheque."
    );
  }

  /**
   * Charge le detail public d'un jeu.
   *
   * @param {string|number} gameId - Identifiant du jeu recherche.
   * @returns {Promise<Object>} Objet contenant `game`.
   */
  static async fetchGame(gameId) {
    return this.fetchJson(
      `/api/library/games/${encodeURIComponent(gameId)}`,
      "Impossible de charger le jeu Bibliotheque."
    );
  }

  /**
   * Signale un jeu comme doublon depuis une session utilisateur.
   *
   * @param {string|number} gameId - Identifiant du jeu signale.
   * @returns {Promise<Object>} Confirmation backend.
   */
  static async reportGameDuplicate(gameId) {
    const requestOptions = {
      method: "POST",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const fallbackMessage = "Impossible de signaler ce doublon.";
    const response = await BackendAvailabilityGuard.fetch(
      `/api/library/games/${encodeURIComponent(gameId)}/doublon`,
      requestOptions
    );
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || fallbackMessage);
    }
    return data;
  }

  /**
   * Construit une URL de liste Bibliotheque a partir des criteres UI.
   *
   * @param {string} path - Chemin backend appele.
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {string} URL complete avec query string optionnelle.
   */
  static buildListUrl(path, criteria = {}) {
    const query = new URLSearchParams();
    const name = String(criteria.name || "").trim();
    if (name) {
      query.set("name", name);
    }
    const platform = String(criteria.platform || "").trim();
    if (platform) {
      query.set("platform", platform);
    }
    const duplicateFlag = criteria.duplicate_flag === false
      ? "false"
      : String(criteria.duplicate_flag || "").trim();
    if (["true", "false"].includes(duplicateFlag)) {
      query.set("duplicate_flag", duplicateFlag);
    }
    if (Number.isFinite(criteria.page)) {
      query.set("page", String(criteria.page));
    }
    if (Number.isFinite(criteria.size)) {
      query.set("size", String(criteria.size));
    }

    this.normalizeSortRules(criteria.sort).forEach((sortRule) => {
      query.append("sort", `${sortRule.column},${sortRule.direction}`);
    });

    const suffix = query.toString();
    return suffix ? `${path}?${suffix}` : path;
  }

  /**
   * Normalise les criteres de tri en liste repetable compatible API.
   *
   * @param {Array|Object|string} sort - Tri demande par le hook appelant.
   * @returns {Array<Object>} Regles de tri normalisees.
   */
  static normalizeSortRules(sort) {
    const rules = Array.isArray(sort) ? sort : [sort];
    return rules
      .map((rule) => {
        if (!rule) {
          return null;
        }
        if (typeof rule === "string") {
          const [column, direction = "asc"] = rule.split(",");
          return { column, direction };
        }
        return rule;
      })
      .filter((rule) => String(rule?.column || "").trim())
      .map((rule) => ({
        column: String(rule.column).trim(),
        direction: String(rule.direction || "asc").trim().toLowerCase(),
      }));
  }

  /**
   * Execute une requete JSON publique et normalise les erreurs.
   *
   * @param {string} url - URL appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   */
  static async fetchJson(url, fallbackMessage) {
    const response = await BackendAvailabilityGuard.fetch(url);
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

export default LibraryApi;
