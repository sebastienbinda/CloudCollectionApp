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
 * Description : view-model React principal de CloudCollectionApp.
 */
import { useRef, useState } from "react";
import useCollectionRefresh from "../collection/useCollectionRefresh";
import useUserCollectionReinitialization from "../collection/useUserCollectionReinitialization";
import useUserCollectionOnboarding from "../collection/useUserCollectionOnboarding";
import useAddGamePage from "../games/useAddGamePage";
import useGameCollectionPage from "../games/useGameCollectionPage";
import useGameDetailPage from "../games/useGameDetailPage";
import useWishlistPage from "../games/useWishlistPage";
import useHomePage from "../home/useHomePage";
import useLibraryEntities from "../library/useLibraryEntities";
import useLibraryGames from "../library/useLibraryGames";
import useLibraryHomeSearch from "../library/useLibraryHomeSearch";
import useLibraryPlatformDetailPage from "../library/useLibraryPlatformDetailPage";
import useLibraryPlatforms from "../library/useLibraryPlatforms";
import useLibraryResetAction from "../library/useLibraryResetAction";
import useLibraryStudios from "../library/useLibraryStudios";
import usePlatformImageModeration from "../library/usePlatformImageModeration";
import usePlatformCatalogSyncAction from "../library/usePlatformCatalogSyncAction";
import useAppNavigation from "../navigation/useAppNavigation";
import usePlatformsCatalog from "../platforms/usePlatformsCatalog";
import useOdsDownload from "../useOdsDownload";
import useSessionState from "./useSessionState";

/**
 * Assemble les hooks metier en proprietes directement consommables par les vues.
 *
 * @returns {Object} Proprietes de vue et proprietes de modale d'authentification.
 */
function useCloudCollectionViewModel() {
  const [error, setError] = useState("");
  const session = useSessionState();
  const canUseCollectionViews = session.hasAccessToken && session.authenticatedProfile !== "ADMIN";
  const refresh = useCollectionRefresh();
  const clearDeleteGameFeedbackRef = useRef(() => {});
  const prepareAddGameFormRef = useRef(() => {});

  const navigation = useAppNavigation({
    hasAccessToken: session.hasAccessToken,
    authenticatedProfile: session.authenticatedProfile,
    canUseCollectionViews,
    clearDeleteGameFeedback: () => clearDeleteGameFeedbackRef.current(),
    prepareAddGameForm: (selectedPlatform) => prepareAddGameFormRef.current(selectedPlatform),
  });
  const addGamePage = useAddGamePage({
    currentView: navigation.currentView,
    hasAccessToken: canUseCollectionViews,
    odsReloadKey: refresh.odsReloadKey,
    actionPermissions: session.actionPermissions,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    openPlatform: navigation.openPlatform,
    platforms: [],
  });
  const platformsCatalog = usePlatformsCatalog({
    currentView: navigation.currentView,
    odsReloadKey: refresh.odsReloadKey,
    isAuthenticated: canUseCollectionViews,
    hasAccessToken: canUseCollectionViews,
    setSelectedPlatform: navigation.setSelectedPlatform,
    setCurrentView: navigation.setCurrentView,
    setGameForm: addGamePage.setGameForm,
    setError,
  });

  prepareAddGameFormRef.current = (selectedPlatform) => {
    addGamePage.prepareAddGameForm(selectedPlatform, platformsCatalog.platforms);
  };

  const homePage = useHomePage({
    currentView: navigation.currentView,
    selectedPlatform: navigation.selectedPlatform,
    odsReloadKey: refresh.odsReloadKey,
    isAuthenticated: canUseCollectionViews,
    hasAccessToken: canUseCollectionViews,
    setError,
  });
  const gameCollection = useGameCollectionPage({
    selectedPlatform: navigation.selectedPlatform,
    gamesReloadKey: refresh.gamesReloadKey,
    isAuthenticated: canUseCollectionViews,
    hasAccessToken: canUseCollectionViews,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    setError,
  });
  const wishlistPage = useWishlistPage({
    currentView: navigation.currentView,
    hasAccessToken: canUseCollectionViews,
    gamesReloadKey: refresh.gamesReloadKey,
  });
  const gameDetailPage = useGameDetailPage({
    currentView: navigation.currentView,
    gameId: navigation.selectedGameId,
    source: navigation.selectedGameSource,
    hasAccessToken: canUseCollectionViews,
  });
  const libraryPlatformDetailPage = useLibraryPlatformDetailPage({
    currentView: navigation.currentView,
    platformId: navigation.selectedLibraryPlatformId,
  });
  const libraryEntities = useLibraryEntities({
    enabled: navigation.currentView === "library",
  });
  const libraryHomeSearch = useLibraryHomeSearch({
    enabled: navigation.currentView === "library",
  });
  const libraryPlatforms = useLibraryPlatforms({
    enabled: navigation.currentView === "libraryPlatforms",
  });
  const libraryStudios = useLibraryStudios({
    enabled: navigation.currentView === "libraryStudios",
  });
  const libraryGames = useLibraryGames({
    enabled: navigation.currentView === "libraryGames",
  });
  const libraryResetAction = useLibraryResetAction();
  const platformCatalogSyncAction = usePlatformCatalogSyncAction();
  const platformImageModeration = usePlatformImageModeration({
    enabled: (
      navigation.currentView === "configuration" &&
      session.authenticatedProfile === "ADMIN" &&
      session.actionPermissions.canModeratePlatformImages
    ),
    canUpdateStatus: session.actionPermissions.canUpdatePlatformImageStatus,
    canUpdateType: session.actionPermissions.canUpdatePlatformImageType,
  });
  const odsDownload = useOdsDownload();
  const userCollectionOnboarding = useUserCollectionOnboarding({
    hasAccessToken: canUseCollectionViews,
    authenticatedUsername: session.authenticatedUsername,
    currentView: navigation.currentView,
    canUseCollectionViews,
    openCollectionOnboarding: navigation.openCollectionOnboarding,
    openConfiguration: navigation.openConfiguration,
    openVerifiedCollection: navigation.openVerifiedCollection,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
  });
  const userCollectionReinitialization = useUserCollectionReinitialization({
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    onCollectionReinitialized: userCollectionOnboarding.markCollectionMissingAfterReinitialization,
    openCollectionOnboarding: navigation.openCollectionOnboarding,
  });

  clearDeleteGameFeedbackRef.current = gameCollection.clearDeleteGameFeedback;

  return {
    viewProps: {
      currentView: navigation.currentView,
      selectedGameId: navigation.selectedGameId,
      selectedLibraryPlatformId: navigation.selectedLibraryPlatformId,
      selectedGameSource: navigation.selectedGameSource,
      gameDetailPage,
      libraryPlatformDetailPage,
      homeStats: homePage.homeStats,
      platforms: platformsCatalog.platforms,
      selectedPlatform: navigation.selectedPlatform,
      error,
      isLoadingHome: homePage.isLoadingHome,
      isSearchingGames: homePage.isSearchingGames,
      hasSearchedGames: homePage.hasSearchedGames,
      homeSearchQuery: homePage.homeSearchQuery,
      homeSearchResults: homePage.homeSearchResults,
      homeSearchError: homePage.homeSearchError,
      gameForm: addGamePage.gameForm,
      addGameColumnValues: addGamePage.addGameColumnValues,
      addGameError: addGamePage.addGameError,
      addGameMessage: addGamePage.addGameMessage,
      isAddingGame: addGamePage.isAddingGame,
      ...gameCollection,
      wishlistPage,
      isLoadingPlatforms: platformsCatalog.isLoadingPlatforms,
      actionPermissions: session.actionPermissions,
      canUseCollectionViews,
      authenticatedUsername: session.authenticatedUsername,
      authenticatedProfile: session.authenticatedProfile,
      selectedPlatformStats: homePage.selectedPlatformStats || platformsCatalog.platforms.find(
        (platform) => String(platform.id) === String(navigation.selectedPlatform)
      ),
      downloadError: odsDownload.downloadError,
      isDownloadingOds: odsDownload.isDownloadingOds,
      libraryResetError: libraryResetAction.libraryResetError,
      libraryResetMessage: libraryResetAction.libraryResetMessage,
      isResettingLibrary: libraryResetAction.isResettingLibrary,
      platformCatalogSyncError: platformCatalogSyncAction.platformCatalogSyncError,
      platformCatalogSyncMessage: platformCatalogSyncAction.platformCatalogSyncMessage,
      isSyncingPlatformCatalog: platformCatalogSyncAction.isSyncingPlatformCatalog,
      platformImageModeration,
      reinitializationError: userCollectionReinitialization.reinitializationError,
      isReinitializingCollection: userCollectionReinitialization.isReinitializingCollection,
      selectedCollectionFileName: userCollectionOnboarding.selectedCollectionFileName,
      availableImportSheets: userCollectionOnboarding.availableImportSheets,
      hasAnalyzedImportFile: userCollectionOnboarding.hasAnalyzedImportFile,
      importResult: userCollectionOnboarding.importResult,
      importConfiguration: userCollectionOnboarding.importConfiguration,
      onboardingError: userCollectionOnboarding.onboardingError,
      isCheckingCollection: userCollectionOnboarding.isCheckingCollection,
      isAnalyzingCollection: userCollectionOnboarding.isAnalyzingCollection,
      isImportingCollection: userCollectionOnboarding.isImportingCollection,
      openAddGamePage: navigation.openAddGamePage,
      openConfiguration: navigation.openConfiguration,
      openLibrary: navigation.openLibrary,
      openLibraryPlatforms: navigation.openLibraryPlatforms,
      openLibraryStudios: navigation.openLibraryStudios,
      openLibraryGames: navigation.openLibraryGames,
      openGameDetail: navigation.openGameDetail,
      openLibraryPlatformDetail: navigation.openLibraryPlatformDetail,
      openWishlist: navigation.openWishlist,
      openCollectionOnboarding: navigation.openCollectionOnboarding,
      openUsersPage: navigation.openUsersPage,
      openAbout: navigation.openAbout,
      openAuth: navigation.openAuth,
      openPlatform: navigation.openPlatform,
      setHomeSearchQuery: homePage.setHomeSearchQuery,
      logout: session.logout,
      searchGamesByName: homePage.searchGamesByName,
      closeHomeSearch: homePage.closeHomeSearch,
      downloadOdsFile: odsDownload.downloadOdsFile,
      resetLibrary: libraryResetAction.resetLibrary,
      syncPlatformCatalog: platformCatalogSyncAction.syncPlatformCatalog,
      reinitializeCollection: userCollectionReinitialization.reinitializeCollection,
      handleAuthenticatedUser: userCollectionOnboarding.handleAuthenticatedUser,
      selectCollectionFile: userCollectionOnboarding.selectCollectionFile,
      updateImportConfiguration: userCollectionOnboarding.updateImportConfiguration,
      updateImportLayout: userCollectionOnboarding.updateImportLayout,
      updateImportLayoutColumn: userCollectionOnboarding.updateImportLayoutColumn,
      updateImportSheet: userCollectionOnboarding.updateImportSheet,
      updateImportSheetLayout: userCollectionOnboarding.updateImportSheetLayout,
      updateImportSheetColumn: userCollectionOnboarding.updateImportSheetColumn,
      updateWishlistConfiguration: userCollectionOnboarding.updateWishlistConfiguration,
      updateWishlistLayout: userCollectionOnboarding.updateWishlistLayout,
      updateWishlistLayoutColumn: userCollectionOnboarding.updateWishlistLayoutColumn,
      addImportSheetConfiguration: userCollectionOnboarding.addImportSheetConfiguration,
      removeImportSheetConfiguration: userCollectionOnboarding.removeImportSheetConfiguration,
      importSelectedCollection: userCollectionOnboarding.importSelectedCollection,
      goHome: navigation.goHome,
      submitNewGame: addGamePage.submitNewGame,
      updateGameFormValue: addGamePage.updateGameFormValue,
      libraryEntities,
      libraryHomeSearch,
      libraryPlatforms,
      libraryStudios,
      libraryGames,
    },
    authModalProps: session.authModalProps,
  };
}

export default useCloudCollectionViewModel;
