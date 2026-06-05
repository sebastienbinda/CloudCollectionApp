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
  formatCellValue,
  getColumnClassName,
  getDateYearOptions,
  isDateColumn,
  isSelectFilterColumn,
} from "../collectionUtils";
import SortIcon from "./SortIcon";

/**
 * Tableau generique des jeux avec filtres par colonne.
 */
class GameTable extends Component {
  /**
   * Rend des pictogrammes de region/version pour une cellule `Version`.
   *
   * @param {unknown} value - Valeur brute de version, par exemple `PAL FR`.
   * @returns {string|import("react").JSX.Element} Tiret si vide, sinon span avec les pictogrammes.
   */
  renderVersionValue(value) {
    if (value === null || value === undefined || value === "") {
      return "-";
    }

    const versionText = String(value);
    const normalized = versionText.toLowerCase();
    const icons = [];

    if (normalized.includes("pal")) {
      icons.push("🌍");
    }
    if (normalized.includes("ntsc")) {
      icons.push("📺");
    }
    if (normalized.includes("jap")) {
      icons.push("🇯🇵");
    }
    if (normalized.includes("us")) {
      icons.push("🇺🇸");
    }
    if (normalized.includes("fr")) {
      icons.push("🇫🇷");
    }

    if (icons.length === 0) {
      return "-";
    }

    return <span className="versionIcons">{icons.join(" ")}</span>;
  }

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
   * Rend le contenu d'une cellule de jeu.
   *
   * @param {Object} game - Ligne de jeu affichee.
   * @param {string} column - Nom de la colonne affichee.
   * @returns {string|number|import("react").JSX.Element} Valeur formatee pour la cellule.
   */
  renderCellValue(game, column) {
    if (column === "Version") {
      return this.renderVersionValue(game[column]);
    }

    return formatCellValue(column, game[column]);
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
    } = this.props;

    return (
      <div className="tableWrapper">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column} className={getColumnClassName(column)}>
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
                    <span>{column}</span>
                    <SortIcon column={column} sortConfig={sortConfig} />
                  </button>
                </th>
              ))}
              {renderRowActions ? <th className="actionColumn">Action</th> : null}
            </tr>
            <tr>
              {columns.map((column) => (
                <th key={`${column}-filter`} className={`filterCell ${getColumnClassName(column)}`}>
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
                  <td key={`${column}-${index}`} className={getColumnClassName(column)}>
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
