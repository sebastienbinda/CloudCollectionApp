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
import ConfigurationView from "./ConfigurationView";
import AboutView from "./AboutView";
import AuthView from "./AuthView";
import HomeView from "./HomeView";
import LibraryEntityListView from "./LibraryEntityListView";
import LibraryHomeView from "./LibraryHomeView";
import PlatformDetailView from "./PlatformDetailView";
import UserCollectionOnboardingView from "./UserCollectionOnboardingView";
import UsersView from "./UsersView";
import WishlistView from "./WishlistView";

/**
 * Selectionne la vue React a afficher selon l'etat applicatif courant.
 */
class AppViewSwitch {
  /**
   * Construit les proprietes communes au layout de page.
   *
   * @param {Object} props - Etat et callbacks applicatifs.
   * @returns {Object} Proprietes communes de session et navigation.
   */
  static buildPageLayoutProps(props) {
    return {
      isAuthenticated: props.actionPermissions.isAuthenticated,
      canUseCollectionViews: props.canUseCollectionViews,
      authenticatedUsername: props.authenticatedUsername,
      authenticatedProfile: props.authenticatedProfile,
      onOpenAbout: props.openAbout,
      onOpenAuth: props.openAuth,
      onOpenHome: props.goHome,
      onOpenLibrary: props.openLibrary,
      onOpenWishlist: props.openWishlist,
      onOpenConfiguration: props.openConfiguration,
      onLogout: props.logout,
    };
  }

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

    if (props.currentView === "configuration") {
      return this.renderConfiguration(props);
    }

    if (props.currentView === "users") {
      return this.renderUsers(props);
    }

    if (props.currentView === "collectionOnboarding") {
      return this.renderCollectionOnboarding(props);
    }

    if (props.currentView === "wishlist") {
      return this.renderWishlist(props);
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
        {...this.buildPageLayoutProps(props)}
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
        {...this.buildPageLayoutProps(props)}
        homeStats={props.homeStats}
        error={props.error}
        isLoadingHome={props.isLoadingHome}
        isSearchingGames={props.isSearchingGames}
        hasSearchedGames={props.hasSearchedGames}
        homeSearchQuery={props.homeSearchQuery}
        homeSearchResults={props.homeSearchResults}
        homeSearchError={props.homeSearchError}
        onOpenPlatform={props.openPlatform}
        onSearchQueryChange={props.setHomeSearchQuery}
        onSearchSubmit={props.searchGamesByName}
        onCloseSearch={props.closeHomeSearch}
      />
    );
  }

  /**
   * Rend la page Configuration.
   *
   * @param {Object} props - Etat et callbacks de configuration.
   * @returns {import("react").JSX.Element} Vue Configuration.
   */
  static renderConfiguration(props) {
    return (
      <ConfigurationView
        {...this.buildPageLayoutProps(props)}
        username={props.authenticatedUsername}
        platforms={props.platforms}
        canAddGame={props.actionPermissions.canAddGame}
        canDownloadOds={props.actionPermissions.canDownloadOds}
        canResetLibrary={props.actionPermissions.canResetLibrary}
        canReinitializeCollection={props.actionPermissions.canReinitializeCollection}
        canSearchUsers={props.actionPermissions.canSearchUsers}
        downloadError={props.downloadError}
        isDownloadingOds={props.isDownloadingOds}
        libraryResetError={props.libraryResetError}
        libraryResetMessage={props.libraryResetMessage}
        isResettingLibrary={props.isResettingLibrary}
        reinitializationError={props.reinitializationError}
        isReinitializingCollection={props.isReinitializingCollection}
        onAddGame={props.openAddGamePage}
        onOpenUsers={props.openUsersPage}
        onOpenCollectionOnboarding={props.openCollectionOnboarding}
        onDownloadOds={props.downloadOdsFile}
        onResetLibrary={props.resetLibrary}
        onReinitializeCollection={props.reinitializeCollection}
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
        {...this.buildPageLayoutProps(props)}
        canSearchUsers={props.actionPermissions.canSearchUsers}
        canDeleteUser={props.actionPermissions.canDeleteUser}
        canLockUser={props.actionPermissions.canLockUser}
        canUnlockUser={props.actionPermissions.canUnlockUser}
        canValidateUser={props.actionPermissions.canValidateUser}
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
        {...this.buildPageLayoutProps(props)}
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
        {...this.buildPageLayoutProps(props)}
        onAuthenticated={props.handleAuthenticatedUser}
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
        {...this.buildPageLayoutProps(props)}
        selectedCollectionFileName={props.selectedCollectionFileName}
        availableImportSheets={props.availableImportSheets}
        hasAnalyzedImportFile={props.hasAnalyzedImportFile}
        importResult={props.importResult}
        importConfiguration={props.importConfiguration}
        onboardingError={props.onboardingError}
        isCheckingCollection={props.isCheckingCollection}
        isAnalyzingCollection={props.isAnalyzingCollection}
        isImportingCollection={props.isImportingCollection}
        onFileChange={props.selectCollectionFile}
        onConfigurationChange={props.updateImportConfiguration}
        onLayoutChange={props.updateImportLayout}
        onLayoutColumnChange={props.updateImportLayoutColumn}
        onSheetChange={props.updateImportSheet}
        onSheetLayoutChange={props.updateImportSheetLayout}
        onSheetColumnChange={props.updateImportSheetColumn}
        onWishlistConfigurationChange={props.updateWishlistConfiguration}
        onWishlistLayoutChange={props.updateWishlistLayout}
        onWishlistLayoutColumnChange={props.updateWishlistLayoutColumn}
        onAddSheet={props.addImportSheetConfiguration}
        onRemoveSheet={props.removeImportSheetConfiguration}
        onSubmitImport={props.importSelectedCollection}
      />
    );
  }

  /**
   * Rend la page de liste de souhaits.
   *
   * @param {Object} props - Etat et callbacks de navigation.
   * @returns {import("react").JSX.Element} Vue liste de souhaits.
   */
  static renderWishlist(props) {
    return (
      <WishlistView
        {...this.buildPageLayoutProps(props)}
        wishlistPage={props.wishlistPage}
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
        {...this.buildPageLayoutProps(props)}
        entities={props.libraryEntities.entities}
        entitiesError={props.libraryEntities.entitiesError}
        isLoadingEntities={props.libraryEntities.isLoadingEntities}
        librarySearch={props.libraryHomeSearch}
        onOpenLibraryPlatforms={props.openLibraryPlatforms}
        onOpenLibraryStudios={props.openLibraryStudios}
        onOpenLibraryGames={props.openLibraryGames}
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
        {...this.buildPageLayoutProps(props)}
        title={title}
        subtitle={subtitle}
        listState={listState}
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
        {...this.buildPageLayoutProps(props)}
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
        sortableColumns={props.sortableColumns}
        deleteGameMessage={props.deleteGameMessage}
        deleteGameError={props.deleteGameError}
        error={props.error}
        isLoadingPlatforms={props.isLoadingPlatforms}
        isLoadingGames={props.isLoadingGames}
        isSavingGame={props.isSavingGame}
        canEditGame={props.actionPermissions.canEditGame}
        canDeleteGame={props.actionPermissions.canDeleteGame}
        editingGame={props.editingGame}
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
