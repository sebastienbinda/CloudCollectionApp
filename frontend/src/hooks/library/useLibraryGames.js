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
import useLibraryGamePlatformFilter from "./useLibraryGamePlatformFilter";
import useGameValidationWorkflow from "./useGameValidationWorkflow";
import useLibraryEntityList from "./useLibraryEntityList";
import {
  getLibraryGameColumns,
  getLibraryGameMobileVisibleColumns,
} from "./libraryGameColumns.js";

const GAME_CONFIGURATION = {
  rowsKey: "games",
  columnLabels: {
    name: "Nom",
    release_date: "Sortie",
    developer: "Developpeur",
    editor: "Editeur",
    platform: "Plateforme",
    status: "Statut",
  },
  sortableColumns: ["name", "release_date", "developer", "platform"],
  tableClassName: "libraryGamesTable",
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les jeux Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchGames(criteria),
  formatCellValue: formatLibraryGameCellValue,
};
const GAME_VALIDATION_STATUS_FILTERS = [
  { value: "", label: "Tous les statuts de validation" },
  { value: "WAITING_VALIDATION", label: "En attente de validation" },
  { value: "ACCEPTED", label: "Acceptes" },
];

/**
 * Charge et pilote la table publique des jeux Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table jeux.
 */
function useLibraryGames(options = {}) {
  const enabled = options.enabled !== false;
  const onGameValidationSummaryRefresh = options.onGameValidationSummaryRefresh;
  const canFilterDuplicateFlag = options.authenticatedProfile === "ADMIN";
  const columns = useMemo(
    () => getLibraryGameColumns(options.authenticatedProfile),
    [options.authenticatedProfile]
  );
  const mobileVisibleColumns = useMemo(
    () => getLibraryGameMobileVisibleColumns(columns),
    [columns]
  );
  const canManageGameValidation = (
    options.authenticatedProfile === "ADMIN" &&
    options.canManageGameValidation === true
  );
  const [selectedDuplicateFlag, setSelectedDuplicateFlag] = useState("");
  const [selectedValidationStatus, setSelectedValidationStatus] = useState("");
  const gamePlatformFilter = useLibraryGamePlatformFilter({ enabled });
  const extraCriteria = useMemo(
    () => ({
      duplicate_flag: canFilterDuplicateFlag ? selectedDuplicateFlag : "",
      platform: gamePlatformFilter.selectedPlatform,
      status: canManageGameValidation ? selectedValidationStatus : "",
    }),
    [
      canFilterDuplicateFlag,
      canManageGameValidation,
      gamePlatformFilter.selectedPlatform,
      selectedDuplicateFlag,
      selectedValidationStatus,
    ]
  );

  const handleDuplicateFlagChange = useCallback((duplicateFlag) => {
    setSelectedDuplicateFlag(duplicateFlag);
  }, []);

  const handleValidationStatusChange = useCallback((validationStatus) => {
    setSelectedValidationStatus(validationStatus);
  }, []);

  useEffect(() => {
    if (!canFilterDuplicateFlag && selectedDuplicateFlag) {
      setSelectedDuplicateFlag("");
    }
  }, [canFilterDuplicateFlag, selectedDuplicateFlag]);

  useEffect(() => {
    if (!canManageGameValidation && selectedValidationStatus) {
      setSelectedValidationStatus("");
    }
  }, [canManageGameValidation, selectedValidationStatus]);

  const listState = useLibraryEntityList({
    ...GAME_CONFIGURATION,
    autoSearchEnabled: true,
    columns,
    enabled,
    extraCriteria,
    mobileVisibleColumns,
  });
  const { clearSelection, workflow: gameValidationWorkflow } = useGameValidationWorkflow({
    enabled: canManageGameValidation,
    rows: listState.rows,
    reloadList: listState.reload,
    reloadSummary: onGameValidationSummaryRefresh,
  });

  useEffect(() => {
    clearSelection();
  }, [clearSelection, selectedValidationStatus]);

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
    platformFilter: gamePlatformFilter.platformFilter,
    duplicateFlagFilter: canFilterDuplicateFlag ? {
      selectedValue: selectedDuplicateFlag,
      onChange: handleDuplicateFlagChange,
    } : null,
    validationStatusFilter: canManageGameValidation ? {
      options: GAME_VALIDATION_STATUS_FILTERS,
      selectedValue: selectedValidationStatus,
      onChange: handleValidationStatusChange,
    } : null,
    validationWorkflow: gameValidationWorkflow,
  };
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
  const markers = [];
  if (row?.in_current_user_collection) {
    markers.push(createElement(
      "span",
      {
        "aria-label": "Dans votre collection",
        className: "libraryGameCollectionMarker",
        key: "collection",
        role: "img",
        title: "Dans votre collection",
      },
      "★"
    ));
  }
  if (row?.in_current_user_wishlist) {
    markers.push(createElement(
      "span",
      {
        "aria-label": "Dans votre liste de souhaits",
        className: "libraryGameWishlistMarker",
        key: "wishlist",
        role: "img",
        title: "Dans votre liste de souhaits",
      },
      "♥"
    ));
  }
  if (markers.length === 0) {
    return formattedName;
  }
  return createElement(
    "span",
    { className: "libraryGameNameWithCollectionMarker" },
    ...markers,
    createElement("span", null, formattedName)
  );
}

export default useLibraryGames;
