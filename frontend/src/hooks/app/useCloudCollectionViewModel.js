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
import useCollectionStatisticsPage from "../collection/useCollectionStatisticsPage";
import useUserCollectionReinitialization from "../collection/useUserCollectionReinitialization";
import useUserCollectionOnboarding from "../collection/useUserCollectionOnboarding";
import useAddGamePage from "../games/useAddGamePage";
import useGameCollectionPage from "../games/useGameCollectionPage";
import useGameDetailPage from "../games/useGameDetailPage";
import useWishlistPage from "../games/useWishlistPage";
import useHomePage from "../home/useHomePage";
import useLibraryEntities from "../library/useLibraryEntities";
import useLibraryGames from "../library/useLibraryGames";
import useGameDuplicateAdminPage from "../library/useGameDuplicateAdminPage";
import useLibraryHomeSearch from "../library/useLibraryHomeSearch";
import useLibraryPlatformDetailPage from "../library/useLibraryPlatformDetailPage";
import useLibraryPlatforms from "../library/useLibraryPlatforms";
import useAdminLibraryCsvImportAction from "../library/useAdminLibraryCsvImportAction";
import useLibraryResetAction from "../library/useLibraryResetAction";
import useLibraryStudios from "../library/useLibraryStudios";
import usePlatformImageModeration from "../library/usePlatformImageModeration";
import usePlatformCatalogSyncAction from "../library/usePlatformCatalogSyncAction";
import useAppNavigation from "../navigation/useAppNavigation";
import usePlatformsCatalog from "../platforms/usePlatformsCatalog";
import useOdsDownload from "../useOdsDownload";
import useSessionState from "./useSessionState";
import useCollectionShareSession from "./useCollectionShareSession";
import useCollectionShareManagement from "../collection/useCollectionShareManagement";

/**
 * Assemble les hooks metier en proprietes directement consommables par les vues.
 *
 * @returns {Object} Proprietes de vue et proprietes de modale d'authentification.
 */
function useCloudCollectionViewModel() {
  const [error, setError] = useState("");
  const session = useSessionState();
  const isCollectionProfile = session.hasAccessToken && session.authenticatedProfile !== "ADMIN";
  const canViewCollection = isCollectionProfile && session.viewAccess.canViewCollection;
  const canViewWishlist = isCollectionProfile && session.viewAccess.canViewWishlist;
  const canViewStatistics = canViewCollection;
  const canUseCollectionViews = canViewCollection || canViewWishlist;
  const refresh = useCollectionRefresh();
  const clearDeleteGameFeedbackRef = useRef(() => {});
  const prepareAddGameFormRef = useRef(() => {});

  const navigation = useAppNavigation({
    hasAccessToken: session.hasAccessToken,
    authenticatedProfile: session.authenticatedProfile,
    canUseCollectionViews,
    canViewCollection,
    canViewWishlist,
    canViewStatistics,
    canAccessConfiguration: session.viewAccess.canAccessConfiguration,
    isGuest: session.viewAccess.isGuest,
    clearDeleteGameFeedback: () => clearDeleteGameFeedbackRef.current(),
    prepareAddGameForm: (selectedPlatform) => prepareAddGameFormRef.current(selectedPlatform),
    setGlobalError: setError,
  });
  useCollectionShareSession({
    setCurrentView: navigation.setCurrentView,
    setError,
  });
  const addGamePage = useAddGamePage({
    currentView: navigation.currentView,
    hasAccessToken: canViewCollection && session.viewAccess.canMutate,
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
    isAuthenticated: canViewCollection,
    hasAccessToken: canViewCollection,
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
    isAuthenticated: canViewCollection,
    hasAccessToken: canViewCollection,
    setError,
    canViewPrices: session.viewAccess.canViewPrices,
  });
  const gameCollection = useGameCollectionPage({
    selectedPlatform: navigation.selectedPlatform,
    gamesReloadKey: refresh.gamesReloadKey,
    isAuthenticated: canViewCollection,
    hasAccessToken: canViewCollection,
    canViewPrices: session.viewAccess.canViewPrices,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    setError,
  });
  const wishlistPage = useWishlistPage({
    currentView: navigation.currentView,
    hasAccessToken: canViewWishlist,
    gamesReloadKey: refresh.gamesReloadKey,
    wishlistBuyStatusDefaultFilter: session.viewAccess.wishlistBuyStatusDefaultFilter,
  });
  const collectionStatisticsPage = useCollectionStatisticsPage({
    enabled: navigation.currentView === "statistics",
    hasAccessToken: canViewStatistics,
    reloadKey: refresh.odsReloadKey,
  });
  const gameDuplicateAdminPage = useGameDuplicateAdminPage({
    enabled: navigation.currentView === "gameDuplicateAdmin",
    gameId: navigation.selectedGameId,
    canCorrect: session.actionPermissions.canCorrectGameDuplicate,
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
    authenticatedProfile: session.authenticatedProfile,
  });
  const adminLibraryCsvImportAction = useAdminLibraryCsvImportAction();
  const libraryResetAction = useLibraryResetAction();
  const platformCatalogSyncAction = usePlatformCatalogSyncAction();
  const platformImageModeration = usePlatformImageModeration({
    enabled: (
      navigation.currentView === "platformImageModeration" &&
      session.authenticatedProfile === "ADMIN" &&
      session.actionPermissions.canModeratePlatformImages
    ),
    canUpdateStatus: session.actionPermissions.canUpdatePlatformImageStatus,
    canUpdateType: session.actionPermissions.canUpdatePlatformImageType,
  });
  const odsDownload = useOdsDownload();
  const userCollectionOnboarding = useUserCollectionOnboarding({
    hasAccessToken: canUseCollectionViews && session.authenticatedProfile !== "GUEST",
    authenticatedUsername: session.authenticatedUsername,
    currentView: navigation.currentView,
    selectedGameSource: navigation.selectedGameSource,
    canUseCollectionViews,
    openCollectionOnboarding: navigation.openCollectionOnboarding,
    openConfiguration: navigation.openConfiguration,
    openVerifiedCollection: navigation.openVerifiedCollection,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
  });
  const gameDetailPage = useGameDetailPage({
    currentView: navigation.currentView,
    gameId: navigation.selectedGameId,
    source: navigation.selectedGameSource,
    hasAccessToken: canUseCollectionViews,
    canCorrectDuplicate: session.actionPermissions.canCorrectGameDuplicate,
    canReportDuplicate: session.actionPermissions.canReportGameDuplicate,
    isGuest: session.viewAccess.isGuest,
    hasCollection: userCollectionOnboarding.hasCollection,
    checkCurrentUserCollection: userCollectionOnboarding.checkCurrentUserCollection,
  });
  const userCollectionReinitialization = useUserCollectionReinitialization({
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    onCollectionReinitialized: userCollectionOnboarding.markCollectionMissingAfterReinitialization,
    openCollectionOnboarding: navigation.openCollectionOnboarding,
  });
  const canManageCollectionShares = (
    session.authenticatedProfile === "USER" &&
    userCollectionOnboarding.hasCollection === true &&
    session.actionPermissions.canManageCollectionShares
  );
  const collectionShareManagement = useCollectionShareManagement({
    enabled: navigation.currentView === "collectionShares" && canManageCollectionShares,
  });

  clearDeleteGameFeedbackRef.current = gameCollection.clearDeleteGameFeedback;

  return {
    viewProps: {
      currentView: navigation.currentView,
      selectedGameId: navigation.selectedGameId,
      selectedLibraryPlatformId: navigation.selectedLibraryPlatformId,
      selectedGameSource: navigation.selectedGameSource,
      gameDetailPage,
      gameDuplicateAdminPage,
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
      canViewCollection,
      canViewWishlist,
      canViewStatistics,
      canViewPrices: session.viewAccess.canViewPrices,
      canAccessConfiguration: session.viewAccess.canAccessConfiguration,
      isGuest: session.viewAccess.isGuest,
      guestOwnerPseudonym: session.viewAccess.ownerPseudonym,
      guestCollectionLabel: session.viewAccess.collectionLabel,
      guestWishlistLabel: session.viewAccess.wishlistLabel,
      canManageCollectionShares,
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
      adminLibraryImportError: adminLibraryCsvImportAction.adminLibraryImportError,
      adminLibraryImportResult: adminLibraryCsvImportAction.adminLibraryImportResult,
      isImportingAdminLibrary: adminLibraryCsvImportAction.isImportingAdminLibrary,
      selectedAdminLibraryImportFileName: (
        adminLibraryCsvImportAction.selectedAdminLibraryImportFileName
      ),
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
      openCollectionShares: navigation.openCollectionShares,
      openLibrary: navigation.openLibrary,
      openLibraryPlatforms: navigation.openLibraryPlatforms,
      openLibraryStudios: navigation.openLibraryStudios,
      openLibraryGames: navigation.openLibraryGames,
      openGameDetail: navigation.openGameDetail,
      openGameDuplicateAdmin: navigation.openGameDuplicateAdmin,
      openLibraryPlatformDetail: navigation.openLibraryPlatformDetail,
      openWishlist: navigation.openWishlist,
      openStatistics: navigation.openStatistics,
      openCollectionOnboarding: navigation.openCollectionOnboarding,
      openUsersPage: navigation.openUsersPage,
      openAdminLibraryImport: navigation.openAdminLibraryImport,
      openPlatformImageModeration: navigation.openPlatformImageModeration,
      openAbout: navigation.openAbout,
      openAuth: navigation.openAuth,
      openPlatform: navigation.openPlatform,
      setHomeSearchQuery: homePage.setHomeSearchQuery,
      logout: session.logout,
      searchGamesByName: homePage.searchGamesByName,
      closeHomeSearch: homePage.closeHomeSearch,
      downloadOdsFile: odsDownload.downloadOdsFile,
      resetLibrary: libraryResetAction.resetLibrary,
      importAdminLibraryCsv: adminLibraryCsvImportAction.importAdminLibraryCsv,
      selectAdminLibraryImportFile: adminLibraryCsvImportAction.selectAdminLibraryImportFile,
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
      updateCsvMapping: userCollectionOnboarding.updateCsvMapping,
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
      collectionStatisticsPage,
      collectionShareManagement,
    },
    authModalProps: session.authModalProps,
  };
}

export default useCloudCollectionViewModel;
