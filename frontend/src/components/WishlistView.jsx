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
 * Description : page React de consultation de la liste de souhaits.
 */
import CollectionGamesTable from "./CollectionGamesTable";
import PageLayout from "./PageLayout";

/**
 * Affiche la page routee de liste de souhaits.
 *
 * @param {Object} props - Informations de session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue liste de souhaits.
 */
function WishlistView({
  isAuthenticated,
  canUseCollectionViews,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  wishlistPage,
}) {
  return (
    <PageLayout
      shellClassName="container"
      eyebrow="Collection"
      title="Liste de souhaits"
      subtitle="Jeux souhaites"
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {wishlistPage?.wishlistError ? <p className="error">{wishlistPage.wishlistError}</p> : null}

      <CollectionGamesTable
        games={wishlistPage?.wishlistGames || []}
        columns={wishlistPage?.wishlistColumns || []}
        valuesByColumn={wishlistPage?.wishlistValuesByColumn || {}}
        columnFilters={wishlistPage?.wishlistColumnFilters || {}}
        sortConfig={wishlistPage?.wishlistSortConfig || { column: "Nom du jeu", direction: "asc" }}
        sortedGames={wishlistPage?.wishlistSortedGames || []}
        filteredGames={wishlistPage?.wishlistFilteredGames || []}
        isLoadingGames={Boolean(wishlistPage?.isLoadingWishlistGames)}
        emptyMessage="Aucun jeu dans la liste de souhaits."
        filterableColumns={wishlistPage?.wishlistFilterableColumns || []}
        sortableColumns={wishlistPage?.wishlistSortableColumns || []}
        onToggleSort={wishlistPage?.toggleWishlistSort}
        onColumnFiltersChange={wishlistPage?.setWishlistColumnFilters}
      />
    </PageLayout>
  );
}

export default WishlistView;
