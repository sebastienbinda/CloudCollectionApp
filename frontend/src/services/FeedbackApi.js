/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : client frontend pour les retours utilisateurs.
 */
import AuthApi from "./AuthApi";
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";

/**
 * Regroupe les appels HTTP lies aux retours utilisateurs.
 */
class FeedbackApi {
  /**
   * Envoie un retour utilisateur authentifie au backend.
   *
   * @param {Object} payload - Donnees du formulaire de retour.
   * @returns {Promise<Object>} Issue GitHub creee par le backend.
   * @throws {Error} Si le retour ne peut pas etre envoye.
   */
  static async submitFeedback(payload) {
    const response = await BackendAvailabilityGuard.fetch("/api/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...AuthApi.getAuthorizationHeaders(),
      },
      body: JSON.stringify(payload),
    });
    const data = await this.parseJson(response);
    if (!response.ok) {
      throw new Error(data.error || "Impossible d'envoyer le retour.");
    }
    return data.feedback || {};
  }

  /**
   * Parse une reponse JSON sans propager les erreurs de format.
   *
   * @param {Response} response - Reponse HTTP recue.
   * @returns {Promise<Object>} Payload JSON ou objet vide.
   * @throws {void} Ne leve pas d'exception.
   */
  static async parseJson(response) {
    try {
      return await response.json();
    } catch {
      return {};
    }
  }
}

export default FeedbackApi;
