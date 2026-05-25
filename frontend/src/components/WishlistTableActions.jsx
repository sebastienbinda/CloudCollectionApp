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
 * Description : actions de ligne du tableau wishlist.
 */

/**
 * Affiche les actions disponibles pour une ligne wishlist.
 *
 * @param {Object} props - Proprietes React des actions.
 * @param {Object} props.game - Jeu wishlist affiche.
 * @param {boolean} props.canAddGame - Autorise le transfert vers la collection.
 * @param {boolean} props.canEditWishlistGame - Autorise la modification wishlist.
 * @param {boolean} props.canDeleteWishlistGame - Autorise la suppression wishlist.
 * @param {Function} props.onEditWishlistGame - Callback de modification.
 * @param {Function} props.onOpenTransferDialog - Callback d'ouverture du transfert.
 * @param {Function} props.onDeleteWishlistGame - Callback de suppression.
 * @returns {import("react").JSX.Element} Groupe d'actions de ligne.
 */
function WishlistTableActions({
  game,
  canAddGame,
  canEditWishlistGame,
  canDeleteWishlistGame,
  onEditWishlistGame,
  onOpenTransferDialog,
  onDeleteWishlistGame,
}) {
  const gameName = game["Nom du jeu"] || "ce jeu";

  return (
    <div className="wishlistActionGroup">
      {canEditWishlistGame ? (
        <button
          className="wishlistIconButton"
          type="button"
          aria-label={`Modifier ${gameName} dans la wishlist`}
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
          aria-label={`Ajouter ${gameName} a la bibliotheque`}
          title="Ajouter a la bibliotheque"
          onClick={() => onOpenTransferDialog(game)}
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
          aria-label={`Supprimer ${gameName} de la wishlist`}
          title="Supprimer de la wishlist"
          onClick={() => onDeleteWishlistGame(game)}
        >
          <svg aria-hidden="true" className="wishlistActionIcon" viewBox="0 0 24 24">
            <path d="M9 3h6l1 2h4v2H4V5h4l1-2Z" />
            <path d="M6 9h12l-1 12H7L6 9Zm4 2v8h2v-8h-2Zm4 0v8h2v-8h-2Z" />
          </svg>
        </button>
      ) : null}
    </div>
  );
}

export default WishlistTableActions;
