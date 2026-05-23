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
 * Description : hook React de la page d'ajout de jeu.
 */
import { useEffect, useState } from "react";
import AppRouting from "../../appRouting";
import AddGameChoicesApi from "../../services/AddGameChoicesApi";
import JeuxVideoApi from "../../services/JeuxVideoApi";
import WishlistAddApi from "../../services/WishlistAddApi";

const initialGameForm = AppRouting.createInitialGameForm();

/**
 * Gere le formulaire, les suggestions et la soumission d'ajout de jeu.
 *
 * @param {Object} options - Dependances de formulaire et navigation.
 * @returns {Object} Etat et callbacks de la page d'ajout.
 */
function useAddGamePage(options) {
  const [gameForm, setGameForm] = useState(initialGameForm);
  const [addGameMessage, setAddGameMessage] = useState("");
  const [addGameError, setAddGameError] = useState("");
  const [addGameColumnValues, setAddGameColumnValues] = useState({});
  const [isAddingGame, setIsAddingGame] = useState(false);

  const prepareAddGameForm = (selectedPlatform, availablePlatforms = options.platforms) => {
    setAddGameMessage("");
    setAddGameError("");
    setGameForm((previous) => ({
      ...previous,
      platform: previous.platform || selectedPlatform || availablePlatforms[0] || "",
    }));
  };

  const updateGameFormValue = (field, value) => {
    setGameForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  useEffect(() => {
    const fetchAddGameColumnValues = async () => {
      if (!options.hasAccessToken || options.currentView !== "addGame") {
        setAddGameColumnValues({});
        return;
      }

      try {
        const data = await AddGameChoicesApi.fetchChoices(gameForm.platform);
        setAddGameColumnValues(data.values_by_column || {});
      } catch (e) {
        setAddGameColumnValues({});
      }
    };

    fetchAddGameColumnValues();
  }, [options.currentView, gameForm.platform, options.odsReloadKey, options.hasAccessToken]);

  const submitNewGame = async (event) => {
    event.preventDefault();
    setAddGameMessage("");
    setAddGameError("");
    const isWishlistTarget = gameForm.addTarget === "wishlist";
    if (isWishlistTarget && !options.actionPermissions.canAddWishlistGame) return;
    if (!isWishlistTarget && !options.actionPermissions.canAddGame) return;

    try {
      setIsAddingGame(true);
      const data = isWishlistTarget
        ? await WishlistAddApi.addWishlistGame(gameForm)
        : await JeuxVideoApi.addGame(gameForm);
      setAddGameMessage(
        isWishlistTarget ? "Jeu ajoute a la liste de souhaits." : "Jeu ajoute avec succes."
      );
      setGameForm({
        ...initialGameForm,
        platform: gameForm.platform,
        addTarget: gameForm.addTarget,
      });
      options.reloadOds();
      options.reloadGames();
      if (isWishlistTarget) options.openWishlist();
      else options.openPlatform(data.item.Plateforme);
    } catch (e) {
      setAddGameError(e.message || "Impossible d'ajouter le jeu.");
    } finally {
      setIsAddingGame(false);
    }
  };

  return {
    gameForm,
    setGameForm,
    addGameColumnValues,
    addGameError,
    setAddGameError,
    addGameMessage,
    setAddGameMessage,
    isAddingGame,
    prepareAddGameForm,
    updateGameFormValue,
    submitNewGame,
  };
}

export default useAddGamePage;
