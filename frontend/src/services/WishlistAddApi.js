/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-08
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * License : Apache 2.0
 *
 * Description : service objet dedie a l'ajout de jeux dans la liste de souhaits.
 */
import JeuxVideoApi from "./JeuxVideoApi";

class WishlistAddApi {
  /**
   * Ajoute un jeu a la liste de souhaits.
   *
   * @param {Object} gameForm - Donnees du formulaire d'ajout wishlist.
   * @returns {Promise<Object>} Objet contenant le jeu ajoute.
   */
  static async addWishlistGame(gameForm) {
    return JeuxVideoApi.fetchJson(
      "/collections/JeuxVideo/wishlist/games",
      "Impossible d'ajouter le jeu a la liste de souhaits.",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...JeuxVideoApi.getAuthorizationHeaders(),
        },
        body: JSON.stringify({ ...gameForm, Console: gameForm.Console || gameForm.platform }),
      }
    );
  }
}

export default WishlistAddApi;
