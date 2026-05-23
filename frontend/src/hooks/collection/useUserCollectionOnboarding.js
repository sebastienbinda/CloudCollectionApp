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
 * Description : hook React pilotant l'onboarding d'import de collection utilisateur.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import UserCollectionApi from "../../services/UserCollectionApi";

/**
 * Convertit une erreur d'import en message utilisateur comprehensible.
 *
 * @param {Error} error - Erreur retournee par le client API.
 * @returns {string} Message affichable par la vue d'onboarding.
 * @throws {void} Ne leve pas d'exception.
 */
function getUserCollectionErrorMessage(error) {
  const messagesByCode = {
    invalid_file: "Le fichier selectionne doit etre un fichier ODS valide.",
    file_too_large: "Le fichier selectionne depasse la taille maximale autorisee.",
    collection_already_imported: "Une collection est deja associee a ce compte.",
    unauthorized: "Votre session ne permet pas d'importer cette collection.",
    unexpected_error: "L'import de la collection a echoue.",
  };
  return messagesByCode[error?.code] || error?.message || messagesByCode.unexpected_error;
}

/**
 * Orchestre la verification de collection et l'import initial du fichier ODS.
 *
 * @param {Object} options - Navigation, session et callbacks de rafraichissement.
 * @returns {Object} Etat et actions exposes a la vue d'onboarding.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function useUserCollectionOnboarding(options) {
  const {
    authenticatedUsername,
    currentView,
    goHome,
    hasAccessToken,
    openCollectionOnboarding,
    reloadGames,
    reloadOds,
  } = options;
  const [hasCollection, setHasCollection] = useState(null);
  const [checkedUsername, setCheckedUsername] = useState("");
  const [selectedCollectionFile, setSelectedCollectionFile] = useState(null);
  const [onboardingError, setOnboardingError] = useState("");
  const [isCheckingCollection, setIsCheckingCollection] = useState(false);
  const [isImportingCollection, setIsImportingCollection] = useState(false);
  const importInProgressRef = useRef(false);

  const resetOnboardingState = useCallback(() => {
    setHasCollection(null);
    setCheckedUsername("");
    setSelectedCollectionFile(null);
    setOnboardingError("");
    setIsCheckingCollection(false);
    setIsImportingCollection(false);
    importInProgressRef.current = false;
  }, []);

  const checkCurrentUserCollection = useCallback(async () => {
    if (!hasAccessToken) {
      resetOnboardingState();
      return null;
    }

    setIsCheckingCollection(true);
    setOnboardingError("");
    try {
      const data = await UserCollectionApi.fetchCurrentCollectionStatus();
      const nextHasCollection = Boolean(data.has_collection);
      setHasCollection(nextHasCollection);
      setCheckedUsername(authenticatedUsername);
      return nextHasCollection;
    } catch (error) {
      setOnboardingError(getUserCollectionErrorMessage(error));
      throw error;
    } finally {
      setIsCheckingCollection(false);
    }
  }, [authenticatedUsername, hasAccessToken, resetOnboardingState]);

  const openOnboardingWhenCollectionIsMissing = useCallback(async () => {
    const nextHasCollection = await checkCurrentUserCollection();
    if (nextHasCollection === false) {
      openCollectionOnboarding();
    }
    return nextHasCollection;
  }, [checkCurrentUserCollection, openCollectionOnboarding]);

  const handleAuthenticatedUser = useCallback(async () => {
    const nextHasCollection = await checkCurrentUserCollection();
    if (nextHasCollection) {
      goHome();
      return;
    }
    openCollectionOnboarding();
  }, [checkCurrentUserCollection, goHome, openCollectionOnboarding]);

  const selectCollectionFile = useCallback((collectionFile) => {
    setSelectedCollectionFile(collectionFile || null);
    setOnboardingError("");
  }, []);

  const importSelectedCollection = useCallback(async () => {
    if (!selectedCollectionFile || importInProgressRef.current) {
      if (!selectedCollectionFile) {
        setOnboardingError("Selectionnez un fichier ODS avant de lancer l'import.");
      }
      return;
    }

    importInProgressRef.current = true;
    setIsImportingCollection(true);
    setOnboardingError("");
    try {
      await UserCollectionApi.importCollection(selectedCollectionFile);
      setHasCollection(true);
      setSelectedCollectionFile(null);
      reloadOds();
      reloadGames();
      goHome();
    } catch (error) {
      setOnboardingError(getUserCollectionErrorMessage(error));
    } finally {
      importInProgressRef.current = false;
      setIsImportingCollection(false);
    }
  }, [goHome, reloadGames, reloadOds, selectedCollectionFile]);

  useEffect(() => {
    if (hasAccessToken) {
      return;
    }
    resetOnboardingState();
  }, [hasAccessToken, resetOnboardingState]);

  useEffect(() => {
    if (!hasAccessToken || !authenticatedUsername) {
      return;
    }
    if (["about", "auth"].includes(currentView)) {
      return;
    }
    if (checkedUsername === authenticatedUsername) {
      if (hasCollection === false && currentView !== "collectionOnboarding") {
        openCollectionOnboarding();
      }
      return;
    }

    openOnboardingWhenCollectionIsMissing().catch(() => {});
  }, [
    checkedUsername,
    authenticatedUsername,
    currentView,
    hasCollection,
    hasAccessToken,
    openCollectionOnboarding,
    openOnboardingWhenCollectionIsMissing,
  ]);

  return {
    hasCollection,
    selectedCollectionFile,
    selectedCollectionFileName: selectedCollectionFile?.name || "",
    onboardingError,
    isCheckingCollection,
    isImportingCollection,
    handleAuthenticatedUser,
    selectCollectionFile,
    importSelectedCollection,
  };
}

export default useUserCollectionOnboarding;
