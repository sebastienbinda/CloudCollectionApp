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

  const selectedPlatformStats = homeStats?.platforms?.find(
    (platform) => String(platform.id) === String(options.selectedPlatform)
  );

  return {
    homeStats,
    selectedPlatformStats,
    isLoadingHome,
    ...search,
  };
}

export default useHomePage;
