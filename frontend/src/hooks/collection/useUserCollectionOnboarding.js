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
import getUserCollectionErrorMessage from "./userCollectionImportMessages";
import updatedLayoutValue from "./importLayoutState";
import {
  buildImportConfigurationDescription,
  collectionRequiredFields,
  createImportConfigurationFromDescription,
  createDefaultImportConfiguration,
} from "./importConfigurationBuilder";
import {
  buildIncompatibleSavedConfigurationMessage,
  normalizeImportFileType,
  resolveImportFileType,
} from "./importFileTypeTools";
import buildImportConfigurationAfterAnalysis from "./importAnalysisConfiguration";
import canCurrentTokenUseCollectionViews from "./collectionSessionPolicy";

/**
 * Orchestre la verification de collection et l'import initial du fichier de collection.
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
    hasAccessToken,
    openConfiguration,
    openCollectionOnboarding,
    openVerifiedCollection,
    reloadGames,
    reloadOds,
  } = options;
  const [hasCollection, setHasCollection] = useState(null);
  const [checkedUsername, setCheckedUsername] = useState("");
  const [selectedCollectionFile, setSelectedCollectionFile] = useState(null);
  const [availableImportSheets, setAvailableImportSheets] = useState([]);
  const [hasAnalyzedImportFile, setHasAnalyzedImportFile] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [importConfiguration, setImportConfiguration] = useState(
    createDefaultImportConfiguration
  );
  const [onboardingError, setOnboardingError] = useState("");
  const [isCheckingCollection, setIsCheckingCollection] = useState(false);
  const [isAnalyzingCollection, setIsAnalyzingCollection] = useState(false);
  const [isImportingCollection, setIsImportingCollection] = useState(false);
  const importInProgressRef = useRef(false);

  const resetOnboardingState = useCallback(() => {
    setHasCollection(null);
    setCheckedUsername("");
    setSelectedCollectionFile(null);
    setAvailableImportSheets([]);
    setHasAnalyzedImportFile(false);
    setImportResult(null);
    setImportConfiguration(createDefaultImportConfiguration());
    setOnboardingError("");
    setIsCheckingCollection(false);
    setIsAnalyzingCollection(false);
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

  const markCollectionMissingAfterReinitialization = useCallback(() => {
    setHasCollection(false);
    setCheckedUsername(authenticatedUsername);
    setSelectedCollectionFile(null);
    setAvailableImportSheets([]);
    setHasAnalyzedImportFile(false);
    setImportResult(null);
    setImportConfiguration(createDefaultImportConfiguration());
    setOnboardingError("");
  }, [authenticatedUsername]);

  const handleAuthenticatedUser = useCallback(async () => {
    if (!canUseCollectionViews && !canCurrentTokenUseCollectionViews()) {
      openConfiguration();
      return;
    }
    const nextHasCollection = await checkCurrentUserCollection();
    if (nextHasCollection) {
      openVerifiedCollection();
      return;
    }
    openCollectionOnboarding();
  }, [
    canUseCollectionViews,
    checkCurrentUserCollection,
    openConfiguration,
    openCollectionOnboarding,
    openVerifiedCollection,
  ]);

  const applyAnalyzedSheets = useCallback((sheetNames, analyzedFileType) => {
    setAvailableImportSheets(sheetNames);
    setHasAnalyzedImportFile(true);
    setImportConfiguration((currentConfiguration) => buildImportConfigurationAfterAnalysis(
      currentConfiguration,
      sheetNames,
      analyzedFileType
    ));
  }, []);

  const applySavedImportConfigurationIfConfirmed = useCallback(async (currentFileType) => {
    try {
      const savedImportConfiguration = await UserCollectionApi.fetchSavedImportConfiguration();
      if (!savedImportConfiguration) {
        return;
      }
      const selectedFileType = normalizeImportFileType(currentFileType);
      const savedFileType = normalizeImportFileType(savedImportConfiguration.file_type);
      if (savedFileType !== selectedFileType) {
        setOnboardingError(
          buildIncompatibleSavedConfigurationMessage(savedFileType, selectedFileType)
        );
        return;
      }
      const confirmed = window.confirm(
        "Une configuration d'import sauvegardee existe. Voulez-vous la reutiliser ?"
      );
      if (!confirmed) {
        return;
      }
      setImportConfiguration(
        createImportConfigurationFromDescription(savedImportConfiguration)
      );
    } catch (error) {
      setOnboardingError(getUserCollectionErrorMessage(error));
    }
  }, []);

  const selectCollectionFile = useCallback(async (collectionFile) => {
    setSelectedCollectionFile(collectionFile || null);
    setAvailableImportSheets([]);
    setHasAnalyzedImportFile(false);
    setImportResult(null);
    setOnboardingError("");
    if (!collectionFile) {
      return;
    }
    setIsAnalyzingCollection(true);
    try {
      const fileType = resolveImportFileType(collectionFile, importConfiguration.fileType);
      setImportConfiguration((currentConfiguration) => (
        normalizeImportFileType(currentConfiguration.fileType) === fileType
          ? currentConfiguration
          : {
            ...createDefaultImportConfiguration(),
            fileType,
          }
      ));
      await UserCollectionApi.uploadImportFile(collectionFile, fileType);
      const analysis = await UserCollectionApi.analyzeImportFile(fileType);
      applyAnalyzedSheets(Array.isArray(analysis.sheets) ? analysis.sheets : [], fileType);
      await applySavedImportConfigurationIfConfirmed(fileType);
    } catch (error) {
      setSelectedCollectionFile(null);
      setOnboardingError(getUserCollectionErrorMessage(error));
    } finally {
      setIsAnalyzingCollection(false);
    }
  }, [applyAnalyzedSheets, applySavedImportConfigurationIfConfirmed, importConfiguration.fileType]);

  const updateImportConfiguration = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      [fieldName]: value,
    }));
    setOnboardingError("");
  }, []);

  const updateCsvMapping = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      csvMapping: {
        ...currentConfiguration.csvMapping,
        [fieldName]: value,
      },
    }));
    setOnboardingError("");
  }, []);

  const updateImportLayout = useCallback((layoutName, fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      [layoutName]: {
        ...updatedLayoutValue(
          currentConfiguration[layoutName],
          fieldName,
          value,
          collectionRequiredFields(
            currentConfiguration,
            layoutName === "singleSheetLayout"
          )
        ),
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
          ? {
            ...sheet,
            layout: updatedLayoutValue(
              sheet.layout,
              fieldName,
              value,
              collectionRequiredFields(currentConfiguration, false)
            ),
          }
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

  const updateWishlistConfiguration = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      wishlist: {
        ...currentConfiguration.wishlist,
        [fieldName]: value,
      },
    }));
    setOnboardingError("");
  }, []);

  const updateWishlistLayout = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      wishlist: {
        ...currentConfiguration.wishlist,
        layout: updatedLayoutValue(
          currentConfiguration.wishlist.layout,
          fieldName,
          value,
          collectionRequiredFields(
            { ...currentConfiguration, wishlist: { mode: "none" } },
            true
          )
        ),
      },
    }));
    setOnboardingError("");
  }, []);

  const updateWishlistLayoutColumn = useCallback((fieldName, value) => {
    setImportConfiguration((currentConfiguration) => ({
      ...currentConfiguration,
      wishlist: {
        ...currentConfiguration.wishlist,
        layout: {
          ...currentConfiguration.wishlist.layout,
          columns: {
            ...currentConfiguration.wishlist.layout.columns,
            [fieldName]: value,
          },
        },
      },
    }));
    setOnboardingError("");
  }, []);

  const importSelectedCollection = useCallback(async () => {
    if (!selectedCollectionFile || importInProgressRef.current) {
      if (!selectedCollectionFile) {
        setOnboardingError("Selectionnez un fichier de collection avant de lancer l'import.");
      }
      return;
    }
    if (!hasAnalyzedImportFile) {
      setOnboardingError("Attendez la fin de l'analyse du fichier avant de lancer l'import.");
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
      const result = await UserCollectionApi.importCollection(description);
      setHasCollection(true);
      setSelectedCollectionFile(null);
      setImportResult(result);
      reloadOds();
      reloadGames();
    } catch (error) {
      setOnboardingError(getUserCollectionErrorMessage(error));
    } finally {
      importInProgressRef.current = false;
      setIsImportingCollection(false);
    }
  }, [hasAnalyzedImportFile, importConfiguration, reloadGames, reloadOds, selectedCollectionFile]);

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
    if (
      currentView === "gameDetail" &&
      options.selectedGameSource === "library"
    ) {
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
    checkCurrentUserCollection,
    selectedCollectionFile,
    availableImportSheets,
    hasAnalyzedImportFile,
    selectedCollectionFileName: selectedCollectionFile?.name || "",
    importResult,
    importConfiguration,
    onboardingError,
    isCheckingCollection,
    isAnalyzingCollection,
    isImportingCollection,
    handleAuthenticatedUser,
    markCollectionMissingAfterReinitialization,
    selectCollectionFile,
    updateImportConfiguration,
    updateImportLayout,
    updateImportLayoutColumn,
    updateImportSheet,
    updateImportSheetLayout,
    updateImportSheetColumn,
    updateWishlistConfiguration,
    updateWishlistLayout,
    updateWishlistLayoutColumn,
    updateCsvMapping,
    addImportSheetConfiguration,
    removeImportSheetConfiguration,
    importSelectedCollection,
  };
}

export default useUserCollectionOnboarding;
