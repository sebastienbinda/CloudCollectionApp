/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-06
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook de gestion des modifications des jeux de la liste de souhaits.
 */
import { useState } from "react";
import JeuxVideoApi from "../services/JeuxVideoApi";

/**
 * Gere l'edition des jeux de la liste de souhaits.
 *
 * @param {Function} reloadOds - Callback de rechargement des statistiques ODS.
 * @param {Function} reloadGames - Callback de rechargement des jeux.
 * @returns {Object} Etat et actions de modification wishlist.
 */
function useWishlistGameMutations(reloadOds, reloadGames) {
  const [editingWishlistGame, setEditingWishlistGame] = useState(null);
  const [isSavingWishlistGame, setIsSavingWishlistGame] = useState(false);

  /**
   * Ouvre le formulaire de modification wishlist.
   *
   * @param {Object} game - Jeu wishlist selectionne.
   * @returns {void} Stocke le jeu en cours de modification.
   */
  const openEditWishlistGame = (game) => setEditingWishlistGame(game);

  /**
   * Ferme le formulaire de modification wishlist.
   *
   * @param {void} Aucun - Utilise l'etat local du hook.
   * @returns {void} Annule la modification courante.
   */
  const cancelEditWishlistGame = () => setEditingWishlistGame(null);

  /**
   * Enregistre les modifications d'un jeu wishlist.
   *
   * @param {Object} originalGame - Jeu original identifiant la ligne ODS.
   * @param {Object} updatedGame - Donnees modifiees par l'utilisateur.
   * @returns {Promise<Object>} Reponse API de modification wishlist.
   */
  const saveEditedWishlistGame = async (originalGame, updatedGame) => {
    try {
      setIsSavingWishlistGame(true);
      const data = await JeuxVideoApi.updateWishlistGame({
        original: originalGame,
        updated: updatedGame,
      });
      setEditingWishlistGame(null);
      reloadOds();
      reloadGames();
      return data;
    } finally {
      setIsSavingWishlistGame(false);
    }
  };

  return {
    editingWishlistGame,
    isSavingWishlistGame,
    openEditWishlistGame,
    cancelEditWishlistGame,
    saveEditedWishlistGame,
  };
}

export default useWishlistGameMutations;
