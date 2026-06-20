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
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

const DEFAULT_PAGE = {
  page: 0,
  size: 10,
  totalElements: 0,
  totalPages: 0,
};
const DEFAULT_STORAGE_SUMMARY = {
  totalImages: 0,
  totalSizeBytes: 0,
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
  const [storageSummary, setStorageSummary] = useState(DEFAULT_STORAGE_SUMMARY);
  const [statusFilter, setStatusFilterValue] = useState("WAITING_VALIDATION");
  const [platformFilter, setPlatformFilterValue] = useState("");
  const [sortConfig, setSortConfig] = useState(DEFAULT_SORT_CONFIG);
  const [isLoading, setIsLoading] = useState(false);
  const [updatingImageId, setUpdatingImageId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [selectedPreviewImage, setSelectedPreviewImage] = useState(null);
  const moderationImageUrlsRef = useRef([]);

  const enabled = Boolean(options.enabled);

  const revokeModerationImageUrls = useCallback(() => {
    moderationImageUrlsRef.current.forEach((imageUrl) => URL.revokeObjectURL(imageUrl));
    moderationImageUrlsRef.current = [];
  }, []);

  const loadModerationImageUrls = useCallback(async (moderationImages) => {
    const imagesWithUrls = await Promise.all(
      moderationImages.map(async (image) => {
        try {
          const imageBlob = await LibraryAdminApi.fetchPlatformImageBlob(
            image.moderation_image_url || image.image_url
          );
          const imageUrl = URL.createObjectURL(imageBlob);
          moderationImageUrlsRef.current.push(imageUrl);
          return { ...image, moderation_preview_url: imageUrl };
        } catch {
          return { ...image, moderation_preview_url: "" };
        }
      })
    );
    return imagesWithUrls;
  }, []);

  const loadImages = useCallback(async () => {
    if (!enabled) {
      revokeModerationImageUrls();
      setImages([]);
      setPageInfo(DEFAULT_PAGE);
      setStorageSummary(DEFAULT_STORAGE_SUMMARY);
      return;
    }

    setIsLoading(true);
    setError("");
    revokeModerationImageUrls();
    try {
      const data = await LibraryAdminApi.listPlatformImages({
        page: pageInfo.page,
        size: pageInfo.size,
        status: statusFilter,
        platform: platformFilter,
        sort: `${getBackendSortColumn(sortConfig.column)},${sortConfig.direction}`,
      });
      const moderationImages = Array.isArray(data.images) ? data.images : [];
      setImages(await loadModerationImageUrls(moderationImages));
      setStorageSummary(normalizeStorageSummary(data.storage_summary));
      setPageInfo(normalizePageInfo(data.page, {
        page: pageInfo.page,
        size: pageInfo.size,
        totalElements: 0,
        totalPages: 0,
      }));
    } catch (loadError) {
      setError(loadError.message || "Impossible de charger les images de plateformes.");
    } finally {
      setIsLoading(false);
    }
  }, [
    enabled,
    loadModerationImageUrls,
    pageInfo.page,
    pageInfo.size,
    platformFilter,
    revokeModerationImageUrls,
    sortConfig,
    statusFilter,
  ]);

  useEffect(() => {
    loadImages();
  }, [loadImages]);

  useEffect(() => () => revokeModerationImageUrls(), [revokeModerationImageUrls]);

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
    setImages((previous) => {
      const removedImage = previous.find((image) => image.id === imageId);
      if (removedImage?.moderation_preview_url) {
        URL.revokeObjectURL(removedImage.moderation_preview_url);
        moderationImageUrlsRef.current = moderationImageUrlsRef.current.filter(
          (imageUrl) => imageUrl !== removedImage.moderation_preview_url
        );
      }
      return previous.filter((image) => image.id !== imageId);
    });
    setStorageSummary((previous) => ({
      totalImages: Math.max(0, Number(previous.totalImages || 0) - 1),
      totalSizeBytes: Math.max(
        0,
        Number(previous.totalSizeBytes || 0) - Number(removedFileSizeBytes(imageId) || 0)
      ),
    }));
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

  const removedFileSizeBytes = (imageId) => {
    const removedImage = images.find((image) => image.id === imageId);
    return Number(removedImage?.file_size_bytes || 0);
  };

  return {
    enabled,
    images,
    pageInfo,
    storageSummary,
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
 * Normalise le resume de stockage retourne par le backend.
 *
 * @param {Object} storageSummary - Payload de stockage backend.
 * @returns {Object} Resume normalise pour la vue.
 * @throws {void} Ne leve pas d'exception.
 */
function normalizeStorageSummary(storageSummary = {}) {
  return {
    totalImages: Number(storageSummary.total_images || 0),
    totalSizeBytes: Number(storageSummary.total_size_bytes || 0),
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
