/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-04
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : composant tableau reutilisable pour afficher, filtrer et trier des jeux.
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
 * Tableau generique des jeux avec filtres par colonne.
 */
class GameTable extends Component {
  /**
   * Met a jour un filtre textuel ou select pour une colonne.
   *
   * @param {string} column - Nom de la colonne filtree.
   * @param {string} value - Nouvelle valeur du filtre.
   * @returns {void} Transmet la mise a jour au parent React.
   */
  updateSimpleFilter(column, value) {
    this.props.onColumnFiltersChange((previous) => ({
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
    this.props.onColumnFiltersChange((previous) => ({
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
    this.props.onColumnFiltersChange((previous) => ({
      ...previous,
      [column]: {
        operator: previous[column]?.operator || "=",
        year,
      },
    }));
  }

  /**
   * Rend le controle de filtre adapte au type de colonne.
   *
   * @param {string} column - Nom de la colonne a filtrer.
   * @returns {import("react").JSX.Element} Controle de filtre pour la colonne.
   */
  renderColumnFilter(column) {
    const { columnFilters, valuesByColumn } = this.props;

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
   * Indique si une colonne doit rester visible en rendu mobile.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {boolean} `true` si la colonne est explicitement visible en mobile.
   */
  isMobileVisibleColumn(column) {
    return (this.props.mobileVisibleColumns || []).includes(column);
  }

  /**
   * Retourne les classes CSS d'une colonne de tableau.
   *
   * @param {string} column - Nom technique de la colonne.
   * @returns {string} Classes CSS combinees.
   */
  getColumnClassNames(column) {
    const classes = [getColumnClassName(column)];
    if (this.isMobileVisibleColumn(column)) {
      classes.push("mobileVisibleColumn");
    }

    return classes.filter(Boolean).join(" ");
  }

  /**
   * Retourne la valeur brute a afficher pour une cellule.
   *
   * @param {Object} game - Ligne de jeu affichee.
   * @param {string} column - Nom technique de la colonne.
   * @returns {unknown} Valeur brute resolue pour la cellule.
   */
  getCellValue(game, column) {
    if (this.props.getCellValue) {
      return this.props.getCellValue(game, column);
    }

    return game[column];
  }

  /**
   * Rend le contenu d'une cellule de jeu.
   *
   * @param {Object} game - Ligne de jeu affichee.
   * @param {string} column - Nom de la colonne affichee.
   * @returns {string|number|import("react").JSX.Element} Valeur formatee pour la cellule.
   */
  renderCellValue(game, column) {
    const value = this.getCellValue(game, column);
    return TableColumnFormatService.formatGameValue(column, value);
  }

  /**
   * Rend le tableau complet des jeux.
   *
   * @param {void} Aucun - Utilise les props React du composant.
   * @returns {import("react").JSX.Element} Tableau HTML des jeux.
   */
  render() {
    const {
      columns,
      sortedGames,
      sortConfig,
      onToggleSort,
      getRowClassName,
      renderRowActions,
      tableClassName,
    } = this.props;

    return (
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
                </th>
              ))}
              {renderRowActions ? <th className="actionColumn">Action</th> : null}
            </tr>
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
          </thead>
          <tbody>
            {sortedGames.map((game, index) => (
              <tr
                className={getRowClassName ? getRowClassName(game) : undefined}
                key={`${game["Nom du jeu"] || "game"}-${index}`}
              >
                {columns.map((column) => (
                  <td
                    key={`${column}-${index}`}
                    className={this.getColumnClassNames(column)}
                    data-column={this.getColumnDataName(column)}
                  >
                    {this.renderCellValue(game, column)}
                  </td>
                ))}
                {renderRowActions ? (
                  <td className="actionColumn">{renderRowActions(game)}</td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
}

export default GameTable;
