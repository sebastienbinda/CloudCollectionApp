/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-08
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : tableau partage de consultation des jeux de collection.
 */
import ProgressBar from "./ProgressBar";
import TableComponent from "./TableComponent";

/**
 * Affiche le tableau de jeux partage par les vues collection.
 *
 * @param {Object} props - Configuration de rendu du tableau de jeux.
 * @param {Array<Object>} props.games - Jeux normalises a afficher.
 * @param {Array<string>} props.columns - Colonnes visibles.
 * @param {Object} props.sortConfig - Configuration de tri courante.
 * @param {Array<Object>} props.sortedGames - Jeux tries et filtres.
 * @param {Array<Object>} props.filteredGames - Jeux filtres avant affichage final.
 * @param {boolean} props.isLoadingGames - Indique si les jeux sont en cours de chargement.
 * @param {string} props.loadingLabel - Libelle de chargement.
 * @param {string} props.emptyMessage - Message affiche sans jeu.
 * @param {string} props.filteredEmptyMessage - Message affiche si les filtres masquent tout.
 * @param {import("react").ReactNode} props.controlsContent - Controles affiches avant le tableau.
 * @param {Array<string>|null} props.sortableColumns - Colonnes triables, ou toutes si absent.
 * @param {Function} props.onToggleSort - Callback de tri.
 * @param {Function|null} props.getRowClassName - Callback de classe de ligne.
 * @param {Function|null} props.renderRowActions - Callback de rendu des actions.
 * @param {Function|null} props.onRowClick - Callback d'ouverture d'une ligne.
 * @param {Object|null} props.columnLabels - Libelles visibles par colonne technique.
 * @param {string|null} props.tableClassName - Classe CSS specifique du tableau.
 * @returns {import("react").JSX.Element} Tableau et etats associes.
 */
function CollectionGamesTable({
  games,
  columns,
  sortConfig,
  sortedGames,
  filteredGames,
  isLoadingGames,
  loadingLabel = "Chargement des jeux",
  emptyMessage = "Aucun jeu a afficher.",
  filteredEmptyMessage = "Aucun jeu ne correspond aux filtres.",
  controlsContent = null,
  sortableColumns = null,
  onToggleSort,
  getRowClassName = null,
  renderRowActions = null,
  onRowClick = null,
  columnLabels = null,
  tableClassName = null,
}) {
  return (
    <>
      {controlsContent}

      {isLoadingGames ? <ProgressBar label={loadingLabel} /> : null}

      {!isLoadingGames && games.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : null}

      {!isLoadingGames && games.length > 0 ? (
        <TableComponent
          rows={games}
          columns={columns}
          sortConfig={sortConfig}
          sortedRows={sortedGames}
          sortableColumns={sortableColumns}
          onToggleSort={onToggleSort}
          getRowClassName={getRowClassName}
          renderRowActions={renderRowActions}
          onRowClick={onRowClick}
          columnLabels={columnLabels}
          tableClassName={tableClassName}
        />
      ) : null}

      {!isLoadingGames && games.length > 0 && filteredGames.length === 0 ? (
        <p>{filteredEmptyMessage}</p>
      ) : null}
    </>
  );
}

export default CollectionGamesTable;
