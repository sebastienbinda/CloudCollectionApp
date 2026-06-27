/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-27
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de correction admin des doublons de jeux.
 */
import { useEffect, useMemo, useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

const DUPLICATE_FIELDS = [
  { key: "name", label: "Nom" },
  { key: "release_date", label: "Date de sortie" },
  { key: "developer_id", label: "Developpeur", payloadKey: "developer" },
  { key: "editor_id", label: "Editeur", payloadKey: "editor" },
  { key: "description", label: "Description" },
];

/**
 * Orchestre l'ecran admin de correction d'un doublon de jeu.
 *
 * @param {Object} options - Etat de navigation et permissions.
 * @returns {Object} Etat et actions de correction.
 */
function useGameDuplicateAdminPage(options = {}) {
  const [duplicateGame, setDuplicateGame] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [candidateSearch, setCandidateSearch] = useState("");
  const [fieldSources, setFieldSources] = useState({});
  const [keepAlias, setKeepAlias] = useState(true);
  const [resolutionResult, setResolutionResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const selectedCandidate = useMemo(
    () => candidates.find((candidate) => String(candidate.id) === String(selectedCandidateId)) || null,
    [candidates, selectedCandidateId]
  );

  useEffect(() => {
    if (!options.enabled || !options.gameId || !options.canCorrect) {
      setDuplicateGame(null);
      setCandidates([]);
      return;
    }
    loadDuplicateContext("");
  }, [options.enabled, options.gameId, options.canCorrect]);

  const loadDuplicateContext = async (name = candidateSearch) => {
    try {
      setIsLoading(true);
      setError("");
      setResolutionResult(null);
      const [gameData, candidateData] = await Promise.all([
        LibraryAdminApi.fetchDuplicateGame(options.gameId),
        LibraryAdminApi.searchDuplicateCandidates(options.gameId, name),
      ]);
      const nextCandidates = Array.isArray(candidateData.candidates)
        ? candidateData.candidates
        : [];
      setDuplicateGame(gameData.game || null);
      setCandidates(nextCandidates);
      const nextCandidateId = selectedCandidateId || nextCandidates[0]?.id || "";
      setSelectedCandidateId(String(nextCandidateId || ""));
      setFieldSources(createDefaultFieldSources());
    } catch (caughtError) {
      setError(caughtError.message || "Impossible de charger le doublon.");
    } finally {
      setIsLoading(false);
    }
  };

  const searchCandidates = async (event) => {
    event.preventDefault();
    await loadDuplicateContext(candidateSearch);
  };

  const updateFieldSource = (fieldKey, source) => {
    setFieldSources((current) => ({
      ...current,
      [fieldKey]: source === "duplicate" ? "duplicate" : "target",
    }));
  };

  const rejectDuplicate = async () => {
    if (!window.confirm("Refuser ce signalement de doublon ?")) {
      return;
    }
    await executeAction(
      () => LibraryAdminApi.rejectDuplicateGame(options.gameId),
      {
        action: "reject",
        duplicateGame,
        successMessage: "Le signalement de doublon a ete refuse.",
        targetGame: duplicateGame,
      }
    );
  };

  const mergeDuplicate = async () => {
    if (!selectedCandidate) {
      setError("Selectionnez le jeu a conserver.");
      return;
    }
    await executeAction(
      () => LibraryAdminApi.mergeDuplicateGame({
        duplicate_game_id: options.gameId,
        target_game_id: selectedCandidate.id,
        keep_duplicate_name_as_alias: keepAlias,
        selected_values: buildSelectedValues(duplicateGame, selectedCandidate, fieldSources),
      }),
      {
        action: "merge",
        duplicateGame,
        successMessage: "Le doublon a ete fusionne avec succes.",
        targetGame: selectedCandidate,
      }
    );
  };

  const executeAction = async (action, metadata) => {
    try {
      setIsSaving(true);
      setError("");
      const actionResult = await action();
      setResolutionResult(createSuccessResult(actionResult, metadata));
    } catch (caughtError) {
      setResolutionResult(createFailureResult(caughtError, metadata));
    } finally {
      setIsSaving(false);
    }
  };

  return {
    candidates,
    candidateSearch,
    duplicateGame,
    error,
    fieldSources,
    fields: DUPLICATE_FIELDS,
    isLoading,
    isSaving,
    keepAlias,
    resolutionResult,
    selectedCandidate,
    selectedCandidateId,
    clearResolutionResult: () => setResolutionResult(null),
    mergeDuplicate,
    rejectDuplicate,
    searchCandidates,
    setCandidateSearch,
    setKeepAlias,
    setSelectedCandidateId,
    updateFieldSource,
  };
}

function createSuccessResult(apiResult, metadata) {
  const result = apiResult?.result || apiResult || {};
  return {
    action: metadata.action,
    duplicateGame: metadata.duplicateGame || null,
    isSuccess: true,
    message: metadata.successMessage,
    result,
    targetGame: resolveTargetGame(metadata.targetGame, result),
  };
}

function createFailureResult(error, metadata) {
  return {
    action: metadata.action,
    duplicateGame: metadata.duplicateGame || null,
    errorStatus: error?.status || 0,
    isSuccess: false,
    message: error?.message || "La correction du doublon a echoue.",
    result: error?.details || {},
    targetGame: metadata.targetGame || null,
  };
}

function resolveTargetGame(targetGame, result) {
  if (targetGame?.id) {
    return targetGame;
  }
  if (result?.target_game_id) {
    return { id: result.target_game_id, name: "" };
  }
  return targetGame || null;
}

function createDefaultFieldSources() {
  return DUPLICATE_FIELDS.reduce((sources, field) => ({
    ...sources,
    [field.key]: "target",
  }), {});
}

function buildSelectedValues(duplicateGame, selectedCandidate, fieldSources) {
  return DUPLICATE_FIELDS.reduce((values, field) => {
    if (fieldSources[field.key] !== "duplicate") {
      return values;
    }
    const payloadKey = field.payloadKey || field.key;
    return {
      ...values,
      [payloadKey]: duplicateGame?.[field.key] ?? selectedCandidate?.[field.key] ?? null,
    };
  }, {});
}

export default useGameDuplicateAdminPage;
