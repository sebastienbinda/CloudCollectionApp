/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | |__|  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-01
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook de resume admin des jeux Bibliotheque a valider.
 */
import { useCallback, useEffect, useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

const EMPTY_SUMMARY = {
  waiting_validation_count: 0,
  has_waiting_validation: false,
};

/**
 * Charge le resume admin des jeux en attente de validation.
 *
 * @param {Object} options - Options d'activation du chargement.
 * @returns {Object} Resume, etat de chargement et callback de rechargement.
 * @throws {void} Les erreurs sont exposees dans l'etat du hook.
 */
function useGameValidationSummary(options = {}) {
  const enabled = options.enabled === true;
  const [summary, setSummary] = useState(EMPTY_SUMMARY);
  const [summaryError, setSummaryError] = useState("");
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);

  const reloadGameValidationSummary = useCallback(async () => {
    if (!enabled) {
      setSummary(EMPTY_SUMMARY);
      setSummaryError("");
      return EMPTY_SUMMARY;
    }

    try {
      setIsLoadingSummary(true);
      setSummaryError("");
      const data = await LibraryAdminApi.fetchGameValidationSummary();
      const nextSummary = normalizeGameValidationSummary(data.summary);
      setSummary(nextSummary);
      return nextSummary;
    } catch (error) {
      setSummary(EMPTY_SUMMARY);
      setSummaryError(
        error.message || "Impossible de charger le resume de validation des jeux."
      );
      return EMPTY_SUMMARY;
    } finally {
      setIsLoadingSummary(false);
    }
  }, [enabled]);

  useEffect(() => {
    reloadGameValidationSummary();
  }, [reloadGameValidationSummary]);

  return {
    gameValidationSummary: summary,
    gameValidationSummaryError: summaryError,
    isLoadingGameValidationSummary: isLoadingSummary,
    reloadGameValidationSummary,
  };
}

/**
 * Normalise le payload de resume de validation des jeux.
 *
 * @param {Object|null} summary - Resume brut retourne par le backend.
 * @returns {Object} Resume utilisable par l'interface.
 * @throws {void} Ne leve pas d'exception.
 */
function normalizeGameValidationSummary(summary) {
  const waitingValidationCount = Math.max(
    0,
    Number.parseInt(summary?.waiting_validation_count, 10) || 0
  );
  return {
    waiting_validation_count: waitingValidationCount,
    has_waiting_validation: waitingValidationCount > 0,
  };
}

export { normalizeGameValidationSummary };
export default useGameValidationSummary;
