/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : rendu de la vue accueil collection pour AppViewSwitch.
 */
import HomeView from "./HomeView";

/**
 * Rend la page d'accueil de collection.
 *
 * @param {Object} props - Etat et callbacks d'accueil.
 * @param {Object} layoutProps - Proprietes communes du layout.
 * @returns {import("react").JSX.Element} Vue d'accueil.
 */
function renderHomeView(props, layoutProps) {
  return (
    <HomeView
      {...layoutProps}
      homeStats={props.homeStats}
      error={props.error}
      isLoadingHome={props.isLoadingHome}
      isSearchingGames={props.isSearchingGames}
      hasSearchedGames={props.hasSearchedGames}
      homeSearchQuery={props.homeSearchQuery}
      homeSearchResults={props.homeSearchResults}
      homeSearchError={props.homeSearchError}
      onOpenPlatform={props.openPlatform}
      onSearchQueryChange={props.setHomeSearchQuery}
      onSearchSubmit={props.searchGamesByName}
      onCloseSearch={props.closeHomeSearch}
      onOpenGameDetail={(game) => props.openGameDetail(
        game,
        "collection",
        props.homeGameResultNavigationContext
      )}
    />
  );
}

export default renderHomeView;
