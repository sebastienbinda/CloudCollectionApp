/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-11
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook dedie au reset admin de la Bibliotheque.
 */
import { useState } from "react";
import LibraryAdminApi, { LibraryAdminApiError } from "../../services/LibraryAdminApi.js";

const RESET_STARTED_MESSAGE = (
  "Le reset de la Bibliotheque est en cours. Le resultat sera envoye par email."
);
const RESET_ALREADY_RUNNING_MESSAGE = "Un reset de la Bibliotheque est deja en cours.";

/**
 * Orchestre l'action frontend de reset admin Bibliotheque.
 *
 * @returns {Object} Etat et callback exposes a la page Configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function useLibraryResetAction(options = {}) {
  const [libraryResetMessage, setLibraryResetMessage] = useState("");
  const [libraryResetError, setLibraryResetError] = useState("");
  const [isResettingLibrary, setIsResettingLibrary] = useState(false);
  const [isLibraryResetConfirmationOpen, setIsLibraryResetConfirmationOpen] = useState(false);
  const waitingValidationCount = Math.max(
    0,
    Number.parseInt(options.waitingValidationCount, 10) || 0
  );

  /**
   * Ouvre la confirmation du reset Bibliotheque.
   *
   * @returns {Promise<void>} Met a jour les messages de resultat.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const resetLibrary = async () => {
    setLibraryResetMessage("");
    setLibraryResetError("");
    setIsLibraryResetConfirmationOpen(true);
  };

  /**
   * Confirme le reset apres affichage de la pop-up de confirmation.
   *
   * @returns {Promise<void>} Lance le reset apres fermeture de la pop-up.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const confirmLibraryReset = async () => {
    setIsLibraryResetConfirmationOpen(false);
    await launchLibraryReset();
  };

  /**
   * Annule la demande de reset depuis la pop-up de confirmation.
   *
   * @returns {void} Ferme la pop-up sans appeler le backend.
   * @throws {void} Ne leve pas d'exception.
   */
  const cancelLibraryReset = () => {
    setIsLibraryResetConfirmationOpen(false);
  };

  /**
   * Appelle le backend de reset Bibliotheque apres confirmation.
   *
   * @returns {Promise<void>} Met a jour les messages de resultat.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const launchLibraryReset = async () => {
    try {
      setIsResettingLibrary(true);
      await LibraryAdminApi.resetLibrary();
      setLibraryResetMessage(RESET_STARTED_MESSAGE);
    } catch (error) {
      if (error instanceof LibraryAdminApiError && error.status === 409) {
        setLibraryResetMessage(RESET_ALREADY_RUNNING_MESSAGE);
        return;
      }
      setLibraryResetError(
        error.message || "Impossible de lancer le reset de la Bibliotheque."
      );
    } finally {
      setIsResettingLibrary(false);
    }
  };

  return {
    cancelLibraryReset,
    confirmLibraryReset,
    isLibraryResetConfirmationOpen,
    isResettingLibrary,
    libraryResetError,
    libraryResetMessage,
    resetLibrary,
    waitingValidationCount,
  };
}

export default useLibraryResetAction;
