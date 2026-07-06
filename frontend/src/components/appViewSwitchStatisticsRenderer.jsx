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
 * Description : rendu de la vue statistiques collection pour AppViewSwitch.
 */
import CollectionStatisticsView from "./CollectionStatisticsView";

/**
 * Rend la page de statistiques collection.
 *
 * @param {Object} props - Etat et callbacks statistiques.
 * @param {Object} layoutProps - Proprietes communes du layout.
 * @returns {import("react").JSX.Element} Vue statistiques.
 */
function renderStatisticsView(props, layoutProps) {
  return (
    <CollectionStatisticsView
      {...layoutProps}
      statisticsPage={props.collectionStatisticsPage}
    />
  );
}

export default renderStatisticsView;
