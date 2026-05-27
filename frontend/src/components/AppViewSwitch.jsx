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
import LibraryEntityListView from "./LibraryEntityListView";
import LibraryHomeView from "./LibraryHomeView";
import PlatformDetailView from "./PlatformDetailView";
import UserCollectionOnboardingView from "./UserCollectionOnboardingView";
import UsersView from "./UsersView";

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

    if (props.currentView === "users") {
      return this.renderUsers(props);
    }

    if (props.currentView === "collectionOnboarding") {
      return this.renderCollectionOnboarding(props);
    }

    if (props.currentView === "library") {
      return this.renderLibrary(props);
    }

    if (props.currentView === "libraryPlatforms") {
      return this.renderLibraryList(props, "Plateformes", "Plateformes du referentiel commun.", props.libraryPlatforms);
    }

    if (props.currentView === "libraryStudios") {
      return this.renderLibraryList(props, "Studios", "Studios du referentiel commun.", props.libraryStudios);
    }

    if (props.currentView === "libraryGames") {
      return this.renderLibraryList(props, "Jeux", "Jeux du referentiel commun.", props.libraryGames);
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
        canUseCollectionViews={props.canUseCollectionViews}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenLibrary={props.openLibrary}
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
        canUseCollectionViews={props.canUseCollectionViews}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenLibrary={props.openLibrary}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
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
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        canAddGame={props.actionPermissions.canAddGame}
        canDownloadOds={props.actionPermissions.canDownloadOds}
        canSearchUsers={props.actionPermissions.canSearchUsers}
        canUseCollectionViews={props.canUseCollectionViews}
        downloadError={props.downloadError}
        isDownloadingOds={props.isDownloadingOds}
        onBack={props.goHome}
        onBackToLibrary={props.openLibrary}
        onAddGame={props.openAddGamePage}
        onOpenUsers={props.openUsersPage}
        onDownloadOds={props.downloadOdsFile}
      />
    );
  }

  /**
   * Rend la page de gestion des utilisateurs.
   *
   * @param {Object} props - Etat et callbacks d'administration utilisateur.
   * @returns {import("react").JSX.Element} Vue utilisateurs.
   */
  static renderUsers(props) {
    return (
      <UsersView
        authenticatedProfile={props.authenticatedProfile}
        canSearchUsers={props.actionPermissions.canSearchUsers}
        canDeleteUser={props.actionPermissions.canDeleteUser}
        canLockUser={props.actionPermissions.canLockUser}
        canUnlockUser={props.actionPermissions.canUnlockUser}
        onBack={props.openAdminDashboard}
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
        canUseCollectionViews={props.canUseCollectionViews}
        onAuthenticated={props.handleAuthenticatedUser}
        onBack={props.openAbout}
      />
    );
  }

  /**
   * Rend le parcours d'import initial de collection utilisateur.
   *
   * @param {Object} props - Etat et callbacks d'onboarding collection.
   * @returns {import("react").JSX.Element} Vue d'onboarding collection.
   */
  static renderCollectionOnboarding(props) {
    return (
      <UserCollectionOnboardingView
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        selectedCollectionFileName={props.selectedCollectionFileName}
        importConfiguration={props.importConfiguration}
        onboardingError={props.onboardingError}
        isCheckingCollection={props.isCheckingCollection}
        isImportingCollection={props.isImportingCollection}
        isAuthenticated={props.actionPermissions.isAuthenticated}
        canUseCollectionViews={props.canUseCollectionViews}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenLibrary={props.openLibrary}
        onOpenPlatform={props.openPlatform}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
        onFileChange={props.selectCollectionFile}
        onConfigurationChange={props.updateImportConfiguration}
        onLayoutChange={props.updateImportLayout}
        onLayoutColumnChange={props.updateImportLayoutColumn}
        onSheetChange={props.updateImportSheet}
        onSheetLayoutChange={props.updateImportSheetLayout}
        onSheetColumnChange={props.updateImportSheetColumn}
        onAddSheet={props.addImportSheetConfiguration}
        onRemoveSheet={props.removeImportSheetConfiguration}
        onSubmitImport={props.importSelectedCollection}
      />
    );
  }

  /**
   * Rend la page d'accueil Bibliotheque publique.
   *
   * @param {Object} props - Etat et callbacks Bibliotheque.
   * @returns {import("react").JSX.Element} Vue Bibliotheque.
   */
  static renderLibrary(props) {
    return (
      <LibraryHomeView
        entities={props.libraryEntities.entities}
        entitiesError={props.libraryEntities.entitiesError}
        isLoadingEntities={props.libraryEntities.isLoadingEntities}
        isAuthenticated={props.actionPermissions.isAuthenticated}
        canUseCollectionViews={props.canUseCollectionViews}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenLibrary={props.openLibrary}
        onOpenLibraryPlatforms={props.openLibraryPlatforms}
        onOpenLibraryStudios={props.openLibraryStudios}
        onOpenLibraryGames={props.openLibraryGames}
        onOpenPlatform={props.openPlatform}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
      />
    );
  }

  /**
   * Rend une liste d'entite Bibliotheque publique.
   *
   * @param {Object} props - Etat et callbacks Bibliotheque.
   * @param {string} title - Titre de la liste.
   * @param {string} subtitle - Sous-titre de la liste.
   * @param {Object} listState - Etat de liste fourni par le hook Bibliotheque.
   * @returns {import("react").JSX.Element} Vue de liste Bibliotheque.
   */
  static renderLibraryList(props, title, subtitle, listState) {
    return (
      <LibraryEntityListView
        title={title}
        subtitle={subtitle}
        listState={listState}
        isAuthenticated={props.actionPermissions.isAuthenticated}
        canUseCollectionViews={props.canUseCollectionViews}
        authenticatedUsername={props.authenticatedUsername}
        authenticatedProfile={props.authenticatedProfile}
        platforms={props.platforms}
        selectedPlatform={props.selectedPlatform}
        onOpenAbout={props.openAbout}
        onOpenHome={props.goHome}
        onOpenLibrary={props.openLibrary}
        onOpenPlatform={props.openPlatform}
        onOpenAdminDashboard={props.openAdminDashboard}
        onLogout={props.logout}
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
