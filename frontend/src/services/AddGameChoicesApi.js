/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-08
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * License : Apache 2.0
 *
 * Description : client objet des choix fusionnes du formulaire d'ajout.
 */
import JeuxVideoApi from "./JeuxVideoApi";

class AddGameChoicesApi {
  /**
   * Charge les choix fusionnes depuis le backend.
   *
   * @param {string} platform - Plateforme collection de reference.
   * @returns {Promise<Object>} Plateformes et valeurs par colonne fusionnees.
   */
  static async fetchChoices(platform) {
    const query = platform ? `?platform=${encodeURIComponent(platform)}` : "";
    return JeuxVideoApi.fetchJson(
      `/collections/JeuxVideo/add-game-choices${query}`,
      "Impossible de recuperer les choix du formulaire d'ajout."
    );
  }
}

export default AddGameChoicesApi;
