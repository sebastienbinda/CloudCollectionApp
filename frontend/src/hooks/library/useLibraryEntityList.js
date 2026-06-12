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
 * Description : hook React generique des listes paginees Bibliotheque.
 */
import { useCallback, useEffect, useState } from "react";

const DEFAULT_PAGE = 0;
const DEFAULT_SIZE = 500;
const SIZE_OPTIONS = [25, 50, 100, 500];

/**
 * Gere recherche, tri, chargement et pagination d'une entite Bibliotheque.
 *
 * @param {Object} configuration - Configuration de l'entite cible.
 * @returns {Object} Etat de liste et callbacks compatibles avec `TableComponent`.
 */
function useLibraryEntityList(configuration) {
  const {
    columnLabels = {},
    columns,
    defaultSortColumn = "name",
    enabled: configuredEnabled,
    errorMessage,
    fetchList,
    mobileVisibleColumns = [],
    rowsKey,
    sortableColumns = [],
  } = configuration;
  const [rows, setRows] = useState([]);
  const [pageMetadata, setPageMetadata] = useState({
    page: DEFAULT_PAGE,
    size: DEFAULT_SIZE,
    totalElements: 0,
    totalPages: 1,
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [appliedSearchQuery, setAppliedSearchQuery] = useState("");
  const [sortConfig, setSortConfig] = useState({
    column: defaultSortColumn,
    direction: "asc",
  });
  const [page, setPage] = useState(DEFAULT_PAGE);
  const [size, setSize] = useState(DEFAULT_SIZE);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const enabled = configuredEnabled !== false;

  const reload = useCallback(async () => {
    if (!enabled) {
      setRows([]);
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      const data = await fetchList({
        name: appliedSearchQuery,
        page,
        size,
        sort: [sortConfig],
      });
      setRows(Array.isArray(data[rowsKey]) ? data[rowsKey] : []);
      setPageMetadata({
        page: data.page?.page ?? page,
        size: data.page?.size ?? size,
        totalElements: data.page?.totalElements ?? 0,
        totalPages: data.page?.totalPages ?? 1,
      });
    } catch (caughtError) {
      setRows([]);
      setError(caughtError.message || errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [appliedSearchQuery, enabled, errorMessage, fetchList, page, rowsKey, size, sortConfig]);

  useEffect(() => {
    reload();
  }, [reload]);

  const submitSearch = useCallback((event) => {
    event?.preventDefault?.();
    setPage(DEFAULT_PAGE);
    setAppliedSearchQuery(searchQuery);
  }, [searchQuery]);

  const clearSearch = useCallback(() => {
    setSearchQuery("");
    setAppliedSearchQuery("");
    setPage(DEFAULT_PAGE);
  }, []);

  const toggleSort = useCallback((column) => {
    if (!sortableColumns.includes(column)) {
      return;
    }
    setPage(DEFAULT_PAGE);
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  }, [sortableColumns]);

  const changePageSize = useCallback((newSize) => {
    setPage(DEFAULT_PAGE);
    setSize(newSize);
  }, []);

  return {
    rows,
    columns,
    columnLabels,
    mobileVisibleColumns,
    sortableColumns,
    searchQuery,
    appliedSearchQuery,
    setSearchQuery,
    submitSearch,
    clearSearch,
    sortConfig,
    toggleSort,
    isLoading,
    error,
    reload,
    pagination: {
      ...pageMetadata,
      isLoading,
      sizeOptions: SIZE_OPTIONS,
      onPageChange: setPage,
      onSizeChange: changePageSize,
    },
  };
}

export default useLibraryEntityList;
