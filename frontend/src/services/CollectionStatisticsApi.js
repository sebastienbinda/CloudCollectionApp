/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : client API des statistiques detaillees de collection.
 */
import AuthApi from "./AuthApi.js";
import VideoGamesApi from "./VideoGamesApi.js";

class CollectionStatisticsApi {
  /**
   * Charge les statistiques detaillees de collection.
   *
   * @returns {Promise<Object>} Statistiques normalisees.
   */
  static async fetchStatistics(options = {}) {
    const queryParameters = new URLSearchParams();
    if (options.platformId) {
      queryParameters.set("platform_id", String(options.platformId));
    }
    const queryString = queryParameters.toString();
    const data = await VideoGamesApi.fetchJson(
      `/collections/statistics${queryString ? `?${queryString}` : ""}`,
      "Impossible de recuperer les statistiques detaillees.",
      {
        headers: AuthApi.getAuthorizationHeaders(),
      }
    );
    return this.normalizeStatistics(data);
  }

  /**
   * Normalise le payload backend pour l'affichage frontend.
   *
   * @param {Object} statistics - Payload retourne par le backend.
   * @returns {Object} Statistiques normalisees.
   */
  static normalizeStatistics(statistics = {}) {
    return {
      totalGames: Number(statistics.total_games || 0),
      platformDistribution: this.normalizeCountRows(
        statistics.platform_distribution,
        "platform_name"
      ),
      releaseYearDistribution: this.normalizeYearRows(statistics.release_year_distribution),
      purchaseYearDistribution: this.normalizeYearRows(statistics.purchase_year_distribution),
      topRatedGames: Array.isArray(statistics.top_rated_games)
        ? statistics.top_rated_games.map((game) => ({
            id: game.id,
            name: game.name || "",
            platformName: game.platform_name || "",
            releaseDate: game.release_date || "",
            buyDate: game.buy_date || "",
            grade: game.grade || "",
            gradeNormalized: Number(game.grade_normalized || 0),
          }))
        : [],
    };
  }

  /**
   * Normalise des lignes de repartition nommee.
   *
   * @param {Array<Object>} rows - Lignes backend.
   * @param {string} labelField - Champ contenant le libelle.
   * @returns {Array<Object>} Lignes normalisees.
   */
  static normalizeCountRows(rows, labelField) {
    return Array.isArray(rows)
      ? rows.map((row) => ({
          id: row.platform_id || row.year || row[labelField],
          label: row[labelField] || "",
          gamesCount: Number(row.games_count || 0),
          ratio: Number(row.ratio || 0),
        }))
      : [];
  }

  /**
   * Normalise des lignes de repartition annuelle.
   *
   * @param {Array<Object>} rows - Lignes backend.
   * @returns {Array<Object>} Annees normalisees.
   */
  static normalizeYearRows(rows) {
    return Array.isArray(rows)
      ? rows.map((row) => ({
          id: row.year,
          label: String(row.year || ""),
          year: Number(row.year || 0),
          gamesCount: Number(row.games_count || 0),
        }))
      : [];
  }
}

export default CollectionStatisticsApi;
