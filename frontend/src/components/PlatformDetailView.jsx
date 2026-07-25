/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
import { useState } from "react";
import {
  formatCurrency,
  formatNumber,
} from "../collectionUtils";
import CollectionGamesTable from "./CollectionGamesTable";
import EditGameDialog from "./EditGameDialog";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";
import SortIcon from "./SortIcon";

/**
 * Page de detail d'une plateforme avec statistiques, filtres et tableau de jeux.
 *
 * @param {Object} props - Donnees de plateforme, tableau filtre/trie et callbacks.
 * @returns {import("react").JSX.Element} Vue detail plateforme.
 */
function PlatformDetailView({
  selectedPlatform,
  selectedPlatformStats,
  studioCount,
  platforms,
  games,
  columns,
  sortConfig,
  sortedGames,
  filteredGames,
  gameNameFilter = "",
  sortableColumns,
  deleteGameMessage,
  deleteGameError,
  error,
  isLoadingPlatforms,
  isLoadingGames,
  isSavingGame,
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
  canEditGame,
  canDeleteGame,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onBackToPlatforms,
  onOpenPlatform,
  onGameNameFilterChange = () => {},
  onToggleSort,
  onEditGame,
  onSaveGame,
  onCancelEditGame,
  onDeleteGame,
  onOpenGameDetail = () => {},
  editingGame,
}) {
  const [isMobileSortMenuOpen, setIsMobileSortMenuOpen] = useState(false);
  const isAllPlatformsSelected = !selectedPlatform;
  const allPlatformsStats = buildAllPlatformsStats(platforms, games);
  const displayedPlatformStats = selectedPlatformStats
    || (isAllPlatformsSelected ? allPlatformsStats : null);
  const selectedPlatformName = selectedPlatformStats?.name
    || platforms.find((platform) => String(platform.id) === String(selectedPlatform))?.name
    || (isAllPlatformsSelected ? "Tous les jeux" : "CloudCollectionApp");
  const platformFilterSubtitle = isAllPlatformsSelected
    ? "Toutes plateformes confondues"
    : "Filtrer la liste par plateforme";
  const platformStatsLabel = isAllPlatformsSelected
    ? "Statistiques de la collection"
    : "Statistiques de la plateforme";
  const emptyCollectionMessage = isAllPlatformsSelected
    ? "Aucun jeu a afficher dans la collection."
    : "Aucun jeu a afficher pour cette plateforme.";
  const activeSortLabel = sortConfig?.column || "Nom du jeu";
  const mobileSortColumns = sortableColumns || [];
  const handleMobileSort = (column) => {
    onToggleSort(column);
    setIsMobileSortMenuOpen(false);
  };

  /**
   * Indique si une note de jeu merite une mise en avant.
   *
   * @param {unknown} value - Valeur brute de la colonne `Note`.
   * @returns {boolean} `true` si la note est egale ou superieure a 9/10.
   */
  const isTopRatedGame = (value) => {
    const textValue = String(value || "").trim().replace(",", ".");
    if (!textValue) {
      return false;
    }

    const [scoreText, maxText] = textValue.split("/");
    const score = Number.parseFloat(scoreText);
    const max = Number.parseFloat(maxText || "10");
    if (Number.isNaN(score) || Number.isNaN(max) || max === 0) {
      return false;
    }

    return (score / max) * 10 >= 9;
  };

  return (
    <PageLayout
      shellClassName="container"
      eyebrow={isAllPlatformsSelected ? "Collection" : "Plateforme"}
      title={selectedPlatformName}
      subtitle={isGuest ? guestCollectionLabel : platformFilterSubtitle}
      headerClassName={`pageHeader${isGuest ? " guestSessionPageHeader" : ""}`}
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
      headerAsideContent={(
        <div
          className={`platformDetailStats ${
            isAuthenticated && canViewPrices
              ? "platformDetailStatsAuthenticated"
              : "platformDetailStatsPublic"
          }`}
          aria-label={platformStatsLabel}
        >
          <article>
            <span>Jeux</span>
            <strong>{formatNumber(displayedPlatformStats?.games_count ?? games.length)}</strong>
          </article>
          {isAuthenticated && canViewPrices ? (
            <>
              <article>
                <span>Valeur</span>
                <strong>{formatCurrency(displayedPlatformStats?.total_price)}</strong>
              </article>
              <article>
                <span>Prix moyen</span>
                <strong>{formatCurrency(displayedPlatformStats?.average_price)}</strong>
              </article>
            </>
          ) : null}
          <article>
            <span>Studios</span>
            <strong>{formatNumber(studioCount)}</strong>
          </article>
        </div>
      )}
    >
      {typeof onBackToPlatforms === "function" ? (
        <button className="backButton" type="button" onClick={onBackToPlatforms}>
          Retour aux plateformes
        </button>
      ) : null}

      {error ? <p className="error">{error}</p> : null}
      {deleteGameError ? <p className="error">{deleteGameError}</p> : null}
      {deleteGameMessage ? <p className="success">{deleteGameMessage}</p> : null}

      {isLoadingPlatforms ? <ProgressBar label="Chargement des plateformes" /> : null}
      <CollectionGamesTable
        games={games}
        columns={columns}
        sortConfig={sortConfig}
        sortedGames={sortedGames}
        filteredGames={filteredGames}
        isLoadingGames={isLoadingGames}
        emptyMessage={emptyCollectionMessage}
        sortableColumns={sortableColumns}
        columnLabels={{ "Prix d'achat": "Prix" }}
        tableClassName="collectionGamesTable"
        controlsContent={(
          <form className="librarySearchForm" onSubmit={(event) => event.preventDefault()}>
            <div className="collectionSearchHeader">
              <label htmlFor="collection-game-name-filter">Recherche par nom</label>
              <div className="mobileCollectionSortControl">
                <button
                  type="button"
                  className="mobileCollectionSortButton"
                  onClick={() => setIsMobileSortMenuOpen((isOpen) => !isOpen)}
                  aria-expanded={isMobileSortMenuOpen}
                  aria-haspopup="menu"
                  aria-label={`Trier les jeux, tri actif ${activeSortLabel}`}
                  title="Trier les jeux"
                >
                  <SortIcon column={activeSortLabel} sortConfig={sortConfig} />
                </button>
                {isMobileSortMenuOpen ? (
                  <div className="mobileCollectionSortMenu" role="menu">
                    <p className="mobileCollectionSortMenuHeader">Critere de tri</p>
                    {mobileSortColumns.map((column) => (
                      <button
                        type="button"
                        key={column}
                        role="menuitem"
                        className={sortConfig?.column === column ? "mobileSortMenuItemActive" : ""}
                        onClick={() => handleMobileSort(column)}
                      >
                        <span>{column}</span>
                        <SortIcon column={column} sortConfig={sortConfig} />
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
            <div>
              <div className="librarySearchInputControl">
                <input
                  id="collection-game-name-filter"
                  type="search"
                  value={gameNameFilter}
                  onChange={(event) => onGameNameFilterChange(event.target.value)}
                  placeholder="Rechercher"
                />
                <button
                  type="button"
                  className="librarySearchClearButton"
                  onClick={() => onGameNameFilterChange("")}
                  disabled={!gameNameFilter}
                  aria-label="Effacer la recherche"
                  title="Effacer la recherche"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="libraryPlatformFilter">
              <select
                id="platform"
                value={selectedPlatform}
                onChange={(event) => onOpenPlatform(event.target.value)}
                disabled={isLoadingPlatforms || platforms.length === 0}
                aria-label="Filtrer par plateforme"
              >
                <option value="">Toutes les plateformes</option>
                {platforms.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.name}
                  </option>
                ))}
              </select>
            </div>
          </form>
        )}
        onToggleSort={onToggleSort}
        getRowClassName={(game) =>
          isTopRatedGame(game.Note) ? "topRatedGameRow" : ""
        }
        onRowClick={onOpenGameDetail}
        renderRowActions={
          canEditGame || canDeleteGame
            ? (game) => (
                <div className="rowActionGroup">
                  {canEditGame ? (
                    <button
                      className="rowIconButton"
                      type="button"
                      aria-label={`Modifier ${game["Nom du jeu"] || "ce jeu"}`}
                      title="Modifier le jeu"
                      onClick={() => onEditGame(game)}
                    >
                      <svg aria-hidden="true" className="rowActionIcon" viewBox="0 0 24 24">
                        <path d="M4 17.5V21h3.5L18.1 10.4l-3.5-3.5L4 17.5Z" />
                        <path d="m16 5.5 1.6-1.6a1.2 1.2 0 0 1 1.7 0l.8.8a1.2 1.2 0 0 1 0 1.7L18.5 8 16 5.5Z" />
                      </svg>
                    </button>
                  ) : null}
                  {canDeleteGame ? (
                    <button
                      className="rowIconButton dangerIconButton"
                      type="button"
                      aria-label={`Supprimer ${game["Nom du jeu"] || "ce jeu"} de la plateforme`}
                      title="Supprimer de la plateforme"
                      onClick={() => onDeleteGame(game)}
                    >
                      <svg aria-hidden="true" className="rowActionIcon" viewBox="0 0 24 24">
                        <path d="M9 3h6l1 2h4v2H4V5h4l1-2Z" />
                        <path d="M6 9h12l-1 12H7L6 9Zm4 2v8h2v-8h-2Zm4 0v8h2v-8h-2Z" />
                      </svg>
                    </button>
                  ) : null}
                </div>
              )
            : null
        }
      />

      <EditGameDialog
        game={editingGame}
        isSaving={isSavingGame}
        onSubmit={onSaveGame}
        onCancel={onCancelEditGame}
      />

    </PageLayout>
  );
}

/**
 * Agrege les statistiques visibles pour la consultation toutes plateformes.
 *
 * @param {Array<Object>} platforms - Plateformes de la collection.
 * @param {Array<Object>} games - Jeux charges pour la vue courante.
 * @returns {Object} Statistiques synthetiques de collection.
 */
function buildAllPlatformsStats(platforms, games) {
  const totalPrice = platforms.reduce(
    (total, platform) => total + Number(platform.total_price || 0),
    0
  );
  const gamesCount = games.length;
  return {
    games_count: gamesCount,
    total_price: totalPrice,
    average_price: gamesCount > 0 ? totalPrice / gamesCount : 0,
  };
}

export default PlatformDetailView;
