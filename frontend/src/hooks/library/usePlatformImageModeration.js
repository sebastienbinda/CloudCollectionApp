/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-19
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook de moderation admin des images de plateformes.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

const DEFAULT_PAGE = {
  page: 0,
  size: 10,
  totalElements: 0,
  totalPages: 0,
};
const PAGE_SIZE_OPTIONS = [10, 25, 50];
const DEFAULT_SORT_CONFIG = { column: "creation_date", direction: "desc" };

/**
 * Orchestre la liste admin et les actions de moderation d'images de plateformes.
 *
 * @param {Object} options - Permissions et activation de la section.
 * @returns {Object} Etat de liste, filtres et callbacks exposes a la vue.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function usePlatformImageModeration(options = {}) {
  const [images, setImages] = useState([]);
  const [pageInfo, setPageInfo] = useState(DEFAULT_PAGE);
  const [statusFilter, setStatusFilterValue] = useState("");
  const [platformFilter, setPlatformFilterValue] = useState("");
  const [sortConfig, setSortConfig] = useState(DEFAULT_SORT_CONFIG);
  const [isLoading, setIsLoading] = useState(false);
  const [updatingImageId, setUpdatingImageId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [selectedPreviewImage, setSelectedPreviewImage] = useState(null);

  const enabled = Boolean(options.enabled);

  const loadImages = useCallback(async () => {
    if (!enabled) {
      setImages([]);
      setPageInfo(DEFAULT_PAGE);
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      const data = await LibraryAdminApi.listPlatformImages({
        page: pageInfo.page,
        size: pageInfo.size,
        status: statusFilter,
        platform: platformFilter,
        sort: `${getBackendSortColumn(sortConfig.column)},${sortConfig.direction}`,
      });
      setImages(Array.isArray(data.images) ? data.images : []);
      setPageInfo(normalizePageInfo(data.page, pageInfo));
    } catch (loadError) {
      setError(loadError.message || "Impossible de charger les images de plateformes.");
    } finally {
      setIsLoading(false);
    }
  }, [enabled, pageInfo.page, pageInfo.size, platformFilter, sortConfig, statusFilter]);

  useEffect(() => {
    loadImages();
  }, [loadImages]);

  const platformOptions = useMemo(() => {
    const names = images
      .map((image) => String(image.platform_name || "").trim())
      .filter(Boolean);
    if (platformFilter) {
      names.push(platformFilter);
    }
    return Array.from(new Set(names)).sort((first, second) => first.localeCompare(second));
  }, [images, platformFilter]);

  const setStatusFilter = (value) => {
    setStatusFilterValue(value);
    setPageInfo((previous) => ({ ...previous, page: 0 }));
  };

  const setPlatformFilter = (value) => {
    setPlatformFilterValue(value);
    setPageInfo((previous) => ({ ...previous, page: 0 }));
  };

  const setPage = (page) => {
    setPageInfo((previous) => ({ ...previous, page }));
  };

  const setSize = (size) => {
    setPageInfo((previous) => ({ ...previous, page: 0, size }));
  };

  const toggleSort = (column) => {
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
    setPageInfo((previous) => ({ ...previous, page: 0 }));
  };

  const acceptImage = async (image) => {
    await updateStatus(image, "accepted", "Image acceptee.", true);
  };

  const refuseImage = async (image) => {
    await updateStatus(image, "refused", "Image refusee.", false);
  };

  const setMainImage = async (image) => {
    await updateImage(
      image,
      () => LibraryAdminApi.updatePlatformImageType(image.platform_id, image.id, "MAIN"),
      "Image principale mise a jour.",
      true
    );
  };

  const updateStatus = async (image, status, successMessage, shouldRefresh) => {
    await updateImage(
      image,
      () => LibraryAdminApi.updatePlatformImageStatus(image.platform_id, image.id, status),
      successMessage,
      shouldRefresh
    );
  };

  const updateImage = async (image, action, successMessage, shouldRefresh) => {
    setUpdatingImageId(image.id);
    setMessage("");
    setError("");
    try {
      await action();
      setMessage(successMessage);
      if (shouldRefresh) {
        await loadImages();
      } else {
        removeLocalImage(image.id);
      }
    } catch (updateError) {
      setError(updateError.message || "Impossible de moderer l'image de plateforme.");
    } finally {
      setUpdatingImageId(null);
    }
  };

  const removeLocalImage = (imageId) => {
    setImages((previous) => previous.filter((image) => image.id !== imageId));
    setPageInfo((previous) => {
      const totalElements = Math.max(0, Number(previous.totalElements || 0) - 1);
      const totalPages = totalElements > 0 ? Math.ceil(totalElements / previous.size) : 0;
      return {
        ...previous,
        totalElements,
        totalPages,
        page: totalPages > 0 ? Math.min(previous.page, totalPages - 1) : 0,
      };
    });
  };

  return {
    enabled,
    images,
    pageInfo,
    pageSizeOptions: PAGE_SIZE_OPTIONS,
    statusFilter,
    platformFilter,
    platformOptions,
    sortConfig,
    isLoading,
    updatingImageId,
    message,
    error,
    selectedPreviewImage,
    canUpdateStatus: Boolean(options.canUpdateStatus),
    canUpdateType: Boolean(options.canUpdateType),
    setStatusFilter,
    setPlatformFilter,
    setPage,
    setSize,
    toggleSort,
    refresh: loadImages,
    acceptImage,
    refuseImage,
    setMainImage,
    openPreview: setSelectedPreviewImage,
    closePreview: () => setSelectedPreviewImage(null),
  };
}

/**
 * Normalise les informations de pagination retournees par le backend.
 *
 * @param {Object} page - Payload de pagination backend.
 * @param {Object} fallbackPage - Pagination courante de repli.
 * @returns {Object} Pagination complete pour le tableau.
 * @throws {void} Ne leve pas d'exception.
 */
function normalizePageInfo(page = {}, fallbackPage = DEFAULT_PAGE) {
  return {
    page: Number.isFinite(page.page) ? page.page : fallbackPage.page,
    size: Number.isFinite(page.size) ? page.size : fallbackPage.size,
    totalElements: Number.isFinite(page.totalElements) ? page.totalElements : 0,
    totalPages: Number.isFinite(page.totalPages) ? page.totalPages : 0,
  };
}

/**
 * Convertit une colonne de vue en colonne de tri backend.
 *
 * @param {string} column - Colonne selectionnee dans le tableau.
 * @returns {string} Colonne acceptee par l'API backend.
 * @throws {void} Ne leve pas d'exception.
 */
function getBackendSortColumn(column) {
  return column === "platform_name" ? "platform" : column;
}

export default usePlatformImageModeration;
