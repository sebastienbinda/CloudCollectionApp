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
 * Description : hook React de la page liste de souhaits.
 */
import VideoGamesApi from "../../services/VideoGamesApi";
import useWishlistGameMutations from "../useWishlistGameMutations";

/**
 * Gere les actions specifiques a la liste de souhaits.
 *
 * @param {Object} options - Dependances de rechargement de la wishlist.
 * @returns {Object} Mutations et callbacks wishlist.
 */
function useWishlistPage(options) {
  const mutations = useWishlistGameMutations(options.reloadOds, options.reloadGames);

  const addWishlistGameToPlatform = async (gamePayload) => {
    const data = await VideoGamesApi.addGame(gamePayload);
    options.reloadOds();
    options.reloadGames();
    return data;
  };

  const deleteWishlistGame = async (game) => {
    const data = await VideoGamesApi.deleteWishlistGame(game);
    options.reloadOds();
    options.reloadGames();
    return data;
  };

  return {
    addWishlistGameToPlatform,
    deleteWishlistGame,
    ...mutations,
  };
}

export default useWishlistPage;
