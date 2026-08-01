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
import LibraryApi from "../../services/LibraryApi";

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
      const nextSummary = await loadGameValidationSummaryWithFallback();
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
 * Charge le compteur admin avec un repli sur la liste filtree des jeux.
 *
 * @returns {Promise<Object>} Resume normalise du nombre de jeux en attente.
 * @throws {Error} Si les deux lectures echouent.
 */
async function loadGameValidationSummaryWithFallback() {
  try {
    const data = await LibraryAdminApi.fetchGameValidationSummary();
    const summary = normalizeGameValidationSummary(data.summary);
    if (summary.waiting_validation_count > 0) {
      return summary;
    }
    return loadGameValidationSummaryFromGameList(summary);
  } catch {
    return loadGameValidationSummaryFromGameList();
  }
}

/**
 * Compte les jeux en attente depuis le total de la liste admin filtree.
 *
 * @param {Object} defaultSummary - Resume deja obtenu par l'endpoint dedie.
 * @returns {Promise<Object>} Resume confirme par la liste admin.
 * @throws {Error} Si la liste filtree est indisponible.
 */
async function loadGameValidationSummaryFromGameList(defaultSummary = EMPTY_SUMMARY) {
  const data = await LibraryApi.fetchGames({
    page: 0,
    size: 1,
    status: "WAITING_VALIDATION",
  });
  const fallbackCount = Number.parseInt(data.page?.totalElements, 10);
  if (!Number.isFinite(fallbackCount) || fallbackCount <= 0) {
    return defaultSummary;
  }
  return normalizeGameValidationSummary({
    waiting_validation_count: fallbackCount,
  });
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

export {
  loadGameValidationSummaryFromGameList,
  normalizeGameValidationSummary,
};
export default useGameValidationSummary;
