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
import AuthApi from "../../services/AuthApi";
import UserCollectionApi from "../../services/UserCollectionApi";
import {
  buildImportConfigurationDescription,
  createDefaultImportConfiguration,
} from "./importConfigurationBuilder";

/**
 * Convertit une erreur d'import en message utilisateur comprehensible.
 *
 * @param {Error} error - Erreur retournee par le client API.
 * @returns {string} Message affichable par la vue d'onboarding.
 * @throws {void} Ne leve pas d'exception.
 */
function getUserCollectionErrorMessage(error) {
  const messagesByCode = {
    invalid_file: formatInvalidFileMessage(error),
    file_too_large: "Le fichier selectionne depasse la taille maximale autorisee.",
    invalid_configuration: formatInvalidConfigurationMessage(error),
    collection_already_imported: "Une collection est deja associee a ce compte.",
    unauthorized: "Votre session ne permet pas d'importer cette collection.",
    unexpected_error: "L'import de la collection a echoue.",
  };
  return messagesByCode[error?.code] || error?.message || messagesByCode.unexpected_error;
}

/**
 * Formate les erreurs 400 de fichier invalide retournees par le backend.
 *
 * @param {Error} error - Erreur API normalisee.
 * @returns {string} Message affichable dans l'onboarding.
 */
function formatInvalidFileMessage(error) {
  const details = Array.isArray(error?.details?.details) ? error.details.details : [];
  if (!details.length) {
    return "Le fichier selectionne doit etre un fichier de collection valide.";
  }
  return `Le fichier selectionne est invalide : ${details.join(" ")}`;
}

/**
 * Formate les erreurs 422 de configuration retournees par le backend.
 *
 * @param {Error} error - Erreur API normalisee.
 * @returns {string} Message affichable dans l'onboarding.
 */
function formatInvalidConfigurationMessage(error) {
  const details = Array.isArray(error?.details?.details) ? error.details.details : [];
  if (!details.length) {
    return "La configuration d'import est invalide.";
  }
  return `La configuration d'import est invalide : ${details.join(" ")}`;
}

/**
 * Indique si le token courant peut ouvrir les vues de collection.
 *
 * @returns {boolean} `true` pour les profils collection utilisateur.
 * @throws {void} Ne leve pas d'exception.
 */
function canCurrentTokenUseCollectionViews() {
  const profile = String(AuthApi.getAccessTokenPayload().profile || "USER").trim().toUpperCase();
  return profile !== "ADMIN";
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
    canUseCollectionViews,
    currentView,
    goHome,
    hasAccessToken,
    openAdminDashboard,
    openCollectionOnboarding,
    reloadGames,
    reloadOds,
  } = options;
  const [hasCollection, setHasCollection] = useState(null);
  const [checkedUsername, setCheckedUsername] = useState("");
  const [selectedCollectionFile, setSelectedCollectionFile] = useState(null);
  const [importConfiguration, setImportConfiguration] = useState(
    createDefaultImportConfiguration
  );
  const [onboardingError, setOnboardingError] = useState("");
  const [isCheckingCollection, setIsCheckingCollection] = useState(false);
  const [isImportingCollection, setIsImportingCollection] = useState(false);
  const importInProgressRef = useRef(false);

  const resetOnboardingState = useCallback(() => {
    setHasCollection(null);
    setCheckedUsername("");
    setSelectedCollectionFile(null);
    setImportConfiguration(createDefaultImportConfiguration());
    setOnboardingError("");
    setIsCheckingCollection(false);
    setIsImportingCollection(false);
    importInProgressRef.current = false;
  }, []);

  const checkCurrentUserCollection = useCallback(async () => {
    if (!hasAccessToken && !AuthApi.getAccessToken()) {
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
    if (!canUseCollectionViews && !canCurrentTokenUseCollectionViews()) {
      openAdminDashboard();
      return;
    }
    const nextHasCollection = await checkCurrentUserCollection();
    if (nextHasCollection) {
      goHome();
      return;
    }
    openCollectionOnboarding();
  }, [
    canUseCollectionViews,
    checkCurrentUserCollection,
    goHome,
    openAdminDashboard,
    openCollectionOnboarding,
  ]);

  const selectCollectionFile = useCallback((collectionFile) => {
    setSelectedCollectionFile(collectionFile || null);
    setOnboardingError("");
  }, []);

  const updateImportConfiguration = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      [fieldName]: value,
    }));
    setOnboardingError("");
  }, []);

  const updateImportLayout = useCallback((layoutName, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      [layoutName]: {
        ...currentConfiguration[layoutName],
        [fieldName]: value,
      },
    }));
    setOnboardingError("");
  }, []);

  const updateImportLayoutColumn = useCallback((layoutName, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      [layoutName]: {
        ...currentConfiguration[layoutName],
        columns: {
          ...currentConfiguration[layoutName].columns,
          [fieldName]: value,
        },
      },
    }));
    setOnboardingError("");
  }, []);

  const updateImportSheet = useCallback((sheetIndex, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      sheets: currentConfiguration.sheets.map((sheet, index) => (
        index === sheetIndex ? { ...sheet, [fieldName]: value } : sheet
      )),
    }));
    setOnboardingError("");
  }, []);

  const updateImportSheetLayout = useCallback((sheetIndex, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      sheets: currentConfiguration.sheets.map((sheet, index) => (
        index === sheetIndex
          ? { ...sheet, layout: { ...sheet.layout, [fieldName]: value } }
          : sheet
      )),
    }));
    setOnboardingError("");
  }, []);

  const updateImportSheetColumn = useCallback((sheetIndex, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      sheets: currentConfiguration.sheets.map((sheet, index) => (
        index === sheetIndex
          ? {
            ...sheet,
            layout: {
              ...sheet.layout,
              columns: { ...sheet.layout.columns, [fieldName]: value },
            },
          }
          : sheet
      )),
    }));
    setOnboardingError("");
  }, []);

  const addImportSheetConfiguration = useCallback(() => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      sheets: [
        ...currentConfiguration.sheets,
        {
          sheetName: "",
          sheetInformation: "platform",
          layout: createDefaultImportConfiguration().sheets[0].layout,
        },
      ],
    }));
  }, []);

  const removeImportSheetConfiguration = useCallback((sheetIndex) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      sheets: currentConfiguration.sheets.filter((_, index) => index !== sheetIndex),
    }));
  }, []);

  const importSelectedCollection = useCallback(async () => {
    if (!selectedCollectionFile || importInProgressRef.current) {
      if (!selectedCollectionFile) {
        setOnboardingError("Selectionnez un fichier de collection avant de lancer l'import.");
      }
      return;
    }
    const { description, errors } = buildImportConfigurationDescription(importConfiguration);
    if (errors.length || !description) {
      setOnboardingError(errors.join(" "));
      return;
    }

    importInProgressRef.current = true;
    setIsImportingCollection(true);
    setOnboardingError("");
    try {
      await UserCollectionApi.importCollection(selectedCollectionFile, description);
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
  }, [goHome, importConfiguration, reloadGames, reloadOds, selectedCollectionFile]);

  useEffect(() => {
    if (hasAccessToken) {
      return;
    }
    resetOnboardingState();
  }, [hasAccessToken, resetOnboardingState]);

  useEffect(() => {
    if (!hasAccessToken || !authenticatedUsername || !canUseCollectionViews) {
      return;
    }
    if ([
      "about",
      "auth",
      "library",
      "libraryPlatforms",
      "libraryStudios",
      "libraryGames",
    ].includes(currentView)) {
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
    canUseCollectionViews,
    openCollectionOnboarding,
    openOnboardingWhenCollectionIsMissing,
  ]);

  return {
    hasCollection,
    selectedCollectionFile,
    selectedCollectionFileName: selectedCollectionFile?.name || "",
    importConfiguration,
    onboardingError,
    isCheckingCollection,
    isImportingCollection,
    handleAuthenticatedUser,
    selectCollectionFile,
    updateImportConfiguration,
    updateImportLayout,
    updateImportLayoutColumn,
    updateImportSheet,
    updateImportSheetLayout,
    updateImportSheetColumn,
    addImportSheetConfiguration,
    removeImportSheetConfiguration,
    importSelectedCollection,
  };
}

export default useUserCollectionOnboarding;
