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
 * Description : page publique generique des listes Bibliotheque.
 */
import { formatCellValue } from "../collectionUtils";
import MainMenu from "./MainMenu";
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";
import TableComponent from "./TableComponent";

/**
 * Affiche une liste paginee d'entites publiques Bibliotheque.
 *
 * @param {Object} props - Etat de liste, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Page de liste Bibliotheque.
 */
function LibraryEntityListView({
  title,
  subtitle,
  listState,
  isAuthenticated,
  authenticatedUsername,
  authenticatedProfile,
  platforms,
  selectedPlatform,
  onOpenAbout,
  onOpenHome,
  onOpenLibrary,
  onOpenPlatform,
  onOpenAdminDashboard,
  onLogout,
}) {
  return (
    <main className="appShell libraryShell">
      <header className="pageHeader libraryHeader">
        <MainMenu
          isAuthenticated={isAuthenticated}
          username={authenticatedUsername}
          profile={authenticatedProfile}
          platforms={platforms}
          selectedPlatform={selectedPlatform}
          onOpenAbout={onOpenAbout}
          onOpenHome={onOpenHome}
          onOpenLibrary={onOpenLibrary}
          onOpenPlatform={onOpenPlatform}
          onOpenAdminDashboard={onOpenAdminDashboard}
          onLogout={onLogout}
        />
        <div>
          <p className="eyebrow">Bibliotheque publique</p>
          <h1>
            <span className="pageTitleWithIcon">
              <ProjectIcon />
              <span>{title}</span>
            </span>
          </h1>
          <p className="subtitle">{subtitle}</p>
        </div>
      </header>

      <section className="libraryListSection">
        <form className="librarySearchForm" onSubmit={listState.submitSearch}>
          <label htmlFor="library-search">Recherche par nom</label>
          <div>
            <input
              id="library-search"
              type="search"
              value={listState.searchQuery}
              onChange={(event) => listState.setSearchQuery(event.target.value)}
              placeholder="Rechercher"
            />
            <button type="submit" disabled={listState.isLoading}>
              Rechercher
            </button>
            <button type="button" onClick={listState.clearSearch} disabled={listState.isLoading}>
              Effacer
            </button>
          </div>
        </form>

        {listState.isLoading ? <ProgressBar label="Chargement de la liste" /> : null}
        {listState.error ? <p className="error">{listState.error}</p> : null}
        {!listState.isLoading && listState.rows.length === 0 ? (
          <p>Aucune donnee a afficher.</p>
        ) : null}

        {listState.rows.length > 0 ? (
          <TableComponent
            rows={listState.rows}
            columns={listState.columns}
            columnLabels={listState.columnLabels}
            mobileVisibleColumns={["name"]}
            sortConfig={listState.sortConfig}
            sortableColumns={listState.sortableColumns}
            sortedRows={listState.rows}
            onToggleSort={listState.toggleSort}
            pagination={listState.pagination}
            formatCellValue={(column, value) => formatCellValue(column, value)}
            getRowKey={(row) => row.id || row.name}
          />
        ) : null}
      </section>
    </main>
  );
}

export default LibraryEntityListView;
