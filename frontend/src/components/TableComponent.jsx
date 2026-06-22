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
 * Description : composant tableau reutilisable avec tri, filtres et pagination.
 */
import { Component } from "react";
import {
  getColumnClassName,
  getDateYearOptions,
  isDateColumn,
  isSelectFilterColumn,
} from "../collectionUtils";
import TableColumnFormatService from "../services/TableColumnFormatService.jsx";
import SortIcon from "./SortIcon";

/**
 * Tableau generique avec filtres par colonne, tri et controles de pagination.
 */
class TableComponent extends Component {
  /**
   * Met a jour un filtre textuel ou select pour une colonne.
   *
   * @param {string} column - Nom de la colonne filtree.
   * @param {string} value - Nouvelle valeur du filtre.
   * @returns {void} Transmet la mise a jour au parent React.
   */
  updateSimpleFilter(column, value) {
    this.props.onColumnFiltersChange?.((previous) => ({
      ...previous,
      [column]: value,
    }));
  }

  /**
   * Met a jour l'operateur du filtre de date.
   *
   * @param {string} column - Nom de la colonne date filtree.
   * @param {string} operator - Operateur de comparaison selectionne.
   * @returns {void} Transmet la mise a jour au parent React.
   */
  updateDateOperator(column, operator) {
    this.props.onColumnFiltersChange?.((previous) => ({
      ...previous,
      [column]: {
        operator,
        year: previous[column]?.year || "",
      },
    }));
  }

  /**
   * Met a jour l'annee du filtre de date.
   *
   * @param {string} column - Nom de la colonne date filtree.
   * @param {string} year - Annee selectionnee.
   * @returns {void} Transmet la mise a jour au parent React.
   */
  updateDateYear(column, year) {
    this.props.onColumnFiltersChange?.((previous) => ({
      ...previous,
      [column]: {
        operator: previous[column]?.operator || "=",
        year,
      },
    }));
  }

  /**
   * Retourne les lignes a afficher dans le tableau.
   *
   * @returns {Array<Object>} Lignes triees ou lignes brutes fournies.
   */
  getRows() {
    return (
      this.props.sortedRows ||
      this.props.sortedGames ||
      this.props.rows ||
      this.props.games ||
      []
    );
  }

  /**
   * Rend le controle de filtre adapte au type de colonne.
   *
   * @param {string} column - Nom de la colonne a filtrer.
   * @returns {import("react").JSX.Element|null} Controle de filtre pour la colonne.
   */
  renderColumnFilter(column) {
    const { columnFilters = {}, valuesByColumn = {}, renderColumnFilter } = this.props;

    if (renderColumnFilter) {
      const customFilter = renderColumnFilter(column);
      if (customFilter !== undefined) {
        return customFilter;
      }
    }

    if (!this.props.onColumnFiltersChange) {
      return null;
    }

    if (isSelectFilterColumn(column)) {
      return (
        <select
          value={columnFilters[column] || ""}
          onChange={(event) => this.updateSimpleFilter(column, event.target.value)}
        >
          <option value="">Tous</option>
          {(valuesByColumn[column] || []).map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
      );
    }

    if (isDateColumn(column)) {
      return (
        <div className="dateFilterGroup">
          <select
            value={columnFilters[column]?.operator || "="}
            onChange={(event) => this.updateDateOperator(column, event.target.value)}
          >
            <option value="=">{"="}</option>
            <option value=">">{">"}</option>
            <option value="<">{"<"}</option>
          </select>
          <select
            value={columnFilters[column]?.year || ""}
            onChange={(event) => this.updateDateYear(column, event.target.value)}
          >
            <option value="">Toutes</option>
            {getDateYearOptions(valuesByColumn, column).map((year) => (
              <option key={`${column}-${year}`} value={String(year)}>
                {year}
              </option>
            ))}
          </select>
        </div>
      );
    }

    return (
      <input
        type="text"
        value={columnFilters[column] || ""}
        onChange={(event) => this.updateSimpleFilter(column, event.target.value)}
        placeholder="Filtrer..."
      />
    );
  }

  /**
   * Retourne le libelle affiche pour une colonne.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {string} Libelle visible dans l'en-tete du tableau.
   */
  getColumnLabel(column) {
    return this.props.columnLabels?.[column] || column;
  }

  /**
   * Retourne le nom de colonne utilise pour les attributs de rendu.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {string} Nom expose dans `data-column`.
   */
  getColumnDataName(column) {
    return this.props.columnDataNames?.[column] || column;
  }

  /**
   * Retourne les classes CSS d'une colonne de tableau.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {string} Classes CSS combinees.
   */
  getColumnClassNames(column) {
    const classes = [getColumnClassName(column)];
    if ((this.props.mobileVisibleColumns || []).includes(column)) {
      classes.push("mobileVisibleColumn");
    }

    return classes.filter(Boolean).join(" ");
  }

  /**
   * Retourne la valeur brute a afficher pour une cellule.
   *
   * @param {Object} row - Ligne affichee.
   * @param {string} column - Nom technique de la colonne.
   * @returns {unknown} Valeur brute resolue pour la cellule.
   */
  getCellValue(row, column) {
    if (this.props.getCellValue) {
      return this.props.getCellValue(row, column);
    }

    return row[column];
  }

  /**
   * Rend le contenu d'une cellule.
   *
   * @param {Object} row - Ligne affichee.
   * @param {string} column - Nom de la colonne affichee.
   * @returns {string|number|import("react").JSX.Element} Valeur formatee pour la cellule.
   */
  renderCellValue(row, column) {
    const value = this.getCellValue(row, column);
    if (this.props.formatCellValue) {
      return this.props.formatCellValue(column, value, row);
    }

    return TableColumnFormatService.formatGameValue(column, value, row);
  }

  /**
   * Indique si une colonne peut declencher un tri.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {boolean} `true` si la colonne est triable.
   */
  isSortableColumn(column) {
    const { sortableColumns } = this.props;
    return !sortableColumns || sortableColumns.includes(column);
  }

  /**
   * Retourne la cle React d'une ligne.
   *
   * @param {Object} row - Ligne affichee.
   * @param {number} index - Position de la ligne.
   * @returns {string|number} Cle de rendu.
   */
  getRowKey(row, index) {
    if (this.props.getRowKey) {
      return this.props.getRowKey(row, index);
    }

    return `${row.id || row["Nom du jeu"] || row.name || "row"}-${index}`;
  }

  /**
   * Indique si une cible d'evenement est deja interactive.
   *
   * @param {EventTarget|null} target - Cible native de l'evenement.
   * @param {EventTarget|null} rowTarget - Ligne courante qui porte l'action.
   * @returns {boolean} `true` si le clic doit rester gere par le controle cible.
   */
  isInteractiveEventTarget(target, rowTarget) {
    const interactiveTarget = target?.closest?.(
      "button, a, input, select, textarea, [role='button']"
    );
    return Boolean(interactiveTarget && interactiveTarget !== rowTarget);
  }

  /**
   * Declenche l'action optionnelle d'une ligne.
   *
   * @param {Object} row - Ligne activee par l'utilisateur.
   * @param {import("react").MouseEvent} event - Evenement de clic React.
   * @returns {void} Appelle le callback de ligne lorsque disponible.
   */
  handleRowClick(row, event) {
    if (
      !this.props.onRowClick ||
      this.isInteractiveEventTarget(event.target, event.currentTarget)
    ) {
      return;
    }

    this.props.onRowClick(row);
  }

  /**
   * Declenche l'action de ligne depuis le clavier.
   *
   * @param {Object} row - Ligne activee par l'utilisateur.
   * @param {import("react").KeyboardEvent} event - Evenement clavier React.
   * @returns {void} Appelle le callback de ligne pour Entree ou Espace.
   */
  handleRowKeyDown(row, event) {
    if (!this.props.onRowClick || (event.key !== "Enter" && event.key !== " ")) {
      return;
    }

    event.preventDefault();
    this.props.onRowClick(row);
  }

  /**
   * Rend les controles de pagination du tableau.
   *
   * @returns {import("react").JSX.Element|null} Controles de pagination ou absence.
   */
  renderPagination() {
    const { pagination } = this.props;
    if (!pagination) {
      return null;
    }

    const page = Number.isFinite(pagination.page) ? pagination.page : 0;
    const size = Number.isFinite(pagination.size) ? pagination.size : this.getRows().length;
    const totalPages = Math.max(1, pagination.totalPages || 1);
    const totalElements = pagination.totalElements;
    const sizeOptions = pagination.sizeOptions || [];
    const canGoPrevious = page > 0 && !pagination.isLoading;
    const canGoNext = page + 1 < totalPages && !pagination.isLoading;

    return (
      <div className="tablePagination" aria-label="Pagination du tableau">
        <div className="tablePaginationSummary">
          <span>
            Page {page + 1} / {totalPages}
          </span>
          {Number.isFinite(totalElements) ? <span>{totalElements} elements</span> : null}
        </div>
        <div className="tablePaginationControls">
          {sizeOptions.length > 0 && pagination.onSizeChange ? (
            <label>
              <span>Taille</span>
              <select
                value={size}
                disabled={pagination.isLoading}
                onChange={(event) => pagination.onSizeChange(Number(event.target.value))}
              >
                {sizeOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <button
            type="button"
            disabled={!canGoPrevious}
            onClick={() => pagination.onPageChange?.(page - 1)}
          >
            Precedent
          </button>
          <button
            type="button"
            disabled={!canGoNext}
            onClick={() => pagination.onPageChange?.(page + 1)}
          >
            Suivant
          </button>
        </div>
      </div>
    );
  }

  /**
   * Rend le tableau complet.
   *
   * @returns {import("react").JSX.Element} Tableau HTML.
   */
  render() {
    const {
      columns,
      sortConfig = {},
      onToggleSort,
      getRowClassName,
      renderRowActions,
      tableClassName,
      onRowClick,
    } = this.props;
    const rows = this.getRows();
    const hasFilters = Boolean(this.props.onColumnFiltersChange || this.props.renderColumnFilter);

    return (
      <>
        <div className="tableWrapper">
          <table className={tableClassName || undefined}>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th
                    key={column}
                    className={this.getColumnClassNames(column)}
                    data-column={this.getColumnDataName(column)}
                  >
                    {onToggleSort && this.isSortableColumn(column) ? (
                      <button
                        className="sortButton"
                        type="button"
                        onClick={() => onToggleSort(column)}
                        aria-label={`Trier ${column} en ${
                          sortConfig.column === column && sortConfig.direction === "asc"
                            ? "descendant"
                            : "ascendant"
                        }`}
                      >
                        <span>{this.getColumnLabel(column)}</span>
                        <SortIcon column={column} sortConfig={sortConfig} />
                      </button>
                    ) : (
                      <span>{this.getColumnLabel(column)}</span>
                    )}
                  </th>
                ))}
                {renderRowActions ? <th className="actionColumn">Action</th> : null}
              </tr>
              {hasFilters ? (
                <tr>
                  {columns.map((column) => (
                    <th
                      key={`${column}-filter`}
                      className={`filterCell ${this.getColumnClassNames(column)}`}
                      data-column={this.getColumnDataName(column)}
                    >
                      {this.renderColumnFilter(column)}
                    </th>
                  ))}
                  {renderRowActions ? <th className="filterCell actionColumn" /> : null}
                </tr>
              ) : null}
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr
                  className={[
                    getRowClassName ? getRowClassName(row) : "",
                    onRowClick ? "clickableTableRow" : "",
                  ].filter(Boolean).join(" ") || undefined}
                  key={this.getRowKey(row, index)}
                  onClick={onRowClick ? (event) => this.handleRowClick(row, event) : undefined}
                  onKeyDown={onRowClick ? (event) => this.handleRowKeyDown(row, event) : undefined}
                  role={onRowClick ? "button" : undefined}
                  tabIndex={onRowClick ? 0 : undefined}
                >
                  {columns.map((column) => (
                    <td
                      key={`${column}-${index}`}
                      className={this.getColumnClassNames(column)}
                      data-column={this.getColumnDataName(column)}
                    >
                      {this.renderCellValue(row, column)}
                    </td>
                  ))}
                  {renderRowActions ? (
                    <td className="actionColumn">{renderRowActions(row)}</td>
                  ) : null}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {this.renderPagination()}
      </>
    );
  }
}

export default TableComponent;
