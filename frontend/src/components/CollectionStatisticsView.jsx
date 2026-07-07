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
import { useEffect, useMemo, useRef } from "react";

import { formatCellValue, formatNumber } from "../collectionUtils";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

const PLATFORM_CHART_COLORS = [
  "#15803d",
  "#2563eb",
  "#f59e0b",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
  "#84cc16",
  "#ea580c",
  "#0f766e",
  "#be123c",
];

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

      {statistics && !hasNoData ? (
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
            <PlatformPieChart
              rows={statistics.platformDistribution}
              selectedPlatformId={statisticsPage.selectedPlatformId}
              onTogglePlatform={statisticsPage.togglePlatformFilter}
            />
          </section>

          <section className="statisticsPanel" aria-label="Repartition par dates">
            <h2>Dates de sortie et d'achat</h2>
            <DateDistributionBarChart
              releaseRows={statistics.releaseYearDistribution}
              purchaseRows={statistics.purchaseYearDistribution}
            />
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
            ) : null}
          </section>
        </>
      ) : null}
    </PageLayout>
  );
}

/**
 * Affiche un camembert de repartition des jeux par plateforme.
 *
 * @param {Object} props - Lignes de repartition par plateforme.
 * @returns {import("react").JSX.Element} Graphique camembert avec legende.
 */
function PlatformPieChart({ rows, selectedPlatformId = null, onTogglePlatform = null }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const chartRows = useMemo(
    () => (Array.isArray(rows) ? rows.filter((row) => Number(row.gamesCount || 0) > 0) : []),
    [rows]
  );
  const chartColors = useMemo(
    () => chartRows.map((row, index) => {
      const baseColor = PLATFORM_CHART_COLORS[index % PLATFORM_CHART_COLORS.length];
      if (!selectedPlatformId || Number(row.id) === selectedPlatformId) {
        return baseColor;
      }
      return `${baseColor}55`;
    }),
    [chartRows, selectedPlatformId]
  );

  useEffect(() => {
    if (!canvasRef.current || chartRows.length === 0) {
      return undefined;
    }

    let isCancelled = false;
    const renderChart = async () => {
      const { default: Chart } = await import("chart.js/auto");
      if (isCancelled || !canvasRef.current) {
        return;
      }

      chartRef.current?.destroy();
      chartRef.current = new Chart(canvasRef.current, {
        type: "pie",
        data: {
          labels: chartRows.map((row) => row.label),
          datasets: [
            {
              data: chartRows.map((row) => row.gamesCount),
              backgroundColor: chartColors,
              borderColor: chartRows.map((row) => (
                Number(row.id) === selectedPlatformId ? "#111827" : "#ffffff"
              )),
              borderWidth: chartRows.map((row) => (
                Number(row.id) === selectedPlatformId ? 3 : 2
              )),
              hoverOffset: 8,
              offset: chartRows.map((row) => (
                Number(row.id) === selectedPlatformId ? 8 : 0
              )),
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const row = chartRows[context.dataIndex];
                  return `${row.label}: ${formatNumber(row.gamesCount)} jeux, ${row.ratio}%`;
                },
              },
            },
          },
        },
      });
    };
    renderChart();

    return () => {
      isCancelled = true;
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [chartRows, chartColors, selectedPlatformId]);

  if (chartRows.length === 0) {
    return <p className="emptyState">Aucune donnee disponible.</p>;
  }

  return (
    <div className="platformPieChart">
      <div className="platformPieCanvasFrame">
        <canvas
          ref={canvasRef}
          role="img"
          aria-label="Repartition des jeux par plateforme"
        />
      </div>
      <ol className="platformPieLegend" aria-label="Legende des plateformes">
        {chartRows.map((row, index) => (
          <li key={row.id || row.label}>
            <span
              className="platformPieLegendSwatch"
              style={{ backgroundColor: PLATFORM_CHART_COLORS[index % PLATFORM_CHART_COLORS.length] }}
              aria-hidden="true"
            />
            <button
              type="button"
              className="platformPieLegendButton"
              aria-pressed={Number(row.id) === selectedPlatformId}
              onClick={() => onTogglePlatform?.(Number(row.id))}
            >
              {row.label}
            </button>
            <strong>{formatNumber(row.gamesCount)} jeux</strong>
            <span>{row.ratio}%</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

/**
 * Affiche les repartitions par dates sur un graphique en barres.
 *
 * @param {Object} props - Repartitions par date.
 * @returns {import("react").JSX.Element} Graphique en barres groupees.
 */
function DateDistributionBarChart({ releaseRows, purchaseRows }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const chartRows = useMemo(() => {
    const rowsByYear = new Map();
    const registerRows = (rows, countKey) => {
      if (!Array.isArray(rows)) {
        return;
      }
      rows.forEach((row) => {
        const year = Number(row.year || row.label || 0);
        const gamesCount = Number(row.gamesCount || 0);
        if (!year || gamesCount <= 0) {
          return;
        }
        const currentRow = rowsByYear.get(year) || {
          year,
          releaseCount: 0,
          purchaseCount: 0,
        };
        currentRow[countKey] = gamesCount;
        rowsByYear.set(year, currentRow);
      });
    };

    registerRows(releaseRows, "releaseCount");
    registerRows(purchaseRows, "purchaseCount");

    return Array.from(rowsByYear.values()).sort((left, right) => left.year - right.year);
  }, [releaseRows, purchaseRows]);

  useEffect(() => {
    if (!canvasRef.current || chartRows.length === 0) {
      return undefined;
    }

    let isCancelled = false;
    const renderChart = async () => {
      const { default: Chart } = await import("chart.js/auto");
      if (isCancelled || !canvasRef.current) {
        return;
      }

      chartRef.current?.destroy();
      chartRef.current = new Chart(canvasRef.current, {
        type: "bar",
        data: {
          labels: chartRows.map((row) => String(row.year)),
          datasets: [
            {
              label: "Sorties",
              data: chartRows.map((row) => row.releaseCount),
              backgroundColor: "#2563eb",
              borderColor: "#1d4ed8",
              borderWidth: 1,
            },
            {
              label: "Achats",
              data: chartRows.map((row) => row.purchaseCount),
              backgroundColor: "#16a34a",
              borderColor: "#15803d",
              borderWidth: 1,
            },
          ],
        },
        options: {
          interaction: {
            intersect: false,
            mode: "index",
          },
          maintainAspectRatio: false,
          responsive: true,
          plugins: {
            legend: {
              labels: {
                boxWidth: 14,
                color: "#1f2937",
                font: {
                  weight: 700,
                },
              },
              position: "bottom",
            },
            tooltip: {
              callbacks: {
                label: (context) => `${context.dataset.label}: ${formatNumber(context.parsed.y)} jeux`,
              },
            },
          },
          scales: {
            x: {
              grid: {
                display: false,
              },
              ticks: {
                color: "#64748b",
              },
            },
            y: {
              beginAtZero: true,
              ticks: {
                color: "#64748b",
                precision: 0,
                callback: (value) => formatNumber(value),
              },
            },
          },
        },
      });
    };
    renderChart();

    return () => {
      isCancelled = true;
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [chartRows]);

  if (chartRows.length === 0) {
    return <p className="emptyState">Aucune donnee disponible.</p>;
  }

  return (
    <div className="dateDistributionChart">
      <div className="dateDistributionCanvasFrame">
        <canvas
          ref={canvasRef}
          role="img"
          aria-label="Repartition des jeux par dates de sortie et d'achat"
        />
      </div>
    </div>
  );
}

export default CollectionStatisticsView;
