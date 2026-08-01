/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-01
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook du filtre plateforme de la liste jeux Bibliotheque.
 */
import { useCallback, useEffect, useState } from "react";
import LibraryApi from "../../services/LibraryApi.js";

const PLATFORM_PAGE_SIZE = 500;

/**
 * Charge les plateformes disponibles pour filtrer les jeux Bibliotheque.
 *
 * @param {Object} options - Options d'activation du filtre.
 * @returns {Object} Etat du filtre plateforme et callback de changement.
 * @throws {void} Les erreurs sont exposees dans l'etat du hook.
 */
function useLibraryGamePlatformFilter(options = {}) {
  const enabled = options.enabled !== false;
  const [platformOptions, setPlatformOptions] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(false);
  const [platformError, setPlatformError] = useState("");

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

  useEffect(() => {
    if (
      selectedPlatform &&
      !platformOptions.some((platform) => platform.name === selectedPlatform)
    ) {
      setSelectedPlatform("");
    }
  }, [platformOptions, selectedPlatform]);

  const handlePlatformChange = useCallback((platformName) => {
    setSelectedPlatform(platformName);
  }, []);

  return {
    selectedPlatform,
    platformFilter: {
      error: platformError,
      isLoading: isLoadingPlatforms,
      options: platformOptions,
      selectedValue: selectedPlatform,
      onChange: handlePlatformChange,
    },
  };
}

/**
 * Garde les plateformes utilisables comme filtre de jeux Bibliotheque.
 *
 * @param {Array<Object>} platforms - Plateformes retournees par l'API.
 * @returns {Array<Object>} Plateformes ayant au moins un jeu associe.
 * @throws {void} Ne leve pas d'exception.
 */
function filterPlatformsWithGames(platforms) {
  if (!Array.isArray(platforms)) {
    return [];
  }
  return platforms.filter((platform) => Number(platform.total_games || 0) > 0);
}

export { filterPlatformsWithGames };
export default useLibraryGamePlatformFilter;
