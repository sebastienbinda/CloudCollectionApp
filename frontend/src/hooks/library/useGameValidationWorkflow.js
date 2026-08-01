/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-01
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook de selection admin des jeux Bibliotheque en validation.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi.js";

/**
 * Orchestre les actions admin de validation/refus sur la liste des jeux.
 *
 * @param {Object} options - Etat de liste et callbacks de rafraichissement.
 * @returns {Object|null} Workflow de selection ou absence si desactive.
 * @throws {void} Les erreurs sont exposees dans l'etat du hook.
 */
function useGameValidationWorkflow(options = {}) {
  const enabled = options.enabled === true;
  const rows = Array.isArray(options.rows) ? options.rows : [];
  const reloadList = options.reloadList;
  const reloadSummary = options.reloadSummary;
  const [selectedGameIds, setSelectedGameIds] = useState([]);
  const [validationActionMessage, setValidationActionMessage] = useState("");
  const [validationActionError, setValidationActionError] = useState("");
  const [isRunningValidationAction, setIsRunningValidationAction] = useState(false);

  const visibleWaitingValidationGameIds = useMemo(
    () => rows
      .filter((game) => String(game.status || "").toUpperCase() === "WAITING_VALIDATION")
      .map((game) => game.id)
      .filter((gameId) => gameId !== undefined && gameId !== null),
    [rows]
  );
  const selectedVisibleGameIds = useMemo(
    () => selectedGameIds.filter((gameId) => visibleWaitingValidationGameIds.includes(gameId)),
    [selectedGameIds, visibleWaitingValidationGameIds]
  );
  const areAllVisibleWaitingGamesSelected = (
    visibleWaitingValidationGameIds.length > 0 &&
    selectedVisibleGameIds.length === visibleWaitingValidationGameIds.length
  );

  useEffect(() => {
    if (!enabled) {
      setSelectedGameIds([]);
      setValidationActionMessage("");
      setValidationActionError("");
      return;
    }
    setSelectedGameIds((currentIds) => (
      currentIds.filter((gameId) => visibleWaitingValidationGameIds.includes(gameId))
    ));
  }, [enabled, visibleWaitingValidationGameIds]);

  const clearSelection = useCallback(() => {
    setSelectedGameIds([]);
  }, []);

  const toggleGameSelection = useCallback((gameId) => {
    setSelectedGameIds((currentIds) => (
      currentIds.includes(gameId)
        ? currentIds.filter((selectedId) => selectedId !== gameId)
        : [...currentIds, gameId]
    ));
  }, []);

  const toggleVisibleGameSelection = useCallback(() => {
    setSelectedGameIds((currentIds) => {
      if (visibleWaitingValidationGameIds.length === 0) {
        return [];
      }
      const allVisibleSelected = visibleWaitingValidationGameIds.every(
        (gameId) => currentIds.includes(gameId)
      );
      if (allVisibleSelected) {
        return currentIds.filter((gameId) => !visibleWaitingValidationGameIds.includes(gameId));
      }
      return [...new Set([...currentIds, ...visibleWaitingValidationGameIds])];
    });
  }, [visibleWaitingValidationGameIds]);

  const runValidationSelectionAction = useCallback(async (action) => {
    const selectedCount = selectedGameIds.length;
    if (selectedCount === 0) {
      return;
    }
    const verb = action === "validate" ? "valider" : "refuser";
    if (!window.confirm(`Confirmer: ${verb} ${selectedCount} jeu(x) en attente de validation ?`)) {
      return;
    }

    try {
      setIsRunningValidationAction(true);
      setValidationActionError("");
      setValidationActionMessage("");
      const data = action === "validate"
        ? await LibraryAdminApi.validateGames(selectedGameIds)
        : await LibraryAdminApi.refuseGames(selectedGameIds);
      const countKey = action === "validate" ? "validated_count" : "refused_count";
      const processedCount = Number.parseInt(data.result?.[countKey], 10) || 0;
      setSelectedGameIds([]);
      setValidationActionMessage(
        `${processedCount} jeu(x) ${action === "validate" ? "valide(s)" : "refuse(s)"}.`
      );
      await reloadList?.();
      await reloadSummary?.();
    } catch (error) {
      setValidationActionError(error.message || "Impossible de traiter la selection de jeux.");
    } finally {
      setIsRunningValidationAction(false);
    }
  }, [reloadList, reloadSummary, selectedGameIds]);

  if (!enabled) {
    return {
      clearSelection,
      workflow: null,
    };
  }

  return {
    clearSelection,
    workflow: {
      selectedGameIds,
      selectedCount: selectedGameIds.length,
      visibleWaitingValidationGameIds,
      areAllVisibleWaitingGamesSelected,
      isRunningAction: isRunningValidationAction,
      message: validationActionMessage,
      error: validationActionError,
      onToggleGameSelection: toggleGameSelection,
      onToggleVisibleSelection: toggleVisibleGameSelection,
      onValidateSelection: () => runValidationSelectionAction("validate"),
      onRefuseSelection: () => runValidationSelectionAction("refuse"),
    },
  };
}

export default useGameValidationWorkflow;
