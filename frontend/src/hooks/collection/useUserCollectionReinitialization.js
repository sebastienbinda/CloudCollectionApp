/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-07
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook dedie a la reinitialisation de collection utilisateur.
 */
import { useState } from "react";
import UserCollectionApi from "../../services/UserCollectionApi";
import getUserCollectionErrorMessage from "./userCollectionImportMessages";

/**
 * Orchestre l'action frontend de reinitialisation de collection.
 *
 * @param {Object} options - Callbacks de rafraichissement et navigation.
 * @returns {Object} Etat et action de reinitialisation exposes a la page Configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function useUserCollectionReinitialization(options) {
  const [reinitializationError, setReinitializationError] = useState("");
  const [isReinitializingCollection, setIsReinitializingCollection] = useState(false);

  /**
   * Demande confirmation puis appelle le backend de reinitialisation.
   *
   * @param {void} Aucun - Utilise les callbacks fournis au hook.
   * @returns {Promise<void>} Redirige vers l'import quand la reinitialisation reussit.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const reinitializeCollection = async () => {
    setReinitializationError("");
    const confirmed = window.confirm(
      "Confirmer la reinitialisation de votre collection ? Cette action supprimera la collection actuelle et son fichier serveur."
    );
    if (!confirmed) {
      return;
    }

    try {
      setIsReinitializingCollection(true);
      await UserCollectionApi.reinitializeCollection();
      options.reloadOds();
      options.reloadGames();
      options.onCollectionReinitialized();
      options.openCollectionOnboarding();
    } catch (error) {
      setReinitializationError(getUserCollectionErrorMessage(error));
    } finally {
      setIsReinitializingCollection(false);
    }
  };

  return {
    isReinitializingCollection,
    reinitializationError,
    reinitializeCollection,
  };
}

export default useUserCollectionReinitialization;
