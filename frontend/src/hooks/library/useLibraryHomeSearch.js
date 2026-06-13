/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-13
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de recherche publique des jeux Bibliotheque.
 */
import { useCallback, useEffect, useState } from "react";
import LibraryApi from "../../services/LibraryApi";

const LIBRARY_GAME_SEARCH_SIZE = 12;

/**
 * Gere la recherche de jeux globale depuis la page Bibliotheque.
 *
 * @param {Object} options - Options d'activation de la recherche.
 * @returns {Object} Etat et callbacks de recherche Bibliotheque.
 */
function useLibraryHomeSearch(options = {}) {
  const enabled = options.enabled !== false;
  const [librarySearchQuery, setLibrarySearchQuery] = useState("");
  const [librarySearchResults, setLibrarySearchResults] = useState([]);
  const [librarySearchError, setLibrarySearchError] = useState("");
  const [hasSearchedLibraryGames, setHasSearchedLibraryGames] = useState(false);
  const [isSearchingLibraryGames, setIsSearchingLibraryGames] = useState(false);

  const fetchSearchResults = useCallback(async (query) => {
    if (!enabled) {
      return;
    }

    try {
      setIsSearchingLibraryGames(true);
      setLibrarySearchError("");
      const data = await LibraryApi.fetchGames({
        name: query,
        page: 0,
        size: LIBRARY_GAME_SEARCH_SIZE,
        sort: [{ column: "name", direction: "asc" }],
      });
      setLibrarySearchResults(Array.isArray(data.games) ? data.games : []);
    } catch (caughtError) {
      setLibrarySearchError(caughtError.message || "Impossible de rechercher dans la Bibliotheque.");
      setLibrarySearchResults([]);
    } finally {
      setIsSearchingLibraryGames(false);
    }
  }, [enabled]);

  const closeLibrarySearch = useCallback(() => {
    setLibrarySearchResults([]);
    setLibrarySearchError("");
    setHasSearchedLibraryGames(false);
    setLibrarySearchQuery("");
  }, []);

  const searchLibraryGamesByName = useCallback(async (event) => {
    event.preventDefault();
    const query = librarySearchQuery.trim();
    setHasSearchedLibraryGames(true);

    if (!query) {
      setLibrarySearchResults([]);
      setLibrarySearchError("");
      return;
    }
    await fetchSearchResults(query);
  }, [fetchSearchResults, librarySearchQuery]);

  useEffect(() => {
    if (enabled) {
      return;
    }
    closeLibrarySearch();
  }, [closeLibrarySearch, enabled]);

  return {
    librarySearchQuery,
    setLibrarySearchQuery,
    librarySearchResults,
    librarySearchError,
    hasSearchedLibraryGames,
    isSearchingLibraryGames,
    closeLibrarySearch,
    searchLibraryGamesByName,
  };
}

export default useLibraryHomeSearch;
