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
 * Description : hook React de la page d'accueil de collection.
 */
import { useEffect, useState } from "react";
import VideoGamesApi from "../../services/VideoGamesApi";
import useHomeSearch from "./useHomeSearch";

/**
 * Gere les donnees, images et recherches de la page d'accueil.
 *
 * @param {Object} options - Dependances de chargement de l'accueil.
 * @returns {Object} Etat et callbacks de la page d'accueil.
 */
function useHomePage(options) {
  const [homeStats, setHomeStats] = useState(null);
  const [platformImageObjectUrls, setPlatformImageObjectUrls] = useState({});
  const [isLoadingHome, setIsLoadingHome] = useState(true);
  const search = useHomeSearch(options.isAuthenticated);

  useEffect(() => {
    const fetchHomeStats = async () => {
      if (!options.hasAccessToken || options.currentView !== "home") {
        setHomeStats(null);
        setIsLoadingHome(false);
        return;
      }

      try {
        setIsLoadingHome(true);
        options.setError("");
        const data = await VideoGamesApi.fetchHomeStats();
        setHomeStats(data);
      } catch (e) {
        options.setError("Impossible de charger les statistiques de l'accueil.");
      } finally {
        setIsLoadingHome(false);
      }
    };

    fetchHomeStats();
  }, [options.odsReloadKey, options.isAuthenticated, options.currentView, options.hasAccessToken]);

  useEffect(() => {
    let isCancelled = false;
    const createdObjectUrls = [];
    const imageUrls = Array.from(
      new Set((homeStats?.platforms || []).map((platform) => platform.image_url).filter(Boolean))
    );

    setPlatformImageObjectUrls({});
    if (!options.hasAccessToken || imageUrls.length === 0) {
      return () => {};
    }

    const fetchPlatformImages = async () => {
      try {
        const imageEntries = await Promise.all(
          imageUrls.map(async (imageUrl) => {
            const objectUrl = await VideoGamesApi.fetchProtectedImageObjectUrl(imageUrl);
            createdObjectUrls.push(objectUrl);
            return [imageUrl, objectUrl];
          })
        );
        if (!isCancelled) {
          setPlatformImageObjectUrls(Object.fromEntries(imageEntries));
        }
      } catch (e) {
        if (!isCancelled) {
          setPlatformImageObjectUrls({});
        }
      }
    };

    fetchPlatformImages();

    return () => {
      isCancelled = true;
      createdObjectUrls.forEach((objectUrl) => window.URL.revokeObjectURL(objectUrl));
    };
  }, [homeStats, options.hasAccessToken, options.isAuthenticated]);

  const homeStatsWithAuthenticatedImages = homeStats
    ? {
        ...homeStats,
        platforms: (homeStats.platforms || []).map((platform) => ({
          ...platform,
          image_url: platformImageObjectUrls[platform.image_url] || "",
        })),
      }
    : null;
  const selectedPlatformStats = homeStatsWithAuthenticatedImages?.platforms?.find(
    (platform) => platform.sheet_name === options.selectedPlatform
  );

  return {
    homeStats: homeStatsWithAuthenticatedImages,
    selectedPlatformStats,
    isLoadingHome,
    ...search,
  };
}

export default useHomePage;
