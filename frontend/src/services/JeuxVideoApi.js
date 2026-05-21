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
import AuthApi from "./AuthApi";

class JeuxVideoApi {
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
    return this.fetchJson("/collections/JeuxVideo/home", "Impossible de recuperer l'accueil.", {
      headers: AuthApi.getAuthorizationHeaders(),
    });
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
      "Impossible de recuperer les plateformes.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
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
      "Impossible de recuperer les jeux video.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
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
      "Impossible de recuperer les valeurs de colonnes.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
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
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible de supprimer le jeu.", {
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
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible de modifier le jeu.", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...AuthApi.getAuthorizationHeaders(),
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
          ...AuthApi.getAuthorizationHeaders(),
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
          ...AuthApi.getAuthorizationHeaders(),
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
      "Impossible de rechercher les jeux.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
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
      headers: AuthApi.getAuthorizationHeaders(),
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
    const response = await fetch("/collections/JeuxVideo/ods/download", requestOptions);
    if (!response.ok) {
      const data = await this.parseJsonResponse(response, "Impossible de telecharger le fichier ODS.");
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession();
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
      if (AuthApi.isExpiredAuthenticatedResponse(response, options)) {
        AuthApi.handleExpiredSession();
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
