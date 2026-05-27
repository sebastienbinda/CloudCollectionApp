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
 * Description : hook de gestion des mutations de jeux d'une plateforme.
 */
import { useState } from "react";
import VideoGamesApi from "../services/VideoGamesApi";

/**
 * Gere la suppression et la modification des jeux de plateforme.
 *
 * @param {string} selectedPlatform - Plateforme courante.
 * @param {Function} reloadOds - Callback de rechargement des statistiques collection.
 * @param {Function} reloadGames - Callback de rechargement des jeux.
 * @returns {Object} Etat et actions de mutation des jeux.
 */
function usePlatformGameMutations(selectedPlatform, reloadOds, reloadGames) {
  const [deleteGameMessage, setDeleteGameMessage] = useState("");
  const [deleteGameError, setDeleteGameError] = useState("");
  const [editingGame, setEditingGame] = useState(null);
  const [isSavingGame, setIsSavingGame] = useState(false);

  /**
   * Efface les messages de mutation.
   *
   * @param {void} Aucun - Utilise l'etat local du hook.
   * @returns {void} Vide les messages de succes et d'erreur.
   */
  const clearDeleteGameFeedback = () => {
    setDeleteGameMessage("");
    setDeleteGameError("");
  };

  /**
   * Ouvre le formulaire de modification.
   *
   * @param {Object} game - Jeu selectionne.
   * @returns {void} Stocke le jeu en cours de modification.
   */
  const openEditGame = (game) => {
    clearDeleteGameFeedback();
    setEditingGame(game);
  };

  /**
   * Ferme le formulaire de modification.
   *
   * @param {void} Aucun - Utilise l'etat local du hook.
   * @returns {void} Annule la modification courante.
   */
  const cancelEditGame = () => setEditingGame(null);

  /**
   * Supprime un jeu de la plateforme courante puis recharge les donnees.
   *
   * @param {Object} game - Jeu de plateforme a supprimer.
   * @returns {Promise<void>} Vide les cellules du jeu et actualise l'interface.
   */
  const deletePlatformGame = async (game) => {
    const gameName = game["Nom du jeu"] || "ce jeu";
    if (!window.confirm(`Confirmer la suppression de "${gameName}" ?`)) return;
    clearDeleteGameFeedback();
    try {
      await VideoGamesApi.deleteGame({ platform: selectedPlatform, ...game });
      setDeleteGameMessage(`${gameName} a ete supprime de ${selectedPlatform}.`);
      reloadOds();
      reloadGames();
    } catch (e) {
      const message = e.message || "Impossible de supprimer le jeu.";
      setDeleteGameError(message);
      window.alert(message);
    }
  };

  /**
   * Enregistre les modifications d'un jeu.
   *
   * @param {Object} originalGame - Jeu original identifiant l'entree collection.
   * @param {Object} updatedGame - Donnees modifiees par l'utilisateur.
   * @returns {Promise<void>} Modifie le jeu et actualise l'interface.
   */
  const saveEditedGame = async (originalGame, updatedGame) => {
    clearDeleteGameFeedback();
    try {
      setIsSavingGame(true);
      await VideoGamesApi.updateGame({ platform: selectedPlatform, original: originalGame, updated: updatedGame });
      setEditingGame(null);
      setDeleteGameMessage(`${updatedGame["Nom du jeu"]} a ete modifie.`);
      reloadOds();
      reloadGames();
    } catch (e) {
      const message = e.message || "Impossible de modifier le jeu.";
      setDeleteGameError(message);
      window.alert(message);
    } finally {
      setIsSavingGame(false);
    }
  };

  return {
    deleteGameMessage, deleteGameError, editingGame, isSavingGame,
    clearDeleteGameFeedback, openEditGame, cancelEditGame,
    deletePlatformGame, saveEditedGame,
  };
}

export default usePlatformGameMutations;
