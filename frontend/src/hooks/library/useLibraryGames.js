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
import { createElement, useCallback, useEffect, useMemo, useState } from "react";
import LibraryApi from "../../services/LibraryApi";
import TableColumnFormatService from "../../services/TableColumnFormatService.jsx";
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
  tableClassName: "libraryGamesTable",
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les jeux Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchGames(criteria),
  formatCellValue: formatLibraryGameCellValue,
};
const PLATFORM_PAGE_SIZE = 500;

/**
 * Charge et pilote la table publique des jeux Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table jeux.
 */
function useLibraryGames(options = {}) {
  const enabled = options.enabled !== false;
  const canFilterDuplicateFlag = options.authenticatedProfile === "ADMIN";
  const [platformOptions, setPlatformOptions] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [selectedDuplicateFlag, setSelectedDuplicateFlag] = useState("");
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(false);
  const [platformError, setPlatformError] = useState("");
  const extraCriteria = useMemo(
    () => ({
      duplicate_flag: canFilterDuplicateFlag ? selectedDuplicateFlag : "",
      platform: selectedPlatform,
    }),
    [canFilterDuplicateFlag, selectedDuplicateFlag, selectedPlatform]
  );

  useEffect(() => {
    if (!enabled) {
      setPlatformOptions([]);
      return;
    }

    let isMounted = true;
    const loadPlatforms = async () => {
      try {
        setIsLoadingPlatforms(true);
        setPlatformError("");
        const data = await LibraryApi.fetchPlatforms({
          page: 0,
          size: PLATFORM_PAGE_SIZE,
          sort: [{ column: "name", direction: "asc" }],
        });
        if (isMounted) {
          setPlatformOptions(filterPlatformsWithGames(data.platforms));
        }
      } catch (caughtError) {
        if (isMounted) {
          setPlatformOptions([]);
          setPlatformError(caughtError.message || "Impossible de charger les plateformes.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingPlatforms(false);
        }
      }
    };

    loadPlatforms();
    return () => {
      isMounted = false;
    };
  }, [enabled]);

  const handlePlatformChange = useCallback((platformName) => {
    setSelectedPlatform(platformName);
  }, []);

  const handleDuplicateFlagChange = useCallback((duplicateFlag) => {
    setSelectedDuplicateFlag(duplicateFlag);
  }, []);

  useEffect(() => {
    if (!canFilterDuplicateFlag && selectedDuplicateFlag) {
      setSelectedDuplicateFlag("");
    }
  }, [canFilterDuplicateFlag, selectedDuplicateFlag]);

  useEffect(() => {
    if (
      selectedPlatform
      && !platformOptions.some((platform) => platform.name === selectedPlatform)
    ) {
      setSelectedPlatform("");
    }
  }, [platformOptions, selectedPlatform]);

  const listState = useLibraryEntityList({
    ...GAME_CONFIGURATION,
    autoSearchEnabled: true,
    enabled,
    extraCriteria,
  });
  const fetchGameResultPage = useCallback(
    async (page) => {
      const data = await LibraryApi.fetchGames({
        name: listState.appliedSearchQuery,
        ...extraCriteria,
        page,
        size: listState.pagination.size,
        sort: [listState.sortConfig],
      });
      return {
        detailSource: "library",
        rows: Array.isArray(data.games) ? data.games : [],
        page: data.page?.page ?? page,
        size: data.page?.size ?? listState.pagination.size,
        totalElements: data.page?.totalElements ?? 0,
      };
    },
    [
      extraCriteria,
      listState.appliedSearchQuery,
      listState.pagination.size,
      listState.sortConfig,
    ]
  );

  return {
    ...listState,
    gameResultNavigationContext: {
      detailSource: "library",
      rows: listState.rows,
      page: listState.pagination.page,
      size: listState.pagination.size,
      totalElements: listState.pagination.totalElements,
      fetchPage: fetchGameResultPage,
    },
    platformFilter: {
      error: platformError,
      isLoading: isLoadingPlatforms,
      options: platformOptions,
      selectedValue: selectedPlatform,
      onChange: handlePlatformChange,
    },
    duplicateFlagFilter: canFilterDuplicateFlag ? {
      selectedValue: selectedDuplicateFlag,
      onChange: handleDuplicateFlagChange,
    } : null,
  };
}

/**
 * Garde les plateformes utilisables comme filtre de jeux Bibliotheque.
 *
 * @param {Array<Object>} platforms - Plateformes retournees par l'API.
 * @returns {Array<Object>} Plateformes ayant au moins un jeu associe.
 */
function filterPlatformsWithGames(platforms) {
  if (!Array.isArray(platforms)) {
    return [];
  }
  return platforms.filter((platform) => Number(platform.total_games || 0) > 0);
}

/**
 * Formate les cellules de la liste publique des jeux.
 *
 * @param {string} column - Colonne affichee.
 * @param {unknown} value - Valeur brute.
 * @param {Object} row - Ligne de jeu complete.
 * @returns {string|import("react").ReactElement} Contenu de cellule.
 */
function formatLibraryGameCellValue(column, value, row) {
  if (column !== "name") {
    return TableColumnFormatService.formatGameValue(column, value, row);
  }
  const formattedName = TableColumnFormatService.formatGameValue(column, value, row);
  if (!row?.in_current_user_collection) {
    return formattedName;
  }
  return createElement(
    "span",
    { className: "libraryGameNameWithCollectionMarker" },
    createElement(
      "span",
      {
        "aria-label": "Dans votre collection",
        className: "libraryGameCollectionMarker",
        role: "img",
        title: "Dans votre collection",
      },
      "★"
    ),
    createElement("span", null, formattedName)
  );
}

export default useLibraryGames;
