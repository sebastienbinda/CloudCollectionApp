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
  const [appliedLibrarySearchQuery, setAppliedLibrarySearchQuery] = useState("");
  const [librarySearchResults, setLibrarySearchResults] = useState([]);
  const [librarySearchError, setLibrarySearchError] = useState("");
  const [pageMetadata, setPageMetadata] = useState({
    page: 0,
    size: LIBRARY_GAME_SEARCH_SIZE,
    totalElements: 0,
  });
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
      setAppliedLibrarySearchQuery(query);
      setPageMetadata({
        page: data.page?.page ?? 0,
        size: data.page?.size ?? LIBRARY_GAME_SEARCH_SIZE,
        totalElements: data.page?.totalElements ?? data.games?.length ?? 0,
      });
    } catch (caughtError) {
      setLibrarySearchError(caughtError.message || "Impossible de rechercher dans la Bibliotheque.");
      setLibrarySearchResults([]);
      setAppliedLibrarySearchQuery("");
      setPageMetadata({ page: 0, size: LIBRARY_GAME_SEARCH_SIZE, totalElements: 0 });
    } finally {
      setIsSearchingLibraryGames(false);
    }
  }, [enabled]);

  const closeLibrarySearch = useCallback(() => {
    setLibrarySearchResults([]);
    setAppliedLibrarySearchQuery("");
    setLibrarySearchError("");
    setPageMetadata({ page: 0, size: LIBRARY_GAME_SEARCH_SIZE, totalElements: 0 });
    setHasSearchedLibraryGames(false);
    setLibrarySearchQuery("");
  }, []);

  const searchLibraryGamesByName = useCallback(async (event) => {
    event.preventDefault();
    const query = librarySearchQuery.trim();
    setHasSearchedLibraryGames(true);

    if (!query) {
      setLibrarySearchResults([]);
      setAppliedLibrarySearchQuery("");
      setLibrarySearchError("");
      setPageMetadata({ page: 0, size: LIBRARY_GAME_SEARCH_SIZE, totalElements: 0 });
      return;
    }
    await fetchSearchResults(query);
  }, [fetchSearchResults, librarySearchQuery]);

  const fetchGameResultPage = useCallback(
    async (page) => {
      const data = await LibraryApi.fetchGames({
        name: appliedLibrarySearchQuery,
        page,
        size: LIBRARY_GAME_SEARCH_SIZE,
        sort: [{ column: "name", direction: "asc" }],
      });
      return {
        detailSource: "library",
        rows: Array.isArray(data.games) ? data.games : [],
        page: data.page?.page ?? page,
        size: data.page?.size ?? LIBRARY_GAME_SEARCH_SIZE,
        totalElements: data.page?.totalElements ?? 0,
      };
    },
    [appliedLibrarySearchQuery]
  );

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
    gameResultNavigationContext: {
      detailSource: "library",
      rows: librarySearchResults,
      page: pageMetadata.page,
      size: pageMetadata.size,
      totalElements: pageMetadata.totalElements,
      fetchPage: fetchGameResultPage,
    },
    hasSearchedLibraryGames,
    isSearchingLibraryGames,
    closeLibrarySearch,
    searchLibraryGamesByName,
  };
}

export default useLibraryHomeSearch;
