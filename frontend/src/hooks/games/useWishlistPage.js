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
 * Description : hook React de consultation de la liste de souhaits.
 */
import { useEffect, useState } from "react";
import { filterGames } from "../../collectionUtils";
import AuthApi from "../../services/AuthApi";
import VideoGamesApi from "../../services/VideoGamesApi";

const wishlistColumns = ["Nom du jeu", "Plateforme", "Studio", "Date de sortie", "Version"];
const wishlistFilterColumns = ["Nom du jeu", "Plateforme"];
const platformValueColumns = ["Plateforme"];
const sortableColumns = ["Nom du jeu", "Plateforme", "Studio", "Date de sortie"];
const wishlistBuyStatusValues = Object.freeze(["all", "yes", "no"]);
const backendSortColumns = {
  "Nom du jeu": "name",
  Plateforme: "platform_name",
  Studio: "studio_name",
  "Date de sortie": "release_date",
};

/**
 * Construit les valeurs distinctes de filtres depuis les jeux charges.
 *
 * @param {Array<Object>} loadedGames - Jeux normalises pour le tableau.
 * @returns {Object} Valeurs distinctes par colonne.
 */
const buildValuesByColumn = (loadedGames) =>
  platformValueColumns.reduce((values, column) => {
    values[column] = Array.from(
      new Set(
        loadedGames
          .map((game) => game[column])
          .filter((value) => value !== null && value !== undefined && String(value).trim() !== "")
      )
    ).sort((firstValue, secondValue) =>
      String(firstValue).localeCompare(String(secondValue), "fr", {
        numeric: true,
        sensitivity: "base",
      })
    );
    return values;
  }, {});

/**
 * Construit le parametre de tri attendu par le backend.
 *
 * @param {Object} sortConfig - Tri courant du tableau.
 * @returns {string} Parametre `sort` backend.
 */
const buildBackendSort = (sortConfig) => {
  const backendColumn = backendSortColumns[sortConfig.column] || "name";
  const direction = sortConfig.direction === "desc" ? "desc" : "asc";
  return `${backendColumn},${direction}`;
};

const normalizeWishlistBuyStatus = (value, defaultValue = "all") => {
  const normalizedValue = String(value || "").trim().toLowerCase();
  if (wishlistBuyStatusValues.includes(normalizedValue)) {
    return normalizedValue;
  }
  const normalizedDefault = String(defaultValue || "").trim().toLowerCase();
  return wishlistBuyStatusValues.includes(normalizedDefault) ? normalizedDefault : "all";
};

const getWishlistBuyStatusFromUrl = (defaultValue) => {
  if (typeof window === "undefined") {
    return normalizeWishlistBuyStatus(defaultValue);
  }
  const urlValue = new URLSearchParams(window.location.search).get("wishlist_buy_status");
  return normalizeWishlistBuyStatus(urlValue, defaultValue);
};

const updateWishlistBuyStatusUrl = (value) => {
  if (typeof window === "undefined" || window.location.pathname !== "/wishlist") {
    return;
  }
  const url = new URL(window.location.href);
  url.searchParams.set("wishlist_buy_status", normalizeWishlistBuyStatus(value));
  window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
};

/**
 * Gere les jeux, filtres et tris backend de la page wishlist.
 *
 * @param {Object} options - Dependances de chargement wishlist.
 * @returns {Object} Etat de wishlist, donnees derivees et callbacks.
 */
function useWishlistPage(options) {
  const [games, setGames] = useState([]);
  const [valuesByColumn, setValuesByColumn] = useState({});
  const [columnFilters, setColumnFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ column: "Nom du jeu", direction: "asc" });
  const [wishlistBuyStatus, setWishlistBuyStatus] = useState(() =>
    getWishlistBuyStatusFromUrl(options.wishlistBuyStatusDefaultFilter)
  );
  const [wishlistError, setWishlistError] = useState("");
  const [isLoadingWishlistGames, setIsLoadingWishlistGames] = useState(false);

  useEffect(() => {
    const loadWishlistGames = async () => {
      if (!options.hasAccessToken || options.currentView !== "wishlist") {
        setGames([]);
        setValuesByColumn({});
        setColumnFilters({});
        setWishlistError("");
        setIsLoadingWishlistGames(false);
        return;
      }

      try {
        setIsLoadingWishlistGames(true);
        setWishlistError("");
        const loadedGames = await VideoGamesApi.fetchGames({
          wishlist: true,
          wishlist_buy_status: wishlistBuyStatus,
          sort: buildBackendSort(sortConfig),
        });
        setGames(Array.isArray(loadedGames) ? loadedGames : []);
        setValuesByColumn(buildValuesByColumn(Array.isArray(loadedGames) ? loadedGames : []));
      } catch (e) {
        if (AuthApi.isSessionExpiredError(e)) {
          return;
        }
        setWishlistError("Impossible de charger la liste de souhaits.");
        setGames([]);
        setValuesByColumn({});
      } finally {
        setIsLoadingWishlistGames(false);
      }
    };

    loadWishlistGames();
  }, [options.currentView, options.hasAccessToken, options.gamesReloadKey, sortConfig, wishlistBuyStatus]);

  useEffect(() => {
    if (options.currentView !== "wishlist") {
      return;
    }
    const selectedStatus = getWishlistBuyStatusFromUrl(options.wishlistBuyStatusDefaultFilter);
    setWishlistBuyStatus(selectedStatus);
    updateWishlistBuyStatusUrl(selectedStatus);
  }, [options.currentView, options.wishlistBuyStatusDefaultFilter]);

  const namedGames = games.filter((game) => String(game["Nom du jeu"] || "").trim() !== "");
  const filteredGames = filterGames(namedGames, wishlistFilterColumns, columnFilters);
  const gameResultNavigationContext = {
    detailSource: "collection",
    rows: filteredGames,
    page: 0,
    size: filteredGames.length,
    totalElements: filteredGames.length,
  };
  const toggleSort = (column) => {
    if (!sortableColumns.includes(column)) {
      return;
    }
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };
  const updateWishlistBuyStatus = (value) => {
    const normalizedValue = normalizeWishlistBuyStatus(value);
    setWishlistBuyStatus(normalizedValue);
    updateWishlistBuyStatusUrl(normalizedValue);
  };

  return {
    wishlistGames: namedGames,
    wishlistColumns,
    wishlistValuesByColumn: valuesByColumn,
    wishlistColumnFilters: columnFilters,
    setWishlistColumnFilters: setColumnFilters,
    wishlistBuyStatus,
    setWishlistBuyStatus: updateWishlistBuyStatus,
    wishlistSortConfig: sortConfig,
    wishlistSortedGames: filteredGames,
    wishlistFilteredGames: filteredGames,
    gameResultNavigationContext,
    isLoadingWishlistGames,
    wishlistError,
    wishlistSortableColumns: sortableColumns,
    toggleWishlistSort: toggleSort,
  };
}

export {
  normalizeWishlistBuyStatus,
};
export default useWishlistPage;
