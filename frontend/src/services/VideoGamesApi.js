/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 */
import AuthApi from "./AuthApi.js";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard.js";

class VideoGamesApi {
  /**
   * Retourne les en-tetes d'autorisation courants.
   *
   * @param {void} Aucun - Delegue la lecture a `AuthApi`.
   * @returns {Object} En-tetes HTTP d'autorisation.
   */
  static getAuthorizationHeaders() {
    return AuthApi.getAuthorizationHeaders();
  }

  /**
   * Retourne le token Bearer courant.
   *
   * @param {void} Aucun - Delegue la lecture a `AuthApi`.
   * @returns {string} Token d'acces ou chaine vide.
   */
  static getAccessToken() {
    return AuthApi.getAccessToken();
  }

  /**
   * Retourne le profil applicatif porte par le token courant.
   *
   * @param {void} Aucun - Delegue le decodage a `AuthApi`.
   * @returns {string} Profil applicatif du token, ou `USER`.
   */
  static getAuthenticatedProfile() {
    return String(AuthApi.getAccessTokenPayload().profile || "USER").trim().toUpperCase();
  }

  /**
   * Charge le catalogue des routes accessibles expose par le backend.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Objet contenant `routes`.
   */
  static async fetchRoutes() {
    return this.fetchJson("/api/routes", "Impossible de recuperer les routes backend.", {
      headers: AuthApi.getAuthorizationHeaders(),
    });
  }

  /**
   * Charge les statistiques d'accueil.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Donnees du tableau de bord.
   */
  static async fetchHomeStats() {
    const requestOptions = {
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const [statistics, platformsPayload] = await Promise.all([
      this.fetchJson(
        "/collections/videogames",
        "Impossible de recuperer les statistiques de collection.",
        requestOptions
      ),
      this.fetchJson(
        `/collections/videogames/platforms/search?${this.buildCollectionGameSearchQuery({ wishlist: false })}`,
        "Impossible de recuperer les plateformes.",
        requestOptions
      ),
    ]);
    const collectionStatistics = this.normalizeCollectionStatistics(statistics);
    const platforms = this.normalizeCollectionPlatforms(platformsPayload.platforms || []);
    return {
      title: "Ma collection",
      first_game_date: "",
      last_game_date: "",
      totals: {
        games_count: collectionStatistics.total || 0,
        total_price: collectionStatistics.total_value || 0,
        average_price: collectionStatistics.average_value || 0,
      },
      max_platform: collectionStatistics.max_platform || "",
      platforms,
    };
  }

  /**
   * Charge la liste des plateformes.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Objet contenant `platforms`.
   */
  static async fetchPlatforms() {
    const query = this.buildCollectionGameSearchQuery({ wishlist: false });
    const data = await this.fetchJson(
      `/collections/videogames/platforms/search?${query}`,
      "Impossible de recuperer les plateformes.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
    return {
      ...data,
      platforms: this.normalizeCollectionPlatforms(data.platforms || []),
    };
  }

  /**
   * Charge les jeux de collection selon les criteres fournis.
   *
   * @param {Object|string|number} criteria - Criteres de recherche ou identifiant de plateforme.
   * @returns {Promise<Array>} Liste des jeux normalisee pour le tableau.
   */
  static async fetchGames(criteria = {}) {
    const query = this.buildCollectionGameSearchQuery(this.normalizeGameSearchCriteria(criteria));
    const data = await this.fetchJson(
      `/collections/videogames/games/search?${query}`,
      "Impossible de recuperer les jeux video.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
    return this.normalizeCollectionGames(data.games || []);
  }

  /**
   * Charge le detail d'un jeu de la collection connectee.
   *
   * @param {string|number} gameId - Identifiant du jeu recherche.
   * @returns {Promise<Object>} Objet contenant `game`.
   */
  static async fetchGame(gameId) {
    const data = await this.fetchJson(
      `/collections/videogames/games/${encodeURIComponent(gameId)}`,
      "Impossible de recuperer le jeu video.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
    return {
      ...data,
      game: this.normalizeCollectionGames(data.game ? [data.game] : [])[0] || null,
    };
  }

  /**
   * Normalise les criteres de recherche de jeux.
   *
   * @param {Object|string|number} criteria - Criteres de recherche ou identifiant plateforme.
   * @returns {Object} Criteres compatibles avec l'API backend.
   */
  static normalizeGameSearchCriteria(criteria) {
    if (typeof criteria !== "object" || criteria === null || Array.isArray(criteria)) {
      return {
        platform_id: criteria,
        wishlist: false,
      };
    }

    return criteria;
  }

  /**
   * Retourne les suggestions disponibles pour les actions futures de jeu.
   *
   * @returns {Promise<Object>} Objet contenant `values_by_column`.
   */
  static async fetchColumnValues() {
    return { values_by_column: {} };
  }

  /**
   * Appelle la route reservee pour l'ajout futur d'un jeu.
   *
   * @param {Object} gameForm - Donnees du formulaire d'ajout.
   * @returns {Promise<Object>} Objet contenant le jeu ajoute.
   */
  static async addGame(gameForm) {
    return this.fetchJson("/collections/videogames/games", "Impossible d'ajouter le jeu.", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...AuthApi.getAuthorizationHeaders(),
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
    return this.fetchJson("/collections/videogames/games", "Impossible de supprimer le jeu.", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...AuthApi.getAuthorizationHeaders(),
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
    return this.fetchJson("/collections/videogames/games", "Impossible de modifier le jeu.", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...AuthApi.getAuthorizationHeaders(),
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Recherche un jeu par nom dans toutes les plateformes.
   *
   * @param {string} query - Texte recherche dans le nom du jeu.
   * @returns {Promise<Object>} Objet contenant les resultats.
   */
  static async searchGamesByName(query) {
    const searchQuery = this.buildCollectionGameSearchQuery({
      name: query,
      wishlist: false,
    });
    const data = await this.fetchJson(
      `/collections/videogames/games/search?${searchQuery}`,
      "Impossible de rechercher les jeux.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
    return {
      ...data,
      items: this.normalizeCollectionGames(data.games || []),
    };
  }

  /**
   * Extrait les statistiques de collection reelle depuis le contrat SQL.
   *
   * @param {Object} statistics - Payload retourne par `GET /collections/videogames`.
   * @returns {Object} Section collection normalisee.
   */
  static normalizeCollectionStatistics(statistics = {}) {
    return statistics.collection || statistics;
  }

  /**
   * Construit une query string de recherche collection.
   *
   * @param {Object} criteria - Criteres de recherche.
   * @returns {string} Query string encodee.
   */
  static buildCollectionGameSearchQuery(criteria) {
    const parameters = new URLSearchParams();
    Object.entries(criteria).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") {
        return;
      }
      parameters.set(key, String(value));
    });
    return parameters.toString();
  }

  /**
   * Normalise les plateformes SQL vers le format historique des vues.
   *
   * @param {Array<Object>} platforms - Plateformes retournees par l'API SQL.
   * @returns {Array<Object>} Plateformes pretes pour l'interface.
   */
  static normalizeCollectionPlatforms(platforms) {
    return platforms.map((platform) => ({
      id: platform.id,
      name: platform.name || "",
      release_date: platform.release_date || "",
      end_date: platform.end_date || "",
      manufacturer: platform.manufacturer || "",
      description: platform.description || "",
      total_games: platform.total_games || platform.nb_games || 0,
      games_count: platform.nb_games || 0,
      total_price: platform.total_value || 0,
      average_price: platform.average_value || 0,
    }));
  }

  /**
   * Normalise les jeux SQL vers les colonnes affichees par la collection.
   *
   * @param {Array<Object>} games - Jeux retournes par l'API SQL.
   * @returns {Array<Object>} Jeux compatibles avec les composants existants.
   */
  static normalizeCollectionGames(games) {
    return games.map((game) => {
      const normalizedGame = {
        id: game.id,
        platform_id: game.platform_id,
        "Nom du jeu": game.name || "",
        Plateforme: game.platform_name || "",
        Studio: game.studio_name || "",
        "Date de sortie": game.release_date || "",
        "Date d'achat": game.buy_date || "",
        "Lieu d'achat": game.buy_location || "",
        Note: game.grade || "",
        Version: game.region || game.version || "",
        Etat: game.condition,
        Notice: game.has_manual,
        Collector: game.is_collector,
        Steelbook: game.has_steelbook,
        "Version digitale": game.is_digital,
        Region: game.region || "",
        Description: game.description || "",
      };
      if (Object.prototype.hasOwnProperty.call(game, "purchase_price")) {
        normalizedGame["Prix d'achat"] = game.purchase_price;
      }
      if (Object.prototype.hasOwnProperty.call(game, "price_unit")) {
        normalizedGame.priceUnit = game.price_unit || "";
      }
      return normalizedGame;
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
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const response = await BackendAvailabilityGuard.fetch(
      "/collections/videogames/download",
      requestOptions
    );
    if (!response.ok) {
      const data = await this.parseJsonResponse(
        response,
        "Impossible de telecharger le fichier de collection."
      );
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || "Impossible de telecharger le fichier de collection.");
    }
    const blob = await response.blob();
    const filename = this.getDownloadFilename(response) || "VideoGames.ods";
    this.saveBlob(blob, filename);
  }

  /**
   * Charge une image protegee et retourne une URL objet utilisable par CSS.
   *
   * @param {string} imageUrl - URL backend de l'image protegee.
   * @returns {Promise<string>} URL objet temporaire creee par le navigateur.
   */
  static async fetchProtectedImageObjectUrl(imageUrl) {
    const requestOptions = {
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const response = await BackendAvailabilityGuard.fetch(imageUrl, requestOptions);
    if (!response.ok) {
      const data = await this.parseJsonResponse(response, "Impossible de recuperer l'image.");
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || "Impossible de recuperer l'image.");
    }

    const blob = await response.blob();
    return window.URL.createObjectURL(blob);
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
   * Execute une requete JSON et normalise les erreurs.
   *
   * @param {string} url - URL appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @param {RequestInit} options - Options transmises a `fetch`.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   */
  static async fetchJson(url, fallbackMessage, options = {}) {
    const response = await BackendAvailabilityGuard.fetch(url, options);
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
      if (AuthApi.isExpiredAuthenticatedResponse(response, options)) {
        AuthApi.handleExpiredSession(response);
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

export default VideoGamesApi;
