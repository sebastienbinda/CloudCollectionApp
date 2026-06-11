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
