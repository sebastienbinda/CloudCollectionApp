/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend dedie a la collection de l'utilisateur connecte.
 */
import AuthApi from "./AuthApi";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";

/**
 * Represente une erreur exploitable par l'interface de collection utilisateur.
 */
class UserCollectionApiError extends Error {
  /**
   * Construit une erreur API de collection utilisateur.
   *
   * @param {string} code - Code fonctionnel stable exploitable par l'interface.
   * @param {string} message - Message lisible retourne par l'API ou par le client.
   * @param {number} status - Statut HTTP de la reponse backend.
   * @param {Object} details - Donnees backend complementaires.
   * @returns {UserCollectionApiError} Instance d'erreur typee.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor(code, message, status = 0, details = {}) {
    super(message);
    this.name = "UserCollectionApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Regroupe les appels frontend lies a la collection de l'utilisateur connecte.
 */
class UserCollectionApi {
  static ERROR_CODES = Object.freeze({
    INVALID_FILE: "invalid_file",
    INVALID_CONFIGURATION: "invalid_configuration",
    FILE_TOO_LARGE: "file_too_large",
    COLLECTION_ALREADY_IMPORTED: "collection_already_imported",
    UNAUTHORIZED: "unauthorized",
    UNEXPECTED: "unexpected_error",
  });

  static errorMessagesByCode = Object.freeze({
    [UserCollectionApi.ERROR_CODES.INVALID_FILE]: "Le fichier de collection est invalide.",
    [UserCollectionApi.ERROR_CODES.INVALID_CONFIGURATION]: "La configuration d'import est invalide.",
    [UserCollectionApi.ERROR_CODES.FILE_TOO_LARGE]: "Le fichier de collection est trop volumineux.",
    [UserCollectionApi.ERROR_CODES.COLLECTION_ALREADY_IMPORTED]: "Une collection a deja ete importee.",
    [UserCollectionApi.ERROR_CODES.UNAUTHORIZED]: "Vous devez etre connecte pour acceder a votre collection.",
    [UserCollectionApi.ERROR_CODES.UNEXPECTED]: "Une erreur inattendue est survenue.",
  });

  /**
   * Charge le statut de collection de l'utilisateur connecte.
   *
   * @param {void} Aucun - Appelle l'API backend avec le token courant.
   * @returns {Promise<Object>} Objet contenant `has_collection`.
   * @throws {UserCollectionApiError} Si le backend refuse ou ne peut pas traiter la requete.
   */
  static async fetchCurrentCollectionStatus() {
    return this.fetchJson(
      "/api/users/me/collection",
      "Impossible de recuperer le statut de votre collection.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
  }

  /**
   * Importe le fichier de collection de l'utilisateur connecte.
   *
   * @param {File|Blob} collectionFile - Fichier selectionne par l'utilisateur.
   * @param {Object} collectionFileDescription - Configuration validee cote frontend.
   * @returns {Promise<Object>} Compteurs d'import retournes par le backend.
   * @throws {UserCollectionApiError} Si le fichier est invalide, trop volumineux, deja importe ou refuse.
   */
  static async importCollection(collectionFile, collectionFileDescription) {
    const formData = new FormData();
    formData.append("collection_file", collectionFile);
    formData.append("collection_file_description", JSON.stringify(collectionFileDescription));

    return this.fetchJson("/api/users/import", "Impossible d'importer votre collection.", {
      method: "POST",
      headers: AuthApi.getAuthorizationHeaders(),
      body: formData,
    });
  }

  /**
   * Execute une requete JSON de collection utilisateur et type les erreurs.
   *
   * @param {string} url - URL backend appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @param {RequestInit} options - Options transmises a `fetch`.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   * @throws {UserCollectionApiError} Si la reponse HTTP est en erreur ou invalide.
   */
  static async fetchJson(url, fallbackMessage, options = {}) {
    const response = await BackendAvailabilityGuard.fetch(url, options);
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
      throw this.createErrorFromResponse(response, data, fallbackMessage, options);
    }
    return data;
  }

  /**
   * Decode une reponse JSON en conservant les statuts d'erreur HTTP.
   *
   * @param {Response} response - Reponse HTTP retournee par `fetch`.
   * @param {string} fallbackMessage - Message d'erreur si le JSON de succes est absent.
   * @returns {Promise<Object>} Corps JSON decode ou objet vide pour une erreur non JSON.
   * @throws {UserCollectionApiError} Si une reponse de succes ne contient pas de JSON exploitable.
   */
  static async parseJsonResponse(response, fallbackMessage) {
    try {
      return await response.json();
    } catch (error) {
      if (!response.ok) {
        return {};
      }
      throw new UserCollectionApiError(
        this.ERROR_CODES.UNEXPECTED,
        fallbackMessage,
        response.status
      );
    }
  }

  /**
   * Cree une erreur API typee a partir d'une reponse backend.
   *
   * @param {Response} response - Reponse HTTP en erreur.
   * @param {Object} data - Corps JSON backend deja decode.
   * @param {string} fallbackMessage - Message utilise par defaut.
   * @param {RequestInit} options - Options de requete permettant de detecter une session expiree.
   * @returns {UserCollectionApiError} Erreur typee pour l'interface.
   * @throws {void} Ne leve pas d'exception.
   */
  static createErrorFromResponse(response, data = {}, fallbackMessage = "", options = {}) {
    if (AuthApi.isExpiredAuthenticatedResponse(response, options)) {
      AuthApi.handleExpiredSession();
    }

    const code = this.getErrorCodeForStatus(response.status);
    const defaultMessage = this.errorMessagesByCode[code] || fallbackMessage;
    return new UserCollectionApiError(
      code,
      data.error || defaultMessage || this.errorMessagesByCode[this.ERROR_CODES.UNEXPECTED],
      response.status,
      data
    );
  }

  /**
   * Convertit un statut HTTP backend en code d'erreur fonctionnel.
   *
   * @param {number} status - Statut HTTP retourne par le backend.
   * @returns {string} Code d'erreur stable exploitable par l'interface.
   * @throws {void} Ne leve pas d'exception.
   */
  static getErrorCodeForStatus(status) {
    if ([401, 403].includes(status)) {
      return this.ERROR_CODES.UNAUTHORIZED;
    }
    if (status === 400) {
      return this.ERROR_CODES.INVALID_FILE;
    }
    if (status === 422) {
      return this.ERROR_CODES.INVALID_CONFIGURATION;
    }
    if (status === 409) {
      return this.ERROR_CODES.COLLECTION_ALREADY_IMPORTED;
    }
    if (status === 413) {
      return this.ERROR_CODES.FILE_TOO_LARGE;
    }
    return this.ERROR_CODES.UNEXPECTED;
  }
}

export { UserCollectionApiError };
export default UserCollectionApi;
