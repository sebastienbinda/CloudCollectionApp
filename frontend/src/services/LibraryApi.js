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
 * Description : client frontend dedie aux endpoints publics Bibliotheque.
 */
import BackendAvailabilityGuard from "./BackendAvailabilityGuard";

/**
 * Regroupe les appels publics de consultation de la Bibliotheque.
 */
class LibraryApi {
  /**
   * Charge les compteurs globaux des entites Bibliotheque.
   *
   * @returns {Promise<Object>} Compteurs `platforms`, `studios` et `games`.
   */
  static async fetchEntities() {
    return this.fetchJson("/api/library/entities", "Impossible de charger les compteurs Bibliotheque.");
  }

  /**
   * Charge la liste paginee des plateformes publiques.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `platforms`.
   */
  static async fetchPlatforms(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/platforms", criteria),
      "Impossible de charger les plateformes Bibliotheque."
    );
  }

  /**
   * Charge la liste paginee des studios publics.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `studios`.
   */
  static async fetchStudios(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/studios", criteria),
      "Impossible de charger les studios Bibliotheque."
    );
  }

  /**
   * Charge la liste paginee des jeux publics.
   *
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {Promise<Object>} Page contenant `games`.
   */
  static async fetchGames(criteria = {}) {
    return this.fetchJson(
      this.buildListUrl("/api/library/games", criteria),
      "Impossible de charger les jeux Bibliotheque."
    );
  }

  /**
   * Construit une URL de liste Bibliotheque a partir des criteres UI.
   *
   * @param {string} path - Chemin backend appele.
   * @param {Object} criteria - Criteres de recherche, pagination et tri.
   * @returns {string} URL complete avec query string optionnelle.
   */
  static buildListUrl(path, criteria = {}) {
    const query = new URLSearchParams();
    const name = String(criteria.name || "").trim();
    if (name) {
      query.set("name", name);
    }
    if (Number.isFinite(criteria.page)) {
      query.set("page", String(criteria.page));
    }
    if (Number.isFinite(criteria.size)) {
      query.set("size", String(criteria.size));
    }

    this.normalizeSortRules(criteria.sort).forEach((sortRule) => {
      query.append("sort", `${sortRule.column},${sortRule.direction}`);
    });

    const suffix = query.toString();
    return suffix ? `${path}?${suffix}` : path;
  }

  /**
   * Normalise les criteres de tri en liste repetable compatible API.
   *
   * @param {Array|Object|string} sort - Tri demande par le hook appelant.
   * @returns {Array<Object>} Regles de tri normalisees.
   */
  static normalizeSortRules(sort) {
    const rules = Array.isArray(sort) ? sort : [sort];
    return rules
      .map((rule) => {
        if (!rule) {
          return null;
        }
        if (typeof rule === "string") {
          const [column, direction = "asc"] = rule.split(",");
          return { column, direction };
        }
        return rule;
      })
      .filter((rule) => String(rule?.column || "").trim())
      .map((rule) => ({
        column: String(rule.column).trim(),
        direction: String(rule.direction || "asc").trim().toLowerCase(),
      }));
  }

  /**
   * Execute une requete JSON publique et normalise les erreurs.
   *
   * @param {string} url - URL appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   */
  static async fetchJson(url, fallbackMessage) {
    const response = await BackendAvailabilityGuard.fetch(url);
    const data = await this.parseJsonResponse(response, fallbackMessage);
    if (!response.ok) {
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

export default LibraryApi;
