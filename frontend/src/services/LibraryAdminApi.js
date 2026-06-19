/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-11
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend dedie aux actions admin Bibliotheque.
 */
import AuthApi from "./AuthApi";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";

/**
 * Represente une erreur exploitable par l'interface admin Bibliotheque.
 */
class LibraryAdminApiError extends Error {
  /**
   * Construit une erreur API d'administration Bibliotheque.
   *
   * @param {string} message - Message lisible par l'interface.
   * @param {number} status - Statut HTTP retourne par le backend.
   * @param {Object} details - Corps JSON backend complementaire.
   * @returns {LibraryAdminApiError} Instance d'erreur typee.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor(message, status = 0, details = {}) {
    super(message);
    this.name = "LibraryAdminApiError";
    this.status = status;
    this.details = details;
  }
}

/**
 * Regroupe les appels admin lies a la Bibliotheque globale.
 */
class LibraryAdminApi {
  /**
   * Liste les images de plateformes a moderer.
   *
   * @param {Object} criteria - Pagination, filtres et tri de la liste.
   * @returns {Promise<Object>} Images et informations de page.
   * @throws {LibraryAdminApiError} Si la liste est refusee ou impossible.
   */
  static async listPlatformImages(criteria = {}) {
    const requestOptions = {
      method: "GET",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const fallbackMessage = "Impossible de charger les images de plateformes.";
    const response = await BackendAvailabilityGuard.fetch(
      this.buildPlatformImagesUrl(criteria),
      requestOptions
    );
    const data = await this.parseJsonResponse(response, fallbackMessage);

    if (!response.ok) {
      throw this.createErrorFromResponse(response, data, fallbackMessage, requestOptions);
    }
    return data;
  }

  /**
   * Lance un reset asynchrone de la Bibliotheque globale.
   *
   * @returns {Promise<Object>} Payload de job retourne par le backend.
   * @throws {LibraryAdminApiError} Si le reset est refuse ou impossible.
   */
  static async resetLibrary() {
    const requestOptions = {
      method: "POST",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const fallbackMessage = "Impossible de lancer le reset de la Bibliotheque.";
    const response = await BackendAvailabilityGuard.fetch("/api/library/reset", requestOptions);
    const data = await this.parseJsonResponse(response, fallbackMessage);

    if (!response.ok) {
      throw this.createErrorFromResponse(response, data, fallbackMessage, requestOptions);
    }
    return data;
  }

  /**
   * Synchronise le catalogue plateformes SQL depuis les CSV backend.
   *
   * @returns {Promise<Object>} Compteurs de plateformes et alias ajoutes.
   * @throws {LibraryAdminApiError} Si la synchronisation est refusee ou impossible.
   */
  static async syncPlatformCatalog() {
    const requestOptions = {
      method: "POST",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const fallbackMessage = "Impossible de mettre a jour le catalogue plateformes.";
    const response = await BackendAvailabilityGuard.fetch(
      "/api/library/platform-catalog/sync",
      requestOptions
    );
    const data = await this.parseJsonResponse(response, fallbackMessage);

    if (!response.ok) {
      throw this.createErrorFromResponse(response, data, fallbackMessage, requestOptions);
    }
    return data;
  }

  /**
   * Modifie le statut d'une image de plateforme.
   *
   * @param {string|number} platformId - Identifiant de plateforme.
   * @param {string|number} imageId - Identifiant d'image.
   * @param {string} status - Statut cible accepte par le backend.
   * @returns {Promise<Object>} Image moderee retournee par le backend.
   * @throws {LibraryAdminApiError} Si la mise a jour est refusee ou impossible.
   */
  static async updatePlatformImageStatus(platformId, imageId, status) {
    return this.updatePlatformImage(
      `/api/library/platforms/${encodeURIComponent(platformId)}/image/` +
        `${encodeURIComponent(imageId)}/status/${encodeURIComponent(status)}`,
      "Impossible de modifier le statut de l'image de plateforme."
    );
  }

  /**
   * Modifie le type d'une image de plateforme.
   *
   * @param {string|number} platformId - Identifiant de plateforme.
   * @param {string|number} imageId - Identifiant d'image.
   * @param {string} imageType - Type cible accepte par le backend.
   * @returns {Promise<Object>} Image moderee retournee par le backend.
   * @throws {LibraryAdminApiError} Si la mise a jour est refusee ou impossible.
   */
  static async updatePlatformImageType(platformId, imageId, imageType) {
    return this.updatePlatformImage(
      `/api/library/platforms/${encodeURIComponent(platformId)}/image/` +
        `${encodeURIComponent(imageId)}/type/${encodeURIComponent(imageType)}`,
      "Impossible de modifier le type de l'image de plateforme."
    );
  }

  /**
   * Appelle un endpoint de mise a jour d'image de plateforme.
   *
   * @param {string} url - URL backend a appeler.
   * @param {string} fallbackMessage - Message de repli pour l'interface.
   * @returns {Promise<Object>} Payload JSON de mise a jour.
   * @throws {LibraryAdminApiError} Si la mise a jour est refusee ou impossible.
   */
  static async updatePlatformImage(url, fallbackMessage) {
    const requestOptions = {
      method: "PUT",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const response = await BackendAvailabilityGuard.fetch(url, requestOptions);
    const data = await this.parseJsonResponse(response, fallbackMessage);

    if (!response.ok) {
      throw this.createErrorFromResponse(response, data, fallbackMessage, requestOptions);
    }
    return data;
  }

  /**
   * Construit l'URL de liste admin des images de plateformes.
   *
   * @param {Object} criteria - Criteres de liste a encoder.
   * @returns {string} URL backend avec chaine de requete.
   * @throws {void} Ne leve pas d'exception.
   */
  static buildPlatformImagesUrl(criteria = {}) {
    const parameters = new URLSearchParams();
    parameters.set("page", String(criteria.page || 0));
    parameters.set("size", String(criteria.size || 10));
    if (criteria.status) {
      parameters.set("status", criteria.status);
    }
    if (criteria.platform) {
      parameters.set("platform", criteria.platform);
    }
    if (criteria.sort) {
      parameters.append("sort", criteria.sort);
    }
    return `/api/library/platforms/images?${parameters.toString()}`;
  }

  /**
   * Decode une reponse JSON backend.
   *
   * @param {Response} response - Reponse HTTP retournee par `fetch`.
   * @param {string} fallbackMessage - Message utilise si le corps est inexploitable.
   * @returns {Promise<Object>} Corps JSON decode ou objet vide.
   * @throws {LibraryAdminApiError} Si une reponse de succes ne contient pas de JSON.
   */
  static async parseJsonResponse(response, fallbackMessage) {
    try {
      return await response.json();
    } catch (error) {
      if (!response.ok) {
        return {};
      }
      throw new LibraryAdminApiError(fallbackMessage, response.status);
    }
  }

  /**
   * Cree une erreur typee depuis une reponse backend.
   *
   * @param {Response} response - Reponse HTTP en erreur.
   * @param {Object} data - Corps JSON backend deja decode.
   * @param {string} fallbackMessage - Message de repli.
   * @param {RequestInit} requestOptions - Options utilisees par la requete.
   * @returns {LibraryAdminApiError} Erreur exploitable par le hook.
   * @throws {void} Ne leve pas d'exception.
   */
  static createErrorFromResponse(response, data = {}, fallbackMessage = "", requestOptions = {}) {
    if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
      AuthApi.handleExpiredSession();
    }
    return new LibraryAdminApiError(
      data.error || fallbackMessage,
      response.status,
      data
    );
  }
}

export { LibraryAdminApiError };
export default LibraryAdminApi;
