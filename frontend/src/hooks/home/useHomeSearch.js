/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de recherche globale depuis l'accueil.
 */
import { useEffect, useState } from "react";
import JeuxVideoApi from "../../services/JeuxVideoApi";

/**
 * Gere la recherche de jeux par nom depuis la page d'accueil.
 *
 * @param {boolean} isAuthenticated - Indique si les actions backend sont disponibles.
 * @returns {Object} Etat et callbacks de recherche.
 */
function useHomeSearch(isAuthenticated) {
  const [homeSearchQuery, setHomeSearchQuery] = useState("");
  const [homeSearchResults, setHomeSearchResults] = useState([]);
  const [homeSearchError, setHomeSearchError] = useState("");
  const [hasSearchedGames, setHasSearchedGames] = useState(false);
  const [isSearchingGames, setIsSearchingGames] = useState(false);

  const fetchSearchResults = async (query) => {
    try {
      setIsSearchingGames(true);
      setHomeSearchError("");
      const data = await JeuxVideoApi.searchGamesByName(query);
      setHomeSearchResults(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setHomeSearchError("Impossible de rechercher dans la collection.");
      setHomeSearchResults([]);
    } finally {
      setIsSearchingGames(false);
    }
  };

  const closeHomeSearch = () => {
    setHomeSearchResults([]);
    setHomeSearchError("");
    setHasSearchedGames(false);
    setHomeSearchQuery("");
  };

  const searchGamesByName = async (event) => {
    event.preventDefault();
    const query = homeSearchQuery.trim();
    setHasSearchedGames(true);

    if (!query) {
      setHomeSearchResults([]);
      setHomeSearchError("");
      return;
    }
    await fetchSearchResults(query);
  };

  useEffect(() => {
    const query = homeSearchQuery.trim();
    if (!hasSearchedGames || !query) {
      return;
    }
    fetchSearchResults(query);
  }, [isAuthenticated]);

  return {
    homeSearchQuery,
    setHomeSearchQuery,
    homeSearchResults,
    homeSearchError,
    hasSearchedGames,
    isSearchingGames,
    closeHomeSearch,
    searchGamesByName,
  };
}

export default useHomeSearch;
