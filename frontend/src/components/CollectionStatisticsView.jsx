/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React des statistiques detaillees de collection.
 */
import { formatCellValue, formatNumber } from "../collectionUtils";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche les statistiques detaillees de la collection.
 *
 * @param {Object} props - Donnees et callbacks de la page.
 * @returns {import("react").JSX.Element} Vue statistiques.
 */
function CollectionStatisticsView({
  statisticsPage,
  isGuest = false,
  guestCollectionLabel = "",
  ...layoutProps
}) {
  const statistics = statisticsPage?.statistics;
  const hasNoData = statistics && statistics.totalGames === 0;

  return (
    <PageLayout
      {...layoutProps}
      eyebrow="Collection personnelle"
      title="Statistiques"
      subtitle={isGuest ? guestCollectionLabel : "Repartitions et jeux les mieux notes."}
      headerClassName={`pageHeader${isGuest ? " guestSessionPageHeader" : ""}`}
      shellClassName="appShell collectionStatisticsShell"
    >
      {statisticsPage?.statisticsError ? (
        <p className="error">{statisticsPage.statisticsError}</p>
      ) : null}
      {statisticsPage?.isLoadingStatistics ? (
        <ProgressBar label="Chargement des statistiques" />
      ) : null}

      {!statisticsPage?.isLoadingStatistics && hasNoData ? (
        <p className="emptyState">Aucune statistique disponible pour cette collection.</p>
      ) : null}

      {!statisticsPage?.isLoadingStatistics && statistics && !hasNoData ? (
        <>
          <section className="statisticsSummary" aria-label="Synthese statistiques">
            <article className="statCard">
              <span>Total jeux</span>
              <strong>{formatNumber(statistics.totalGames)}</strong>
            </article>
            <article className="statCard">
              <span>Plateformes</span>
              <strong>{formatNumber(statistics.platformDistribution.length)}</strong>
            </article>
            <article className="statCard">
              <span>Jeux notes &gt; 9</span>
              <strong>{formatNumber(statistics.topRatedGames.length)}</strong>
            </article>
          </section>

          <section className="statisticsPanel" aria-label="Proportion par plateforme">
            <h2>Jeux par plateforme</h2>
            <StatisticsBars
              rows={statistics.platformDistribution}
              valueFormatter={(row) => `${formatNumber(row.gamesCount)} jeux - ${row.ratio}%`}
              widthResolver={(row) => row.ratio}
            />
          </section>

          <section className="statisticsTimelineGrid" aria-label="Repartitions temporelles">
            <div className="statisticsPanel">
              <h2>Dates de sortie</h2>
              <StatisticsBars rows={statistics.releaseYearDistribution} />
            </div>
            <div className="statisticsPanel">
              <h2>Dates d'achat</h2>
              <StatisticsBars rows={statistics.purchaseYearDistribution} />
            </div>
          </section>

          <section className="statisticsPanel" aria-label="Jeux les mieux notes">
            <div className="statisticsSectionHeader">
              <h2>Jeux les mieux notes</h2>
              <span>{formatNumber(statistics.topRatedGames.length)} jeux</span>
            </div>
            {statistics.topRatedGames.length > 0 ? (
              <div className="topRatedGamesList">
                {statistics.topRatedGames.map((game) => (
                  <article className="topRatedGame" key={game.id}>
                    <div>
                      <h3>{game.name}</h3>
                      <span>{game.platformName}</span>
                    </div>
                    <dl>
                      <div>
                        <dt>Sortie</dt>
                        <dd>{formatCellValue("Date", game.releaseDate)}</dd>
                      </div>
                      <div>
                        <dt>Achat</dt>
                        <dd>{formatCellValue("Date", game.buyDate)}</dd>
                      </div>
                      <div>
                        <dt>Note</dt>
                        <dd>{formatCellValue("Note", game.grade)}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            ) : (
              <p className="emptyState">Aucun jeu avec une note superieure a 9.</p>
            )}
          </section>
        </>
      ) : null}
    </PageLayout>
  );
}

/**
 * Affiche une serie de barres statistiques.
 *
 * @param {Object} props - Lignes et formateurs de barres.
 * @returns {import("react").JSX.Element} Liste de barres.
 */
function StatisticsBars({
  rows,
  valueFormatter = (row) => `${formatNumber(row.gamesCount)} jeux`,
  widthResolver = null,
}) {
  const maxCount = Math.max(...(rows || []).map((row) => row.gamesCount || 0), 1);
  if (!rows || rows.length === 0) {
    return <p className="emptyState">Aucune donnee disponible.</p>;
  }
  return (
    <div className="statisticsBars">
      {rows.map((row) => {
        const width = widthResolver
          ? widthResolver(row)
          : Math.round(((row.gamesCount || 0) / maxCount) * 100);
        return (
          <div className="statisticsBarRow" key={row.id || row.label}>
            <div className="statisticsBarLabels">
              <span>{row.label}</span>
              <strong>{valueFormatter(row)}</strong>
            </div>
            <div className="statisticsBarTrack" aria-hidden="true">
              <span style={{ width: `${Math.max(width, 4)}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default CollectionStatisticsView;
