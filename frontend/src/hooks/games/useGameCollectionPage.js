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
 * Description : hook React de la page collection de jeux par plateforme.
 */
import { useEffect, useState } from "react";
import { filterGames, getStudioCount, sortGames } from "../../collectionUtils";
import VideoGamesApi from "../../services/VideoGamesApi";
import usePlatformGameMutations from "../usePlatformGameMutations";

/**
 * Gere les jeux, filtres, tris et mutations de la collection par plateforme.
 *
 * @param {Object} options - Dependances de chargement et mutations de collection.
 * @returns {Object} Etat de collection, donnees derivees et callbacks.
 */
function useGameCollectionPage(options) {
  const [games, setGames] = useState([]);
  const [valuesByColumn, setValuesByColumn] = useState({});
  const [columnFilters, setColumnFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ column: "Nom du jeu", direction: "asc" });
  const [isLoadingGames, setIsLoadingGames] = useState(false);
  const mutations = usePlatformGameMutations(
    options.selectedPlatform,
    options.reloadOds,
    options.reloadGames
  );

  useEffect(() => {
    const fetchGames = async () => {
      if (!options.hasAccessToken || !options.selectedPlatform) {
        setGames([]);
        setIsLoadingGames(false);
        return;
      }

      try {
        setIsLoadingGames(true);
        options.setError("");
        const data = await VideoGamesApi.fetchGames(options.selectedPlatform);
        setGames(Array.isArray(data) ? data : []);
        setColumnFilters({});
      } catch (e) {
        options.setError("Impossible de charger les jeux video pour cette plateforme.");
        setGames([]);
      } finally {
        setIsLoadingGames(false);
      }
    };

    fetchGames();
  }, [options.selectedPlatform, options.gamesReloadKey, options.isAuthenticated, options.hasAccessToken]);

  useEffect(() => {
    const fetchColumnValues = async () => {
      if (!options.hasAccessToken || !options.selectedPlatform) {
        setValuesByColumn({});
        return;
      }

      try {
        const data = await VideoGamesApi.fetchColumnValues(options.selectedPlatform);
        setValuesByColumn(data.values_by_column || {});
      } catch (e) {
        setValuesByColumn({});
      }
    };

    fetchColumnValues();
  }, [options.selectedPlatform, options.gamesReloadKey, options.isAuthenticated, options.hasAccessToken]);

  const namedGames = games.filter((game) => String(game["Nom du jeu"] || "").trim() !== "");
  const columns = namedGames.length > 0
    ? ["Nom du jeu", ...Object.keys(namedGames[0]).filter((column) => column !== "Nom du jeu")]
    : [];
  const filteredGames = filterGames(namedGames, columns, columnFilters);
  const sortedGames = sortGames(filteredGames, sortConfig);
  const toggleSort = (column) => {
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };

  return {
    namedGames,
    columns,
    valuesByColumn,
    columnFilters,
    setColumnFilters,
    sortConfig,
    sortedGames,
    filteredGames,
    isLoadingGames,
    studioCount: getStudioCount(namedGames),
    toggleSort,
    ...mutations,
  };
}

export default useGameCollectionPage;
