/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend de gestion proprietaire des partages de collection.
 */
import AuthApi from "./AuthApi.js";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard.js";

/**
 * Centralise les appels HTTP de gestion des partages de collection.
 */
class CollectionSharesApi {
  /**
   * Liste les partages du proprietaire connecte.
   *
   * @returns {Promise<Array<Object>>} Partages actifs, expires et revoques.
   * @throws {Error} Si le backend refuse ou ne peut traiter la requete.
   */
  static async listShares() {
    const data = await this.request("/api/collection-shares");
    return Array.isArray(data.shares) ? data.shares : [];
  }

  /**
   * Cree un partage avec les permissions demandees.
   *
   * @param {Object} payload - Duree et permissions validees par le hook.
   * @returns {Promise<Object>} Partage cree par le backend.
   * @throws {Error} Si le backend refuse ou ne peut traiter la requete.
   */
  static async createShare(payload) {
    const data = await this.request("/api/collection-shares", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return data.share;
  }

  /**
   * Revoque un partage appartenant au proprietaire connecte.
   *
   * @param {number|string} shareId - Identifiant technique du partage.
   * @returns {Promise<Object>} Partage revoque par le backend.
   * @throws {Error} Si le partage est absent ou si le backend echoue.
   */
  static async revokeShare(shareId) {
    const data = await this.request(
      `/api/collection-shares/${encodeURIComponent(shareId)}`,
      { method: "DELETE" }
    );
    return data.share;
  }

  /**
   * Execute une requete protegee et normalise ses erreurs.
   *
   * @param {string} url - Route backend cible.
   * @param {RequestInit} options - Options HTTP complementaires.
   * @returns {Promise<Object>} Corps JSON decode.
   * @throws {Error} Si la reponse HTTP est invalide ou en erreur.
   */
  static async request(url, options = {}) {
    const requestOptions = {
      ...options,
      headers: {
        ...AuthApi.getAuthorizationHeaders(),
        ...(options.headers || {}),
      },
    };
    const response = await BackendAvailabilityGuard.fetch(url, requestOptions);
    const data = await this.parseJsonResponse(response);
    if (!response.ok) {
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || "Impossible de gerer les partages de collection.");
    }
    return data;
  }

  /**
   * Decode une reponse JSON backend.
   *
   * @param {Response} response - Reponse HTTP a decoder.
   * @returns {Promise<Object>} Corps JSON ou objet vide pour une erreur non JSON.
   * @throws {Error} Si une reponse de succes ne contient pas de JSON.
   */
  static async parseJsonResponse(response) {
    try {
      return await response.json();
    } catch (error) {
      if (!response.ok) {
        return {};
      }
      throw new Error("Reponse de partage invalide.");
    }
  }
}

export default CollectionSharesApi;
