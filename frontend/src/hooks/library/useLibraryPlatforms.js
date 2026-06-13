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
 * Description : hook React de la liste publique des plateformes Bibliotheque.
 */
import LibraryApi from "../../services/LibraryApi";
import useLibraryEntityList from "./useLibraryEntityList";

const PLATFORM_CONFIGURATION = {
  rowsKey: "platforms",
  columns: ["name", "release_date", "manufacturer", "status", "total_games"],
  columnLabels: {
    name: "Nom",
    release_date: "Sortie",
    manufacturer: "Constructeur",
    status: "Statut",
    total_games: "Jeux",
  },
  mobileVisibleColumns: ["name", "total_games"],
  sortableColumns: ["name", "release_date", "manufacturer"],
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les plateformes Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchPlatforms(criteria),
};

/**
 * Charge et pilote la table publique des plateformes Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table plateformes.
 */
function useLibraryPlatforms(options = {}) {
  return useLibraryEntityList({
    ...PLATFORM_CONFIGURATION,
    autoSearchEnabled: true,
    enabled: options.enabled,
  });
}

export default useLibraryPlatforms;
