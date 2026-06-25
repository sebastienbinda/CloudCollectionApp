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
 * Description : client frontend d'echange d'un lien de partage contre une session GUEST.
 */
import BackendAvailabilityGuard from "./BackendAvailabilityGuard.js";

/**
 * Erreur typee retournee pendant l'activation d'un partage.
 */
class CollectionShareSessionApiError extends Error {
  /**
   * Construit une erreur d'activation de partage.
   *
   * @param {string} message - Message destine a l'interface.
   * @param {number} status - Statut HTTP retourne par le backend.
   * @returns {CollectionShareSessionApiError} Erreur typee.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor(message, status = 0) {
    super(message);
    this.name = "CollectionShareSessionApiError";
    this.status = status;
  }
}

/**
 * Echange les tokens publics de partage sans reutiliser une session locale.
 */
class CollectionShareSessionApi {
  /**
   * Resout la destination autorisee par les claims GUEST.
   *
   * @param {Object} payload - Claims du Bearer GUEST nouvellement stocke.
   * @returns {{path: string, view: string}|null} Destination autorisee ou absence.
   * @throws {void} Ne leve pas d'exception.
   */
  static resolveGuestDestination(payload) {
    const permissions = payload?.permissions || {};
    if (permissions.collection === true) {
      return { path: "/collection", view: "home" };
    }
    if (permissions.wishlist === true) {
      return { path: "/wishlist", view: "wishlist" };
    }
    return null;
  }

  /**
   * Echange un token de lien contre un Bearer GUEST.
   *
   * @param {string} shareToken - Token signe extrait de l'URL publique.
   * @returns {Promise<Object>} Reponse OAuth2 de session GUEST.
   * @throws {CollectionShareSessionApiError} Si le lien est invalide ou indisponible.
   */
  static async exchangeShareToken(shareToken) {
    const response = await BackendAvailabilityGuard.fetch(
      "/api/auth/collection-share/session",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: shareToken }),
      }
    );
    const data = await this.parseJsonResponse(response);
    if (!response.ok) {
      throw new CollectionShareSessionApiError(
        data.error || "Impossible d'activer ce partage.",
        response.status
      );
    }
    if (!String(data.access_token || "").trim()) {
      throw new CollectionShareSessionApiError("Session invitee invalide.", response.status);
    }
    return data;
  }

  /**
   * Decode une reponse JSON en conservant son statut HTTP.
   *
   * @param {Response} response - Reponse backend a decoder.
   * @returns {Promise<Object>} Corps JSON ou objet vide en cas d'erreur non JSON.
   * @throws {CollectionShareSessionApiError} Si un succes ne contient pas de JSON.
   */
  static async parseJsonResponse(response) {
    try {
      return await response.json();
    } catch (error) {
      if (!response.ok) {
        return {};
      }
      throw new CollectionShareSessionApiError("Reponse de partage invalide.", response.status);
    }
  }
}

export { CollectionShareSessionApiError };
export default CollectionShareSessionApi;
