/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page publique d'accueil de la Bibliotheque.
 */
import { formatCellValue, formatNumber } from "../collectionUtils";
import CardComponent from "./CardComponent";
import CardCountComponent from "./CardCountComponent";
import CardHeaderComponent from "./CardHeaderComponent";
import GridComponent from "./GridComponent";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche les compteurs publics et les acces aux entites Bibliotheque.
 *
 * @param {Object} props - Etat de page, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Page Bibliotheque publique.
 */
function LibraryHomeView({
  entities,
  entitiesError,
  isLoadingEntities,
  librarySearch,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenFeedback,
  onOpenWishlist,
  onOpenStatistics,
  onOpenLibraryPlatforms,
  onOpenLibraryStudios,
  onOpenLibraryGames,
  onOpenGameDetail = () => {},
  onOpenConfiguration,
  onLogout,
}) {
  const cards = [
    ["Plateformes", entities.platforms, onOpenLibraryPlatforms],
    ["Studios", entities.studios, onOpenLibraryStudios],
    ["Jeux", entities.games, onOpenLibraryGames],
  ];
  const resolvedLibrarySearch = librarySearch || {
    librarySearchQuery: "",
    librarySearchResults: [],
    librarySearchError: "",
    hasSearchedLibraryGames: false,
    isSearchingLibraryGames: false,
    closeLibrarySearch: () => {},
    searchLibraryGamesByName: (event) => event.preventDefault(),
    setLibrarySearchQuery: () => {},
  };
  const searchResults = resolvedLibrarySearch.librarySearchResults || [];
  const canCloseSearchResults = (
    resolvedLibrarySearch.hasSearchedLibraryGames || searchResults.length > 0
  ) && !resolvedLibrarySearch.isSearchingLibraryGames;
  const shouldDisplaySearchResultCount = canCloseSearchResults;
  const searchResultCountClassName = searchResults.length === 0
    ? "homeSearchResultCount homeSearchResultCountEmpty"
    : "homeSearchResultCount";

  return (
    <PageLayout
      shellClassName="appShell libraryShell"
      eyebrow="Bibliotheque publique"
      title="Bibliotheque"
      subtitle="Consultez les plateformes, studios et jeux du referentiel commun."
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenFeedback={onOpenFeedback}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {isLoadingEntities ? <ProgressBar label="Chargement de la Bibliotheque" /> : null}
      {entitiesError ? <p className="error">{entitiesError}</p> : null}

      <section
        className={`homeSearchSection ${canCloseSearchResults ? "homeSearchSectionClosable" : ""}`}
        aria-label="Recherche de jeux Bibliotheque"
      >
        {canCloseSearchResults ? (
          <button
            className="closeSearchButton"
            type="button"
            aria-label="Fermer les resultats de recherche"
            onClick={resolvedLibrarySearch.closeLibrarySearch}
          >
            x
          </button>
        ) : null}
        <form
          className={`homeSearchForm ${shouldDisplaySearchResultCount ? "homeSearchFormWithCount" : ""}`}
          onSubmit={resolvedLibrarySearch.searchLibraryGamesByName}
        >
          <div>
            <input
              id="library-home-search"
              type="search"
              value={resolvedLibrarySearch.librarySearchQuery}
              onChange={(event) => resolvedLibrarySearch.setLibrarySearchQuery(event.target.value)}
              placeholder="Rechercher un jeu"
              aria-label="Rechercher un jeu dans la Bibliotheque"
            />
            {shouldDisplaySearchResultCount ? (
              <span className={searchResultCountClassName}>
                {searchResults.length} resultats
              </span>
            ) : null}
            <button
              className="homeSearchSubmitButton"
              type="submit"
              disabled={resolvedLibrarySearch.isSearchingLibraryGames}
              aria-label="Lancer la recherche"
              title="Rechercher"
            >
              <svg aria-hidden="true" className="homeSearchSubmitIcon" viewBox="0 0 24 24">
                <path d="M10.5 4a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm0 2a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Zm5.2 9.3 4 4-1.4 1.4-4-4 1.4-1.4Z" />
              </svg>
            </button>
          </div>
        </form>

        {resolvedLibrarySearch.isSearchingLibraryGames ? <ProgressBar label="Recherche en cours" /> : null}
        {resolvedLibrarySearch.librarySearchError ? (
          <p className="error">{resolvedLibrarySearch.librarySearchError}</p>
        ) : null}

        {searchResults.length > 0 ? (
          <div className="searchResults">
            {searchResults.map((game, index) => (
              <article
                className="searchResultCard"
                key={`${game.id || game.name}-${game.platform}-${index}`}
                role="button"
                tabIndex={0}
                onClick={() => onOpenGameDetail(game)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onOpenGameDetail(game);
                  }
                }}
              >
                <div>
                  <span>{game.platform || "Plateforme inconnue"}</span>
                  <h3>{game.name}</h3>
                </div>
                <dl>
                  <div>
                    <dt>Developpeur</dt>
                    <dd>{formatCellValue("Studio", game.developer)}</dd>
                  </div>
                  <div>
                    <dt>Sortie</dt>
                    <dd>{formatCellValue("Date", game.release_date)}</dd>
                  </div>
                  <div>
                    <dt>Editeur</dt>
                    <dd>{formatCellValue("Studio", game.editor)}</dd>
                  </div>
                  <div>
                    <dt>Statut</dt>
                    <dd>{formatCellValue("Statut", game.status)}</dd>
                  </div>
                </dl>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onOpenGameDetail(game);
                  }}
                >
                  Voir le detail
                </button>
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <section className="platformSection libraryEntitySection">
        <GridComponent className="libraryEntityGrid">
          {cards.map(([label, count, onClick]) => (
            <CardComponent key={label} className="libraryEntityCard" onClick={onClick}>
              <CardHeaderComponent>
                <h3>{label}</h3>
                <CardCountComponent>{formatNumber(count)} elements</CardCountComponent>
              </CardHeaderComponent>
            </CardComponent>
          ))}
        </GridComponent>
      </section>
    </PageLayout>
  );
}

export default LibraryHomeView;
