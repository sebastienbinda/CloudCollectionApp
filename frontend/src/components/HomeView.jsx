import { formatCellValue, formatCurrency, formatNumber } from "../collectionUtils";
import CardComponent from "./CardComponent";
import CardCountComponent from "./CardCountComponent";
import CardHeaderComponent from "./CardHeaderComponent";
import GridComponent from "./GridComponent";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Page d'accueil avec statistiques, recherche globale et cartes plateformes.
 *
 * @param {Object} props - Donnees et callbacks necessaires a la page d'accueil.
 * @returns {import("react").JSX.Element} Vue d'accueil.
 */
function HomeView({
  homeStats,
  error,
  isLoadingHome,
  isSearchingGames,
  hasSearchedGames,
  homeSearchQuery,
  homeSearchResults,
  homeSearchError,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  canViewPrices = true,
  isGuest = false,
  guestCollectionLabel = "",
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onOpenPlatform,
  onOpenGameDetail = () => {},
  onSearchQueryChange,
  onSearchSubmit,
  onCloseSearch,
}) {
  const topPlatform = homeStats?.platforms?.reduce((top, platform) => {
    if (!top || (platform.games_count || 0) > (top.games_count || 0)) {
      return platform;
    }
    return top;
  }, null);
  const canCloseSearchResults = (hasSearchedGames || homeSearchResults.length > 0)
    && !isSearchingGames;
  const shouldDisplaySearchResultCount = canCloseSearchResults;
  const searchResultCountClassName = homeSearchResults.length === 0
    ? "homeSearchResultCount homeSearchResultCountEmpty"
    : "homeSearchResultCount";

  return (
    <PageLayout
      eyebrow="Collection personnelle"
      title={homeStats?.title || "Ma collection"}
      subtitle={isGuest ? guestCollectionLabel : "Jeux, plateformes et statistiques essentielles."}
      headerClassName={`pageHeader${isGuest ? " guestSessionPageHeader" : ""}`}
      headerExtraContent={(
        <p className="pageHeaderDateSummary">
          <span>
            <span className="pageHeaderDateLabel">Premier jeu : </span>
            {formatCellValue("Date", homeStats?.first_game_date)}
          </span>
          <span className="pageHeaderDateSeparator">-</span>
          <span>
            <span className="pageHeaderDateLabel">Dernier jeu : </span>
            {formatCellValue("Date", homeStats?.last_game_date)}
          </span>
        </p>
      )}
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
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {error ? <p className="error">{error}</p> : null}
      {isLoadingHome ? <ProgressBar label="Chargement des statistiques" /> : null}

      {!isLoadingHome && homeStats ? (
        <>
          <section
            className={`homeSearchSection ${canCloseSearchResults ? "homeSearchSectionClosable" : ""}`}
            aria-label="Recherche de jeux"
          >
            {canCloseSearchResults ? (
              <button
                className="closeSearchButton"
                type="button"
                aria-label="Fermer les resultats de recherche"
                onClick={onCloseSearch}
              >
                x
              </button>
            ) : null}
            <form
              className={`homeSearchForm ${shouldDisplaySearchResultCount ? "homeSearchFormWithCount" : ""}`}
              onSubmit={onSearchSubmit}
            >
              <div>
                <input
                  id="home-search"
                  type="search"
                  value={homeSearchQuery}
                  onChange={(event) => onSearchQueryChange(event.target.value)}
                  placeholder="Rechercher un jeu"
                  aria-label="Rechercher un jeu"
                />
                {shouldDisplaySearchResultCount ? (
                  <span className={searchResultCountClassName}>
                    {homeSearchResults.length} resultats
                  </span>
                ) : null}
                <button
                  className="homeSearchSubmitButton"
                  type="submit"
                  disabled={isSearchingGames}
                  aria-label="Lancer la recherche"
                  title="Rechercher"
                >
                  <svg aria-hidden="true" className="homeSearchSubmitIcon" viewBox="0 0 24 24">
                    <path d="M10.5 4a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm0 2a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Zm5.2 9.3 4 4-1.4 1.4-4-4 1.4-1.4Z" />
                  </svg>
                </button>
              </div>
            </form>

            {isSearchingGames ? <ProgressBar label="Recherche en cours" /> : null}
            {homeSearchError ? <p className="error">{homeSearchError}</p> : null}

            {homeSearchResults.length > 0 ? (
              <div className="searchResults">
                {homeSearchResults.map((game, index) => (
                  <article
                    className="searchResultCard"
                    key={`${game.platform_id}-${game["Nom du jeu"]}-${index}`}
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
                      <span>{game.Plateforme}</span>
                      <h3>{game["Nom du jeu"]}</h3>
                    </div>
                    <dl>
                      <div>
                        <dt>Studio</dt>
                        <dd>{formatCellValue("Studio", game.Studio)}</dd>
                      </div>
                      <div>
                        <dt>Sortie</dt>
                        <dd>{formatCellValue("Date", game["Date de sortie"])}</dd>
                      </div>
                      <div>
                        <dt>Achat</dt>
                        <dd>{formatCellValue("Date", game["Date d'achat"])}</dd>
                      </div>
                      <div>
                        <dt>Note</dt>
                        <dd>{formatCellValue("Note", game.Note)}</dd>
                      </div>
                      {isAuthenticated && canViewPrices ? (
                        <div>
                          <dt>Prix</dt>
                          <dd>{formatCurrency(game["Prix d'achat"])}</dd>
                        </div>
                      ) : null}
                      <div>
                        <dt>Version</dt>
                        <dd>{formatCellValue("Version", game.Version)}</dd>
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

          <section
            className={`statsGrid ${isAuthenticated && canViewPrices ? "statsGridAuthenticated" : "statsGridPublic"}`}
            aria-label="Statistiques principales"
          >
            <article className="statCard">
              <span>Total jeux</span>
              <strong>{formatNumber(homeStats.totals?.games_count)}</strong>
            </article>
            {isAuthenticated && canViewPrices ? (
              <>
                <article className="statCard">
                  <span>Valeur totale</span>
                  <strong>{formatCurrency(homeStats.totals?.total_price)}</strong>
                </article>
                <article className="statCard">
                  <span>Prix moyen</span>
                  <strong>{formatCurrency(homeStats.totals?.average_price)}</strong>
                </article>
              </>
            ) : null}
            <article className="statCard statCardTopPlatform">
              <span>Plateforme la plus fournie</span>
              <strong>{topPlatform ? topPlatform.name : "-"}</strong>
            </article>
          </section>

          <section className="platformSection">
            <div className="sectionHeader">
              <div>
                <h2>Plateformes</h2>
                <span>{formatNumber(homeStats.platforms?.length || 0)} plateformes</span>
              </div>
            </div>
            <GridComponent>
              {(homeStats.platforms || []).map((platform) => (
                <CardComponent
                  className={[
                    topPlatform?.id === platform.id ? "platformCardTopCount" : "",
                  ].join(" ")}
                  key={platform.id || platform.name}
                  onClick={() => onOpenPlatform(platform.id)}
                >
                  <CardHeaderComponent>
                    <h3>{platform.name}</h3>
                    <CardCountComponent>
                      {formatNumber(platform.games_count)} jeux
                    </CardCountComponent>
                  </CardHeaderComponent>
                  <p className="platformLifecycle">
                    {formatPlatformLifecycle(platform)}
                  </p>
                  {isAuthenticated && canViewPrices ? (
                    <dl>
                      <div>
                        <dt>Prix</dt>
                        <dd>{formatCurrency(platform.total_price)}</dd>
                      </div>
                      <div>
                        <dt>Moyen</dt>
                        <dd>{formatCurrency(platform.average_price)}</dd>
                      </div>
                    </dl>
                  ) : null}
                </CardComponent>
              ))}
            </GridComponent>
          </section>
        </>
      ) : null}
    </PageLayout>
  );
}

/**
 * Formate les dates de vie commerciale d'une plateforme.
 *
 * @param {Object} platform - Plateforme normalisee par le service frontend.
 * @returns {string} Dates de sortie et retrait affichees sur une ligne.
 */
function formatPlatformLifecycle(platform) {
  const releaseDate = formatCellValue("Date", platform.release_date);
  const endDate = formatCellValue("Date", platform.end_date);
  return `${releaseDate || "-"} / ${endDate || "-"}`;
}

export default HomeView;
