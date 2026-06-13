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
 * Description : hook React de la liste publique des studios Bibliotheque.
 */
import LibraryApi from "../../services/LibraryApi";
import useLibraryEntityList from "./useLibraryEntityList";

const STUDIO_CONFIGURATION = {
  rowsKey: "studios",
  columns: [
    "name",
    "country",
    "city",
    "creation_date",
    "status",
    "editor_total_games",
    "developer_total_games",
  ],
  columnLabels: {
    name: "Nom",
    country: "Pays",
    city: "Ville",
    creation_date: "Creation",
    status: "Statut",
    editor_total_games: "Editeur",
    developer_total_games: "Developpeur",
  },
  mobileVisibleColumns: ["name", "country"],
  sortableColumns: ["name", "country", "creation_date"],
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les studios Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchStudios(criteria),
};

/**
 * Charge et pilote la table publique des studios Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table studios.
 */
function useLibraryStudios(options = {}) {
  return useLibraryEntityList({
    ...STUDIO_CONFIGURATION,
    autoSearchEnabled: true,
    enabled: options.enabled,
  });
}

export default useLibraryStudios;
