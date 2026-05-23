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
import useAddGamePage from "../games/useAddGamePage";
import useGameCollectionPage from "../games/useGameCollectionPage";
import useHomePage from "../home/useHomePage";
import useAppNavigation from "../navigation/useAppNavigation";
import usePlatformsCatalog from "../platforms/usePlatformsCatalog";
import useWishlistPage from "../wishlist/useWishlistPage";
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
  const refresh = useCollectionRefresh();
  const clearDeleteGameFeedbackRef = useRef(() => {});
  const prepareAddGameFormRef = useRef(() => {});

  const navigation = useAppNavigation({
    hasAccessToken: session.hasAccessToken,
    authenticatedProfile: session.authenticatedProfile,
    clearDeleteGameFeedback: () => clearDeleteGameFeedbackRef.current(),
    prepareAddGameForm: (selectedPlatform) => prepareAddGameFormRef.current(selectedPlatform),
  });
  const addGamePage = useAddGamePage({
    currentView: navigation.currentView,
    hasAccessToken: session.hasAccessToken,
    odsReloadKey: refresh.odsReloadKey,
    actionPermissions: session.actionPermissions,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    openWishlist: navigation.openWishlist,
    openPlatform: navigation.openPlatform,
    platforms: [],
  });
  const platformsCatalog = usePlatformsCatalog({
    currentView: navigation.currentView,
    odsReloadKey: refresh.odsReloadKey,
    isAuthenticated: session.actionPermissions.isAuthenticated,
    hasAccessToken: session.hasAccessToken,
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
    isAuthenticated: session.actionPermissions.isAuthenticated,
    hasAccessToken: session.hasAccessToken,
    setError,
  });
  const gameCollection = useGameCollectionPage({
    selectedPlatform: navigation.selectedPlatform,
    gamesReloadKey: refresh.gamesReloadKey,
    isAuthenticated: session.actionPermissions.isAuthenticated,
    hasAccessToken: session.hasAccessToken,
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
    setError,
  });
  const wishlistPage = useWishlistPage({
    reloadOds: refresh.reloadOds,
    reloadGames: refresh.reloadGames,
  });
  const odsDownload = useOdsDownload();

  clearDeleteGameFeedbackRef.current = gameCollection.clearDeleteGameFeedback;

  return {
    viewProps: {
      currentView: navigation.currentView,
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
      cacheResetMessage: refresh.cacheResetMessage,
      cacheResetError: refresh.cacheResetError,
      isResettingCache: refresh.isResettingCache,
      gameForm: addGamePage.gameForm,
      addGameColumnValues: addGamePage.addGameColumnValues,
      addGameError: addGamePage.addGameError,
      addGameMessage: addGamePage.addGameMessage,
      isAddingGame: addGamePage.isAddingGame,
      ...gameCollection,
      isLoadingPlatforms: platformsCatalog.isLoadingPlatforms,
      actionPermissions: session.actionPermissions,
      authenticatedUsername: session.authenticatedUsername,
      authenticatedProfile: session.authenticatedProfile,
      selectedPlatformStats: homePage.selectedPlatformStats,
      editingWishlistGame: wishlistPage.editingWishlistGame,
      isSavingWishlistGame: wishlistPage.isSavingWishlistGame,
      downloadError: odsDownload.downloadError,
      isDownloadingOds: odsDownload.isDownloadingOds,
      openAddGamePage: navigation.openAddGamePage,
      openAdminDashboard: navigation.openAdminDashboard,
      openUsersPage: navigation.openUsersPage,
      openAbout: navigation.openAbout,
      openWishlist: navigation.openWishlist,
      openPlatform: navigation.openPlatform,
      setHomeSearchQuery: homePage.setHomeSearchQuery,
      logout: session.logout,
      searchGamesByName: homePage.searchGamesByName,
      closeHomeSearch: homePage.closeHomeSearch,
      resetOdsCache: refresh.resetOdsCache,
      downloadOdsFile: odsDownload.downloadOdsFile,
      goHome: navigation.goHome,
      submitNewGame: addGamePage.submitNewGame,
      updateGameFormValue: addGamePage.updateGameFormValue,
      addWishlistGameToPlatform: wishlistPage.addWishlistGameToPlatform,
      deleteWishlistGame: wishlistPage.deleteWishlistGame,
      openEditWishlistGame: wishlistPage.openEditWishlistGame,
      saveEditedWishlistGame: wishlistPage.saveEditedWishlistGame,
      cancelEditWishlistGame: wishlistPage.cancelEditWishlistGame,
    },
    authModalProps: session.authModalProps,
  };
}

export default useCloudCollectionViewModel;
