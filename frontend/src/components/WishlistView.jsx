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
 * Description : vue React autonome pour la liste de souhaits.
 */
import { Component } from "react";
import { formatCellValue, formatNumber } from "../collectionUtils";
import WishlistTransferService from "../services/WishlistTransferService";
import EditWishlistDialog from "./EditWishlistDialog";
import GameTable from "./GameTable";
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";
/**
 * Vue dediee a l'onglet ODS `Liste de souhaits`.
 */
class WishlistView extends Component {
  transferService = new WishlistTransferService();
  state = {
    transferError: "",
    transferForm: {
      "Date d'achat": "",
      "Lieu d'achat": "",
    },
    transferMessage: "",
    transferPlatform: "",
    transferSelectedGame: null,
    purchaseStatusFilter: "all",
    isTransferringGame: false,
  };
  /**
   * Filtre les jeux selon leur statut d'achat wishlist.
   *
   * @param {Record<string, unknown>[]} games - Jeux deja filtres par colonnes.
   * @returns {Record<string, unknown>[]} Jeux correspondant au filtre de statut.
   */
  filterGamesByPurchaseStatus(games) {
    const { purchaseStatusFilter } = this.state;
    if (purchaseStatusFilter === "pending") {
      return games.filter((game) => this.transferService.hasPurchaseDate(game));
    }
    if (purchaseStatusFilter === "wishlist") {
      return games.filter((game) => !this.transferService.hasPurchaseDate(game));
    }
    return games;
  }
  /**
   * Retire les lignes wishlist sans nom de jeu.
   *
   * @param {Record<string, unknown>[]} games - Jeux bruts ou filtres.
   * @returns {Record<string, unknown>[]} Jeux ayant un nom visible.
   */
  filterNamedGames(games) {
    return games.filter((game) => this.transferService.hasTextValue(game["Nom du jeu"]));
  }
  /**
   * Met a jour le filtre de statut d'achat de la wishlist.
   *
   * @param {string} value - Valeur selectionnee dans le filtre.
   * @returns {void} Met a jour l'etat local du composant.
   */
  updatePurchaseStatusFilter(value) {
    this.setState({ purchaseStatusFilter: value });
  }
  /**
   * Ouvre la confirmation d'ajout vers la plateforme cible.
   *
   * @param {Record<string, unknown>} game - Jeu wishlist a ajouter dans une plateforme.
   * @returns {void} Prepare la modale de confirmation.
   */
  openTransferDialog(game) {
    const transferPlatform = this.transferService.findTargetPlatform(game, this.props.platforms);
    this.setState({
      transferError: transferPlatform
        ? ""
        : "Aucune plateforme existante ne correspond a la console de ce jeu.",
      transferForm: {
        "Date d'achat": this.transferService.formatDateInputValue(game["Date d'achat"]),
        "Lieu d'achat": String(game["Lieu d'achat"] || ""),
      },
      transferMessage: "",
      transferPlatform,
      transferSelectedGame: game,
    });
  }
  /**
   * Ferme la modale de transfert wishlist.
   *
   * @param {void} Aucun - Reinitialise l'etat de transfert local.
   * @returns {void} Masque la modale.
   */
  closeTransferDialog() {
    this.setState({
      transferError: "",
      transferForm: {
        "Date d'achat": "",
        "Lieu d'achat": "",
      },
      transferPlatform: "",
      transferSelectedGame: null,
      isTransferringGame: false,
    });
  }
  /**
   * Met a jour un champ de la confirmation de transfert.
   *
   * @param {string} field - Nom du champ modifie.
   * @param {string} value - Nouvelle valeur saisie.
   * @returns {void} Met a jour le formulaire local.
   */
  updateTransferFormField(field, value) {
    this.setState((previous) => ({
      transferForm: {
        ...previous.transferForm,
        [field]: value,
      },
    }));
  }
  /**
   * Valide puis ajoute le jeu wishlist dans sa plateforme.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de validation de la modale.
   * @returns {Promise<void>} Ajoute le jeu et affiche le resultat.
   */
  async submitTransferDialog(event) {
    event.preventDefault();
    const { transferSelectedGame, transferPlatform, transferForm } = this.state;
    if (!transferSelectedGame || !transferPlatform) {
      this.setState({ transferError: "La plateforme cible est introuvable." });
      return;
    }
    if (
      !this.transferService.hasTextValue(transferForm["Date d'achat"]) ||
      !this.transferService.hasTextValue(transferForm["Lieu d'achat"])
    ) {
      this.setState({ transferError: "La date d'achat et le lieu d'achat sont obligatoires." });
      return;
    }
    try {
      this.setState({ isTransferringGame: true, transferError: "" });
      await this.props.onAddWishlistGameToPlatform(
        this.transferService.buildTransferPayload(
          transferSelectedGame,
          transferPlatform,
          transferForm
        )
      );
      this.setState({
        transferMessage: `${transferSelectedGame["Nom du jeu"]} a ete ajoute a ${transferPlatform}.`,
      });
      this.closeTransferDialog();
    } catch (error) {
      this.setState({
        transferError: error.message || "Impossible d'ajouter ce jeu a la plateforme.",
        isTransferringGame: false,
      });
    }
  }
  /**
   * Confirme puis supprime un jeu de la wishlist.
   *
   * @param {Record<string, unknown>} game - Jeu wishlist a supprimer.
   * @returns {Promise<void>} Supprime le jeu et affiche le resultat.
   */
  async deleteWishlistGame(game) {
    const gameName = game["Nom du jeu"] || "ce jeu";
    const confirmed = window.confirm(
      `Confirmer la suppression de "${gameName}" de la wishlist ?`
    );
    if (!confirmed) {
      return;
    }
    try {
      await this.props.onDeleteWishlistGame(game);
      this.setState({
        transferError: "",
        transferMessage: `${gameName} a ete supprime de la liste de souhaits.`,
      });
    } catch (error) {
      this.setState({
        transferError: error.message || "Impossible de supprimer ce jeu de la liste de souhaits.",
      });
    }
  }
  /**
   * Enregistre la modification d'un jeu wishlist.
   *
   * @param {Record<string, unknown>} originalGame - Jeu original.
   * @param {Record<string, unknown>} updatedGame - Jeu modifie.
   * @returns {Promise<void>} Modifie le jeu et affiche le resultat.
   */
  async saveWishlistGame(originalGame, updatedGame) {
    try {
      await this.props.onSaveWishlistGame(originalGame, updatedGame);
      this.setState({
        transferError: "",
        transferMessage: `${updatedGame["Nom du jeu"]} a ete modifie dans la liste de souhaits.`,
      });
    } catch (error) {
      this.setState({
        transferError: error.message || "Impossible de modifier ce jeu de la liste de souhaits.",
      });
    }
  }
  /**
   * Retourne la classe visuelle d'une ligne wishlist.
   *
   * @param {Record<string, unknown>} game - Jeu affiche dans le tableau.
   * @returns {string} Classe CSS de statut de ligne.
   */
  getWishlistRowClassName(game) {
    return this.transferService.hasPurchaseDate(game)
      ? "wishlistPurchasePendingRow"
      : "wishlistRegularRow";
  }
  /**
   * Retourne le message a afficher quand aucun jeu ne passe les filtres.
   *
   * @param {void} Aucun - Utilise le filtre de statut courant.
   * @returns {string} Message adapte au filtre actif.
   */
  getEmptyFilterMessage() {
    if (this.state.purchaseStatusFilter === "pending") {
      return "Aucun jeu deja precommande ne correspond aux filtres.";
    }
    if (this.state.purchaseStatusFilter === "wishlist") {
      return "Aucun jeu souhaite ne correspond aux filtres.";
    }
    return "Aucun jeu ne correspond aux filtres de colonnes.";
  }
  /**
   * Rend le contenu principal de la liste de souhaits.
   *
   * @param {void} Aucun - Utilise les props React du composant.
   * @returns {import("react").JSX.Element} Vue complete de la wishlist.
   */
  render() {
    const {
      games,
      columns,
      valuesByColumn,
      columnFilters,
      sortConfig,
      sortedGames,
      filteredGames,
      error,
      isLoadingGames,
      canAddGame,
      canEditWishlistGame,
      canDeleteWishlistGame,
      editingWishlistGame,
      isSavingWishlistGame,
      onBack,
      onEditWishlistGame,
      onCancelEditWishlistGame,
      onToggleSort,
      onColumnFiltersChange,
    } = this.props;
    const { transferSelectedGame, transferPlatform } = this.state;
    const namedGames = this.filterNamedGames(games);
    const namedSortedGames = this.filterNamedGames(sortedGames);
    const namedFilteredGames = this.filterNamedGames(filteredGames);
    const purchasePendingCount = namedGames.filter((game) =>
      this.transferService.hasPurchaseDate(game)
    ).length;
    const wishlistOnlyCount = namedGames.length - purchasePendingCount;
    const filteredSortedGames = this.filterGamesByPurchaseStatus(namedSortedGames);
    const filteredVisibleGames = this.filterGamesByPurchaseStatus(namedFilteredGames);
    const nextRelease = this.transferService.getNextWishlistRelease(namedGames);
    return (
      <main className="container">
        <button className="backButton" type="button" onClick={onBack}>
          Accueil
        </button>
        <section className="platformDetailHero wishlistHero">
          <div className="platformDetailContent">
            <p className="eyebrow">Souhaits</p>
            <h1>
              <span className="pageTitleWithIcon">
                <ProjectIcon />
                <span>Liste de souhaits</span>
              </span>
            </h1>
            <p className="subtitle">Jeux reperes avant ajout a la collection.</p>
          </div>
        </section>
        <section className="statsGrid wishlistStatsGrid" aria-label="Statistiques de la liste de souhaits">
          <article className="statCard">
            <span>Jeux</span>
            <strong>{formatNumber(namedGames.length)}</strong>
          </article>
          <article className="statCard">
            <span>Jeux deja precommandes</span>
            <strong>{formatNumber(purchasePendingCount)}</strong>
          </article>
          <article className="statCard">
            <span>Jeux souhaites</span>
            <strong>{formatNumber(wishlistOnlyCount)}</strong>
          </article>
          <article className="statCard wishlistNextReleaseCard">
            <span>Prochaine sortie</span>
            <strong className="wishlistNextReleaseName">
              {nextRelease ? nextRelease.game["Nom du jeu"] : "-"}
            </strong>
            {nextRelease ? (
              <>
                <small>
                  {formatCellValue(
                    "Console",
                    nextRelease.game.Console || nextRelease.game.Plateforme
                  )}
                </small>
                <small>{formatCellValue("Date", nextRelease.game["Date de sortie"])}</small>
                <span className="wishlistReleaseCountdown">
                  J-
                  {formatNumber(this.transferService.getDaysUntilRelease(nextRelease.releaseDate))}
                </span>
              </>
            ) : null}
          </article>
        </section>
        {error ? <p className="error">{error}</p> : null}
        {this.state.transferMessage ? <p className="success">{this.state.transferMessage}</p> : null}
        {isLoadingGames ? <ProgressBar label="Chargement des jeux" /> : null}
        {!isLoadingGames && namedGames.length === 0 ? (
          <p>Aucun jeu dans la liste de souhaits.</p>
        ) : null}
        {!isLoadingGames && namedGames.length > 0 ? (
          <>
            <section className="wishlistPurchaseFilter" aria-label="Filtre achat wishlist">
              <label htmlFor="wishlist-purchase-filter">Statut d'achat</label>
              <select
                id="wishlist-purchase-filter"
                value={this.state.purchaseStatusFilter}
                onChange={(event) => this.updatePurchaseStatusFilter(event.target.value)}
              >
                <option value="all">Tous les souhaits</option>
                <option value="pending">Jeux deja precommandes</option>
                <option value="wishlist">Jeux souhaites</option>
              </select>
              <span>{formatNumber(filteredVisibleGames.length)} jeux affiches</span>
            </section>
            <GameTable
              games={namedGames}
              columns={columns}
              valuesByColumn={valuesByColumn}
              columnFilters={columnFilters}
              sortConfig={sortConfig}
              sortedGames={filteredSortedGames}
              onToggleSort={onToggleSort}
              onColumnFiltersChange={onColumnFiltersChange}
              getRowClassName={(game) => this.getWishlistRowClassName(game)}
              renderRowActions={
                canAddGame || canEditWishlistGame || canDeleteWishlistGame
                  ? (game) => (
                      <div className="wishlistActionGroup">
                        {canEditWishlistGame ? (
                          <button
                            className="wishlistIconButton"
                            type="button"
                            aria-label={`Modifier ${game["Nom du jeu"] || "ce jeu"} dans la wishlist`}
                            title="Modifier dans la wishlist"
                            onClick={() => onEditWishlistGame(game)}
                          >
                            <svg aria-hidden="true" className="wishlistActionIcon" viewBox="0 0 24 24">
                              <path d="M4 17.5V21h3.5L18.1 10.4l-3.5-3.5L4 17.5Z" />
                              <path d="m16 5.5 1.6-1.6a1.2 1.2 0 0 1 1.7 0l.8.8a1.2 1.2 0 0 1 0 1.7L18.5 8 16 5.5Z" />
                            </svg>
                          </button>
                        ) : null}
                        {canAddGame ? (
                          <button
                            className="wishlistIconButton"
                            type="button"
                            aria-label={`Ajouter ${game["Nom du jeu"] || "ce jeu"} a la bibliotheque`}
                            title="Ajouter a la bibliotheque"
                            onClick={() => this.openTransferDialog(game)}
                          >
                            <svg aria-hidden="true" className="wishlistActionIcon" viewBox="0 0 24 24">
                              <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H9v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z" />
                              <path d="M10 3h4v16h-4V3Z" />
                              <path d="M15 3h2.5A2.5 2.5 0 0 1 20 5.5v16a2.5 2.5 0 0 0-2.5-2.5H15V3Z" />
                              <path d="M6 7h1.5v2H6V7Zm10.5 0H18v2h-1.5V7Z" />
                            </svg>
                          </button>
                        ) : null}
                        {canDeleteWishlistGame ? (
                          <button
                            className="wishlistIconButton dangerIconButton"
                            type="button"
                            aria-label={`Supprimer ${game["Nom du jeu"] || "ce jeu"} de la wishlist`}
                            title="Supprimer de la wishlist"
                            onClick={() => this.deleteWishlistGame(game)}
                          >
                            <svg aria-hidden="true" className="wishlistActionIcon" viewBox="0 0 24 24">
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
          </>
        ) : null}
        {!isLoadingGames && namedGames.length > 0 && filteredVisibleGames.length === 0 ? (
          <p>{this.getEmptyFilterMessage()}</p>
        ) : null}
        {transferSelectedGame ? (
          <div className="modalOverlay" role="presentation">
            <form
              className="wishlistTransferDialog"
              onSubmit={(event) => this.submitTransferDialog(event)}
              role="dialog"
              aria-modal="true"
              aria-labelledby="wishlist-transfer-title"
            >
              <h2 id="wishlist-transfer-title">Ajouter a la plateforme</h2>
              <p>
                {transferPlatform
                  ? `${transferSelectedGame["Nom du jeu"]} sera ajoute a la plateforme existante ${transferPlatform}.`
                  : "Aucune plateforme existante ne correspond a la console de ce jeu."}
              </p>
              {this.state.transferError ? (
                <p className="error">{this.state.transferError}</p>
              ) : null}
              <label>
                Date d'achat
                <input
                  type="date"
                  value={this.state.transferForm["Date d'achat"]}
                  onChange={(event) =>
                    this.updateTransferFormField("Date d'achat", event.target.value)
                  }
                  required
                />
              </label>
              <label>
                Lieu d'achat
                <input
                  type="text"
                  value={this.state.transferForm["Lieu d'achat"]}
                  onChange={(event) =>
                    this.updateTransferFormField("Lieu d'achat", event.target.value)
                  }
                  required
                />
              </label>
              <div className="formActions">
                <button
                  className="secondaryButton"
                  type="button"
                  onClick={() => this.closeTransferDialog()}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={!transferPlatform || this.state.isTransferringGame}
                >
                  Confirmer l'ajout
                </button>
              </div>
              {this.state.isTransferringGame ? <ProgressBar label="Ajout du jeu en cours" /> : null}
            </form>
          </div>
        ) : null}
        <EditWishlistDialog
          game={editingWishlistGame}
          isSaving={isSavingWishlistGame}
          onSubmit={(originalGame, updatedGame) =>
            this.saveWishlistGame(originalGame, updatedGame)
          }
          onCancel={onCancelEditWishlistGame}
        />
      </main>
    );
  }
}
export default WishlistView;
