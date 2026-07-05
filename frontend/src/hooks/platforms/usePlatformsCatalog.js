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
 * Description : hook React du catalogue de plateformes jeux video.
 */
import { useEffect, useState } from "react";
import AppRouting from "../../appRouting";
import AuthApi from "../../services/AuthApi";
import VideoGamesApi from "../../services/VideoGamesApi";

/**
 * Charge les plateformes et synchronise la selection initiale.
 *
 * @param {Object} options - Dependances de chargement des plateformes.
 * @returns {Object} Plateformes disponibles et etat de chargement.
 */
function usePlatformsCatalog(options) {
  const [platforms, setPlatforms] = useState([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);

  useEffect(() => {
    const fetchPlatforms = async () => {
      if (!options.hasAccessToken) {
        setPlatforms([]);
        setIsLoadingPlatforms(false);
        return;
      }

      try {
        setIsLoadingPlatforms(true);
        options.setError("");
        const data = await VideoGamesApi.fetchPlatforms();
        const loadedPlatforms = data.platforms || [];
        setPlatforms(loadedPlatforms);

        const platformIdFromUrl = AppRouting.getPlatformIdFromUrl();
        if (platformIdFromUrl) {
          options.setSelectedPlatform(platformIdFromUrl);
          options.setCurrentView("games");
        } else if (loadedPlatforms.length > 0) {
          options.setSelectedPlatform(String(loadedPlatforms[0].id || ""));
          options.setGameForm((previous) => ({
            ...previous,
            platform: previous.platform || loadedPlatforms[0].name || "",
          }));
        }
      } catch (e) {
        if (AuthApi.isSessionExpiredError(e)) {
          return;
        }
        options.setError("Impossible de charger les plateformes depuis le backend.");
      } finally {
        setIsLoadingPlatforms(false);
      }
    };

    fetchPlatforms();
  }, [options.currentView, options.odsReloadKey, options.isAuthenticated, options.hasAccessToken]);

  return { platforms, isLoadingPlatforms };
}

export default usePlatformsCatalog;
