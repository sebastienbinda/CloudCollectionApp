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
 * Description : hook React de la liste publique des jeux Bibliotheque.
 */
import LibraryApi from "../../services/LibraryApi";
import useLibraryEntityList from "./useLibraryEntityList";

const GAME_CONFIGURATION = {
  rowsKey: "games",
  columns: ["name", "release_date", "developer", "editor", "platform", "status"],
  columnLabels: {
    name: "Nom",
    release_date: "Sortie",
    developer: "Developpeur",
    editor: "Editeur",
    platform: "Plateforme",
    status: "Statut",
  },
  mobileVisibleColumns: ["name", "release_date"],
  sortableColumns: ["name", "release_date", "developer", "platform"],
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les jeux Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchGames(criteria),
};

/**
 * Charge et pilote la table publique des jeux Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table jeux.
 */
function useLibraryGames(options = {}) {
  return useLibraryEntityList({
    ...GAME_CONFIGURATION,
    enabled: options.enabled,
  });
}

export default useLibraryGames;
