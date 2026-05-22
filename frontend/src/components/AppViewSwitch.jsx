/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-04
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : routeur de vues React pour l'application jeux video.
 */
import AddGameView from "./AddGameView";
import AdminDashboardView from "./AdminDashboardView";
import AboutView from "./AboutView";
import AuthView from "./AuthView";
import HomeView from "./HomeView";
import PlatformDetailView from "./PlatformDetailView";
import WishlistView from "./WishlistView";

/**
 * Selectionne la vue React a afficher selon l'etat applicatif courant.
 */
class AppViewSwitch {
  /**
   * Rend la vue active.
   *
   * @param {Object} props - Etat et callbacks de l'application.
   * @returns {import("react").JSX.Element} Vue active.
   */
  static render(props) {
    if (props.currentView === "home") {
      return this.renderHome(props);
    }

    if (props.currentView === "about") {
      return this.renderAbout(props);
    }

    if (props.currentView === "addGame") {
      return this.renderAddGame(props);
    }

    if (props.currentView === "auth") {
      return this.renderAuth(props);
    }

    if (props.currentView === "adminDashboard") {
      return this.renderAdminDashboard(props);
    }

    if (props.currentView === "wishlist") {
      return this.renderWishlist(props);
    }

    return this.renderPlatform(props);
  }

  /**
   * Rend la page About publique.
   *
   * @param {Object} props - Etat et callbacks de navigation.
   * @returns {import("react").JSX.Element} Vue About.
   */
  static renderAbout(props) {
    return (
      <AboutView
        isAuthenticated={props.actionPermissions.isAuthenticated}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenWishlist={props.openWishlist}
        onOpenPlatform={props.openPlatform}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
      />
    );
  }

  /**
   * Rend la page d'accueil.
   *
   * @param {Object} props - Etat et callbacks d'accueil.
   * @returns {import("react").JSX.Element} Vue d'accueil.
   */
  static renderHome(props) {
    return (
      <HomeView
        homeStats={props.homeStats}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        error={props.error}
        isLoadingHome={props.isLoadingHome}
        isSearchingGames={props.isSearchingGames}
        hasSearchedGames={props.hasSearchedGames}
        homeSearchQuery={props.homeSearchQuery}
        homeSearchResults={props.homeSearchResults}
        homeSearchError={props.homeSearchError}
        isAuthenticated={props.actionPermissions.isAuthenticated}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
        onOpenWishlist={props.openWishlist}
        onOpenPlatform={props.openPlatform}
        onSearchQueryChange={props.setHomeSearchQuery}
        onSearchSubmit={props.searchGamesByName}
        onCloseSearch={props.closeHomeSearch}
      />
    );
  }

  /**
   * Rend le tableau de bord administrateur.
   *
   * @param {Object} props - Etat et callbacks d'administration.
   * @returns {import("react").JSX.Element} Vue d'administration.
   */
  static renderAdminDashboard(props) {
    return (
      <AdminDashboardView
        username={props.authenticatedUsername}
        platforms={props.platforms}
        canAddGame={props.actionPermissions.canAddGame}
        canResetCache={props.actionPermissions.canResetCache}
        canDownloadOds={props.actionPermissions.canDownloadOds}
        cacheResetMessage={props.cacheResetMessage}
        cacheResetError={props.cacheResetError}
        isResettingCache={props.isResettingCache}
        downloadError={props.downloadError}
        isDownloadingOds={props.isDownloadingOds}
        onBack={props.goHome}
        onAddGame={props.openAddGamePage}
        onResetCache={props.resetOdsCache}
        onDownloadOds={props.downloadOdsFile}
      />
    );
  }

  /**
   * Rend la page d'ajout de jeu.
   *
   * @param {Object} props - Etat et callbacks du formulaire.
   * @returns {import("react").JSX.Element} Vue d'ajout.
   */
  static renderAddGame(props) {
    return (
      <AddGameView
        platforms={props.platforms}
        gameForm={props.gameForm}
        addGameColumnValues={props.addGameColumnValues}
        addGameError={props.addGameError}
        addGameMessage={props.addGameMessage}
        isAddingGame={props.isAddingGame}
        canAddGame={props.actionPermissions.canAddGame}
        canAddWishlistGame={props.actionPermissions.canAddWishlistGame}
        onBack={props.goHome}
        onSubmit={props.submitNewGame}
        onFieldChange={props.updateGameFormValue}
      />
    );
  }

  /**
   * Rend la page d'authentification.
   *
   * @param {Object} props - Etat et callbacks de connexion.
   * @returns {import("react").JSX.Element} Vue d'authentification.
   */
  static renderAuth(props) {
    return (
      <AuthView
        isAuthenticated={props.actionPermissions.isAuthenticated}
        onAuthenticated={props.goHome}
        onBack={props.openAbout}
      />
    );
  }

  /**
   * Rend la liste de souhaits.
   *
   * @param {Object} props - Etat et callbacks wishlist.
   * @returns {import("react").JSX.Element} Vue wishlist.
   */
  static renderWishlist(props) {
    return (
      <WishlistView
        games={props.namedGames}
        columns={props.columns}
        valuesByColumn={props.valuesByColumn}
        columnFilters={props.columnFilters}
        sortConfig={props.sortConfig}
        sortedGames={props.sortedGames}
        filteredGames={props.filteredGames}
        error={props.error}
        isLoadingGames={props.isLoadingGames}
        platforms={props.platforms}
        canAddGame={props.actionPermissions.canAddGame}
        canEditWishlistGame={props.actionPermissions.canEditWishlistGame}
        canDeleteWishlistGame={props.actionPermissions.canDeleteWishlistGame}
        editingWishlistGame={props.editingWishlistGame}
        isSavingWishlistGame={props.isSavingWishlistGame}
        onBack={props.goHome}
        onAddWishlistGameToPlatform={props.addWishlistGameToPlatform}
        onDeleteWishlistGame={props.deleteWishlistGame}
        onEditWishlistGame={props.openEditWishlistGame}
        onSaveWishlistGame={props.saveEditedWishlistGame}
        onCancelEditWishlistGame={props.cancelEditWishlistGame}
        onToggleSort={props.toggleSort}
        onColumnFiltersChange={props.setColumnFilters}
      />
    );
  }

  /**
   * Rend le detail d'une plateforme.
   *
   * @param {Object} props - Etat et callbacks de plateforme.
   * @returns {import("react").JSX.Element} Vue plateforme.
   */
  static renderPlatform(props) {
    return (
      <PlatformDetailView
        selectedPlatform={props.selectedPlatform}
        selectedPlatformStats={props.selectedPlatformStats}
        studioCount={props.studioCount}
        platforms={props.platforms}
        games={props.namedGames}
        columns={props.columns}
        valuesByColumn={props.valuesByColumn}
        columnFilters={props.columnFilters}
        sortConfig={props.sortConfig}
        sortedGames={props.sortedGames}
        filteredGames={props.filteredGames}
        deleteGameMessage={props.deleteGameMessage}
        deleteGameError={props.deleteGameError}
        error={props.error}
        isLoadingPlatforms={props.isLoadingPlatforms}
        isLoadingGames={props.isLoadingGames}
        isSavingGame={props.isSavingGame}
        isAuthenticated={props.actionPermissions.isAuthenticated}
        canEditGame={props.actionPermissions.canEditGame}
        canDeleteGame={props.actionPermissions.canDeleteGame}
        editingGame={props.editingGame}
        onBack={props.goHome}
        onOpenPlatform={props.openPlatform}
        onToggleSort={props.toggleSort}
        onColumnFiltersChange={props.setColumnFilters}
        onEditGame={props.openEditGame}
        onSaveGame={props.saveEditedGame}
        onCancelEditGame={props.cancelEditGame}
        onDeleteGame={props.deletePlatformGame}
      />
    );
  }
}

export default AppViewSwitch;
