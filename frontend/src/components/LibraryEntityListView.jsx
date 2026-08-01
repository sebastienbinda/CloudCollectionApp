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
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";
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
  renderRowActions = null,
  onRowClick = null,
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
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onBackToLibrary,
}) {
  const renderValidationRowSelection = (row) => {
    const workflow = listState.validationWorkflow;
    const isWaitingValidation = String(row.status || "").toUpperCase() === "WAITING_VALIDATION";
    if (!workflow || !isWaitingValidation) {
      return null;
    }
    const isSelected = workflow.selectedGameIds.includes(row.id);
    return (
      <label className="libraryValidationRowSelection">
        <input
          type="checkbox"
          aria-label={`Selectionner ${row.name || "ce jeu"}`}
          checked={isSelected}
          disabled={workflow.isRunningAction}
          onChange={() => workflow.onToggleGameSelection(row.id)}
        />
      </label>
    );
  };

  const resolvedRenderRowActions = listState.validationWorkflow
    ? renderValidationRowSelection
    : renderRowActions;

  return (
    <PageLayout
      shellClassName="appShell libraryShell"
      eyebrow="Bibliotheque publique"
      title={title}
      subtitle={subtitle}
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
      {typeof onBackToLibrary === "function" ? (
        <button className="backButton" type="button" onClick={onBackToLibrary}>
          Retour a la Bibliotheque
        </button>
      ) : null}

      <section className="libraryListSection">
        <form className="librarySearchForm" onSubmit={listState.submitSearch}>
          <label htmlFor="library-search">Recherche par nom</label>
          <div>
            <div className="librarySearchInputControl">
              <input
                id="library-search"
                type="search"
                value={listState.searchQuery}
                onChange={(event) => listState.setSearchQuery(event.target.value)}
                placeholder="Rechercher"
              />
              <button
                type="button"
                className="librarySearchClearButton"
                onClick={listState.clearSearch}
                disabled={listState.isLoading || !listState.searchQuery}
                aria-label="Effacer la recherche"
                title="Effacer la recherche"
              >
                ×
              </button>
            </div>
            {!listState.autoSearchEnabled ? (
              <button type="submit" disabled={listState.isLoading}>
                Rechercher
              </button>
            ) : null}
          </div>
          {listState.platformFilter ? (
            <div className="libraryPlatformFilter">
              <select
                id="library-platform-filter"
                value={listState.platformFilter.selectedValue}
                onChange={(event) => listState.platformFilter.onChange(event.target.value)}
                disabled={listState.platformFilter.isLoading}
                aria-label="Filtrer par plateforme"
              >
                <option value="">Toutes les plateformes</option>
                {listState.platformFilter.options.map((platform) => (
                  <option key={platform.id || platform.name} value={platform.name}>
                    {platform.name}
                  </option>
                ))}
              </select>
              {listState.platformFilter.error ? (
                <span className="error">{listState.platformFilter.error}</span>
              ) : null}
            </div>
          ) : null}
          {listState.duplicateFlagFilter ? (
            <div className="libraryPlatformFilter">
              <select
                id="library-duplicate-flag-filter"
                value={listState.duplicateFlagFilter.selectedValue}
                onChange={(event) => listState.duplicateFlagFilter.onChange(event.target.value)}
                aria-label="Filtrer par signalement doublon"
              >
                <option value="">Tous les statuts doublon</option>
                <option value="true">Doublons signales</option>
                <option value="false">Non signales</option>
              </select>
            </div>
          ) : null}
          {listState.validationStatusFilter ? (
            <div className="libraryPlatformFilter">
              <select
                id="library-validation-status-filter"
                value={listState.validationStatusFilter.selectedValue}
                onChange={(event) => listState.validationStatusFilter.onChange(event.target.value)}
                aria-label="Filtrer par statut de validation"
              >
                {listState.validationStatusFilter.options.map((option) => (
                  <option key={option.value || "all"} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          ) : null}
        </form>

        {listState.validationWorkflow ? (
          <div className="libraryValidationToolbar">
            <label className="libraryValidationSelectAll">
              <input
                type="checkbox"
                checked={listState.validationWorkflow.areAllVisibleWaitingGamesSelected}
                disabled={
                  listState.validationWorkflow.isRunningAction ||
                  listState.validationWorkflow.visibleWaitingValidationGameIds.length === 0
                }
                onChange={listState.validationWorkflow.onToggleVisibleSelection}
              />
              <span>Tout selectionner</span>
            </label>
            <div className="libraryValidationActions">
              <span>{listState.validationWorkflow.selectedCount} selection(s)</span>
              <button
                type="button"
                disabled={
                  listState.validationWorkflow.isRunningAction ||
                  listState.validationWorkflow.selectedCount === 0
                }
                onClick={listState.validationWorkflow.onValidateSelection}
              >
                Valider
              </button>
              <button
                type="button"
                className="secondaryButton"
                disabled={
                  listState.validationWorkflow.isRunningAction ||
                  listState.validationWorkflow.selectedCount === 0
                }
                onClick={listState.validationWorkflow.onRefuseSelection}
              >
                Refuser
              </button>
            </div>
            {listState.validationWorkflow.message ? (
              <p className="success">{listState.validationWorkflow.message}</p>
            ) : null}
            {listState.validationWorkflow.error ? (
              <p className="error">{listState.validationWorkflow.error}</p>
            ) : null}
          </div>
        ) : null}

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
            mobileVisibleColumns={listState.mobileVisibleColumns}
            sortConfig={listState.sortConfig}
            sortableColumns={listState.sortableColumns}
            sortedRows={listState.rows}
            tableClassName={listState.tableClassName}
            formatCellValue={listState.formatCellValue}
            onToggleSort={listState.toggleSort}
            pagination={listState.pagination}
            renderRowActions={resolvedRenderRowActions}
            actionColumnLabel={listState.validationWorkflow ? "" : undefined}
            actionColumnPosition={listState.validationWorkflow ? "left" : "right"}
            onRowClick={onRowClick}
            getRowKey={(row) => row.id || row.name}
          />
        ) : null}
      </section>
    </PageLayout>
  );
}

export default LibraryEntityListView;
