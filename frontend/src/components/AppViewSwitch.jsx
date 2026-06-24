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
import AboutView from "./AboutView";
import AuthView from "./AuthView";
import EmailVerificationResultView from "./EmailVerificationResultView";
import GameDetailView from "./GameDetailView";
import HomeView from "./HomeView";
import LibraryEntityListView from "./LibraryEntityListView";
import LibraryHomeView from "./LibraryHomeView";
import LibraryPlatformDetailView from "./LibraryPlatformDetailView";
import PlatformDetailView from "./PlatformDetailView";
import renderPlatformImageModerationView from "./appViewSwitchPlatformImageModerationRenderer";
import renderConfigurationView from "./appViewSwitchConfigurationRenderer";
import renderCollectionShareManagementView from "./appViewSwitchCollectionShareRenderer";
import UserCollectionOnboardingView from "./UserCollectionOnboardingView";
import UsersView from "./UsersView";
import WishlistView from "./WishlistView";

/**
 * Selectionne la vue React a afficher selon l'etat applicatif courant.
 */
class AppViewSwitch {
  /**
   * Determine l'entree de menu correspondant a la vue active.
   *
   * @param {Object} props - Etat et source de navigation courants.
   * @returns {string} Cle de l'entree de menu active.
   */
  static getActiveNavigationKey(props) {
    if (["auth", "emailVerificationResult"].includes(props.currentView)) {
      return "login";
    }
    if (props.currentView === "about") {
      return "about";
    }
    if (["configuration", "collectionShares", "platformImageModeration", "users"].includes(props.currentView)) {
      return "configuration";
    }
    if (props.currentView === "wishlist") {
      return "wishlist";
    }
    if (props.currentView === "gameDetail" && props.selectedGameSource !== "collection") {
      return "library";
    }
    const libraryViews = [
      "library",
      "libraryPlatforms",
      "libraryPlatformDetail",
      "libraryStudios",
      "libraryGames",
    ];
    if (libraryViews.includes(props.currentView)) {
      return "library";
    }
    return "collection";
  }

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
      activeNavigationKey: this.getActiveNavigationKey(props),
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

    if (props.currentView === "emailVerificationResult") {
      return this.renderEmailVerificationResult(props);
    }

    if (props.currentView === "configuration") {
      return renderConfigurationView(props, this.buildPageLayoutProps(props));
    }

    if (props.currentView === "collectionShares") {
      if (props.authenticatedProfile === "USER") {
        return renderCollectionShareManagementView(props, this.buildPageLayoutProps(props));
      }
      return props.authenticatedProfile === "ADMIN"
        ? renderConfigurationView(props, this.buildPageLayoutProps(props))
        : this.renderAbout(props);
    }

    if (props.currentView === "users") {
      return this.renderUsers(props);
    }

    if (props.currentView === "platformImageModeration") {
      return renderPlatformImageModerationView(props, this.buildPageLayoutProps(props));
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

    if (props.currentView === "libraryPlatformDetail") {
      return this.renderLibraryPlatformDetail(props);
    }

    if (props.currentView === "libraryStudios") {
      return this.renderLibraryList(props, "Studios", "Studios du referentiel commun.", props.libraryStudios);
    }

    if (props.currentView === "libraryGames") {
      return this.renderLibraryList(props, "Jeux", "Jeux du referentiel commun.", props.libraryGames);
    }

    if (props.currentView === "gameDetail") {
      return this.renderGameDetail(props);
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
        error={props.error}
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
        onOpenGameDetail={(game) => props.openGameDetail(game, "collection")}
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
   * Rend la page de resultat de validation email.
   *
   * @param {Object} props - Etat et callbacks de navigation.
   * @returns {import("react").JSX.Element} Vue de resultat de validation email.
   */
  static renderEmailVerificationResult(props) {
    return (
      <EmailVerificationResultView
        {...this.buildPageLayoutProps(props)}
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
        onOpenGameDetail={(game) => props.openGameDetail(game, "collection")}
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
        onOpenGameDetail={(game) => props.openGameDetail(game, "library")}
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
        onRowClick={
          listState === props.libraryGames
            ? (game) => props.openGameDetail(game, "library")
            : listState === props.libraryPlatforms
              ? (platform) => props.openLibraryPlatformDetail(platform)
            : null
        }
      />
    );
  }

  /**
   * Rend la page de detail d'un jeu.
   *
   * @param {Object} props - Etat et callbacks de navigation.
   * @returns {import("react").JSX.Element} Vue detail jeu.
   */
  static renderGameDetail(props) {
    return (
      <GameDetailView
        {...this.buildPageLayoutProps(props)}
        gameDetailPage={props.gameDetailPage}
        selectedGameSource={props.selectedGameSource}
        onBack={() => window.history.back()}
      />
    );
  }

  /**
   * Rend la page de detail d'une plateforme Bibliotheque.
   *
   * @param {Object} props - Etat et callbacks de navigation.
   * @returns {import("react").JSX.Element} Vue detail plateforme Bibliotheque.
   */
  static renderLibraryPlatformDetail(props) {
    return (
      <LibraryPlatformDetailView
        {...this.buildPageLayoutProps(props)}
        platformDetailPage={props.libraryPlatformDetailPage}
        onBack={() => window.history.back()}
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
        sortConfig={props.sortConfig}
        sortedGames={props.sortedGames}
        filteredGames={props.filteredGames}
        gameNameFilter={props.gameNameFilter}
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
        onGameNameFilterChange={props.setGameNameFilter}
        onToggleSort={props.toggleSort}
        onEditGame={props.openEditGame}
        onSaveGame={props.saveEditedGame}
        onCancelEditGame={props.cancelEditGame}
        onDeleteGame={props.deletePlatformGame}
        onOpenGameDetail={(game) => props.openGameDetail(game, "collection")}
      />
    );
  }
}

export default AppViewSwitch;
