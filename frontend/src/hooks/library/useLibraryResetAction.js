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
  const waitingValidationCount = Math.max(
    0,
    Number.parseInt(options.waitingValidationCount, 10) || 0
  );

  /**
   * Demande confirmation puis appelle le backend de reset Bibliotheque.
   *
   * @returns {Promise<void>} Met a jour les messages de resultat.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const resetLibrary = async () => {
    setLibraryResetMessage("");
    setLibraryResetError("");
    const confirmed = window.confirm(buildLibraryResetConfirmationMessage(waitingValidationCount));
    if (!confirmed) {
      return;
    }

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
    isResettingLibrary,
    libraryResetError,
    libraryResetMessage,
    resetLibrary,
  };
}

/**
 * Construit le message de confirmation du reset Bibliotheque.
 *
 * @param {number} waitingValidationCount - Nombre de jeux actuellement en attente.
 * @returns {string} Message de confirmation affiche a l'administrateur.
 * @throws {void} Ne leve pas d'exception.
 */
function buildLibraryResetConfirmationMessage(waitingValidationCount = 0) {
  const baseMessage = (
    "ATTENTION : ce reset supprime et reconstruit toute la Bibliotheque globale a partir des imports utilisateur."
  );
  const waitingMessage = Number(waitingValidationCount) > 0
    ? ` ${waitingValidationCount} jeu(x) en attente seront valides automatiquement par le reset.`
    : "";
  return `${baseMessage}${waitingMessage} Confirmer le lancement ?`;
}

export { buildLibraryResetConfirmationMessage };
export default useLibraryResetAction;
