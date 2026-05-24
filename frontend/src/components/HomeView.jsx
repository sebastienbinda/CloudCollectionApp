import { formatCellValue, formatCurrency, formatNumber } from "../collectionUtils";
import CardComponent from "./CardComponent";
import CardCountComponent from "./CardCountComponent";
import CardHeaderComponent from "./CardHeaderComponent";
import GridComponent from "./GridComponent";
import MainMenu from "./MainMenu";
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";

/**
 * Page d'accueil avec statistiques, recherche globale et cartes plateformes.
 *
 * @param {Object} props - Donnees et callbacks necessaires a la page d'accueil.
 * @returns {import("react").JSX.Element} Vue d'accueil.
 */
function HomeView({
  homeStats,
  platforms,
  selectedPlatform,
  error,
  isLoadingHome,
  isSearchingGames,
  hasSearchedGames,
  homeSearchQuery,
  homeSearchResults,
  homeSearchError,
  isAuthenticated,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenHome,
  onOpenAdminDashboard,
  onLogout,
  onOpenWishlist,
  onOpenPlatform,
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
  return (
    <main className="appShell">
      <header className="pageHeader">
        <MainMenu
          isAuthenticated={isAuthenticated}
          username={authenticatedUsername}
          profile={authenticatedProfile}
          platforms={platforms}
          selectedPlatform={selectedPlatform}
          onOpenAbout={onOpenAbout}
          onOpenHome={onOpenHome}
          onOpenWishlist={onOpenWishlist}
          onOpenPlatform={onOpenPlatform}
          onOpenAdminDashboard={onOpenAdminDashboard}
          onLogout={onLogout}
        />
        <div>
          <p className="eyebrow">Collection personnelle</p>
          <h1>
            <span className="pageTitleWithIcon">
              <ProjectIcon />
              <span>{homeStats?.title || "Ma collection"}</span>
            </span>
          </h1>
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
          <p className="subtitle">Jeux, plateformes et statistiques essentielles.</p>
        </div>
      </header>

      {error ? <p className="error">{error}</p> : null}
      {isLoadingHome ? <ProgressBar label="Chargement des statistiques" /> : null}

      {!isLoadingHome && homeStats ? (
        <>
          <section className="homeSearchSection" aria-label="Recherche de jeux">
            {(hasSearchedGames || homeSearchResults.length > 0) && !isSearchingGames ? (
              <button
                className="closeSearchButton"
                type="button"
                aria-label="Fermer les resultats de recherche"
                onClick={onCloseSearch}
              >
                x
              </button>
            ) : null}
            <form className="homeSearchForm" onSubmit={onSearchSubmit}>
              <div>
                <input
                  id="home-search"
                  type="search"
                  value={homeSearchQuery}
                  onChange={(event) => onSearchQueryChange(event.target.value)}
                  placeholder="Rechercher un jeu"
                  aria-label="Rechercher un jeu"
                />
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
            {hasSearchedGames && !isSearchingGames && homeSearchResults.length === 0 ? (
              <p>Aucun jeu trouve pour cette recherche.</p>
            ) : null}

            {homeSearchResults.length > 0 ? (
              <div className="searchResults">
                {homeSearchResults.map((game, index) => (
                  <article
                    className="searchResultCard"
                    key={`${game.Plateforme}-${game["Nom du jeu"]}-${index}`}
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
                      {isAuthenticated ? (
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
                    <button type="button" onClick={() => onOpenPlatform(game.Plateforme)}>
                      Voir la plateforme
                    </button>
                  </article>
                ))}
              </div>
            ) : null}
          </section>

          <section
            className={`statsGrid ${isAuthenticated ? "statsGridAuthenticated" : "statsGridPublic"}`}
            aria-label="Statistiques principales"
          >
            <article className="statCard">
              <span>Total jeux</span>
              <strong>{formatNumber(homeStats.totals?.games_count)}</strong>
            </article>
            {isAuthenticated ? (
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
                <span>{formatNumber(homeStats.platforms?.length || 0)} onglets</span>
              </div>
            </div>
            <GridComponent>
              {(homeStats.platforms || []).map((platform) => (
                <CardComponent
                  className={[
                    platform.has_image ? "platformCardWithImage" : "",
                    topPlatform?.sheet_name === platform.sheet_name ? "platformCardTopCount" : "",
                  ].join(" ")}
                  key={platform.name}
                  onClick={() => onOpenPlatform(platform.sheet_name)}
                  style={
                    platform.image_url
                      ? { backgroundImage: `url("${encodeURI(platform.image_url)}")` }
                      : undefined
                  }
                >
                  <CardHeaderComponent>
                    <h3>{platform.name}</h3>
                    <CardCountComponent>
                      {formatNumber(platform.games_count)} jeux
                    </CardCountComponent>
                  </CardHeaderComponent>
                  {isAuthenticated ? (
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
    </main>
  );
}

export default HomeView;
