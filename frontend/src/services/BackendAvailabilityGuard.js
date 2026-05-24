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
 * Description : garde-fou frontend contre les appels backend repetes en indisponibilite.
 */

/**
 * Signale qu'un appel backend est temporairement bloque par le garde-fou.
 */
class BackendUnavailableError extends Error {
  /**
   * Construit une erreur d'indisponibilite backend.
   *
   * @param {number} retryAt - Timestamp epoch millisecondes de prochaine tentative.
   * @returns {BackendUnavailableError} Instance d'erreur d'indisponibilite.
   * @throws {void} Ne leve pas d'exception.
   */
  constructor(retryAt) {
    super("Backend temporairement indisponible. Nouvelle tentative dans quelques secondes.");
    this.name = "BackendUnavailableError";
    this.retryAt = retryAt;
  }
}

/**
 * Centralise un coupe-circuit leger pour les appels HTTP au backend.
 */
class BackendAvailabilityGuard {
  static failureThreshold = 3;
  static cooldownMilliseconds = 30000;
  static unavailableStatuses = new Set([502, 503, 504]);
  static consecutiveFailures = 0;
  static blockedUntil = 0;

  /**
   * Execute un appel `fetch` si le backend n'est pas temporairement bloque.
   *
   * @param {string|Request|URL} url - URL ou requete transmise a `fetch`.
   * @param {RequestInit} options - Options transmises a `fetch`.
   * @returns {Promise<Response>} Reponse HTTP du backend ou du proxy.
   * @throws {BackendUnavailableError} Si les appels sont temporairement suspendus.
   * @throws {Error} Si `fetch` echoue pour une autre raison.
   */
  static async fetch(url, options = {}) {
    this.ensureBackendCanBeCalled();
    try {
      const response = await window.fetch(url, options);
      this.recordResponse(response);
      return response;
    } catch (error) {
      this.recordFailedAttempt();
      if (this.isBackendBlocked()) {
        throw new BackendUnavailableError(this.blockedUntil);
      }
      throw error;
    }
  }

  /**
   * Verifie que le garde-fou autorise une nouvelle requete.
   *
   * @returns {void} Ne retourne aucune valeur.
   * @throws {BackendUnavailableError} Si la fenetre de pause est active.
   */
  static ensureBackendCanBeCalled() {
    if (this.isBackendBlocked()) {
      throw new BackendUnavailableError(this.blockedUntil);
    }
    if (this.blockedUntil > 0 && Date.now() >= this.blockedUntil) {
      this.blockedUntil = 0;
      this.consecutiveFailures = 0;
    }
  }

  /**
   * Met a jour l'etat du garde-fou selon la reponse HTTP recue.
   *
   * @param {Response} response - Reponse HTTP retournee par `fetch`.
   * @returns {void} Ne retourne aucune valeur.
   * @throws {void} Ne leve pas d'exception.
   */
  static recordResponse(response) {
    if (this.unavailableStatuses.has(response.status)) {
      this.recordFailedAttempt();
      return;
    }
    this.recordSuccessfulAttempt();
  }

  /**
   * Enregistre un appel backend abouti.
   *
   * @returns {void} Ne retourne aucune valeur.
   * @throws {void} Ne leve pas d'exception.
   */
  static recordSuccessfulAttempt() {
    this.consecutiveFailures = 0;
    this.blockedUntil = 0;
  }

  /**
   * Enregistre un echec de disponibilite backend.
   *
   * @returns {void} Ne retourne aucune valeur.
   * @throws {void} Ne leve pas d'exception.
   */
  static recordFailedAttempt() {
    this.consecutiveFailures += 1;
    if (this.consecutiveFailures >= this.failureThreshold) {
      this.blockedUntil = Date.now() + this.cooldownMilliseconds;
    }
  }

  /**
   * Indique si les appels backend sont actuellement suspendus.
   *
   * @returns {boolean} `true` si la fenetre de pause est active.
   * @throws {void} Ne leve pas d'exception.
   */
  static isBackendBlocked() {
    return this.blockedUntil > Date.now();
  }
}

export { BackendUnavailableError };
export default BackendAvailabilityGuard;
