/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-22
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client frontend dedie a l'administration des utilisateurs.
 */
import AuthApi from "./AuthApi";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";
import VideoGamesApi from "./VideoGamesApi";

/**
 * Regroupe les appels frontend de gestion administrative des utilisateurs.
 */
class UsersApi {
  /**
   * Charge les utilisateurs visibles par l'administrateur courant.
   *
   * @param {Object} criteria - Criteres optionnels de recherche utilisateur.
   * @returns {Promise<Object>} Objet contenant `users`.
   */
  static async searchUsers(criteria = {}) {
    const query = new URLSearchParams();
    Object.entries(criteria).forEach(([key, value]) => {
      const normalizedValue = String(value || "").trim();
      if (normalizedValue) {
        query.set(key, normalizedValue);
      }
    });
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return VideoGamesApi.fetchJson(`/api/users${suffix}`, "Impossible de charger les utilisateurs.", {
      headers: AuthApi.getAuthorizationHeaders(),
    });
  }

  /**
   * Supprime un utilisateur.
   *
   * @param {number|string} userId - Identifiant technique de l'utilisateur.
   * @returns {Promise<void>} Promesse resolue apres suppression.
   */
  static async deleteUser(userId) {
    const requestOptions = {
      method: "DELETE",
      headers: AuthApi.getAuthorizationHeaders(),
    };
    const response = await BackendAvailabilityGuard.fetch(
      `/api/users/${encodeURIComponent(userId)}`,
      requestOptions
    );
    if (!response.ok) {
      const data = await VideoGamesApi.parseJsonResponse(
        response,
        "Impossible de supprimer l'utilisateur."
      );
      if (AuthApi.isExpiredAuthenticatedResponse(response, requestOptions)) {
        AuthApi.handleExpiredSession(response);
      }
      throw new Error(data.error || "Impossible de supprimer l'utilisateur.");
    }
  }

  /**
   * Bloque un utilisateur.
   *
   * @param {number|string} userId - Identifiant technique de l'utilisateur.
   * @returns {Promise<Object>} Objet contenant l'utilisateur modifie.
   */
  static async lockUser(userId) {
    return VideoGamesApi.fetchJson(
      `/api/users/${encodeURIComponent(userId)}/lock`,
      "Impossible de bloquer l'utilisateur.",
      {
        method: "POST",
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
  }

  /**
   * Debloque un utilisateur.
   *
   * @param {number|string} userId - Identifiant technique de l'utilisateur.
   * @returns {Promise<Object>} Objet contenant l'utilisateur modifie.
   */
  static async unlockUser(userId) {
    return VideoGamesApi.fetchJson(
      `/api/users/${encodeURIComponent(userId)}/unlock`,
      "Impossible de debloquer l'utilisateur.",
      {
        method: "POST",
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
  }

  /**
   * Valide un utilisateur en attente.
   *
   * @param {number|string} userId - Identifiant technique de l'utilisateur.
   * @returns {Promise<Object>} Objet contenant l'utilisateur modifie.
   */
  static async validateUser(userId) {
    return VideoGamesApi.fetchJson(
      `/api/users/${encodeURIComponent(userId)}/validate`,
      "Impossible de valider l'utilisateur.",
      {
        method: "POST",
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
  }
}

export default UsersApi;
