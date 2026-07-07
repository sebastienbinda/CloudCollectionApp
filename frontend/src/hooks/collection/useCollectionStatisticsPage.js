/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de la page statistiques collection.
 */
import { useCallback, useEffect, useState } from "react";
import CollectionStatisticsApi from "../../services/CollectionStatisticsApi";

/**
 * Charge et expose les statistiques detaillees de collection.
 *
 * @param {Object} options - Etat de navigation et session.
 * @returns {Object} Etat de la page statistiques.
 */
function useCollectionStatisticsPage(options = {}) {
  const [statistics, setStatistics] = useState(null);
  const [statisticsError, setStatisticsError] = useState("");
  const [isLoadingStatistics, setIsLoadingStatistics] = useState(false);
  const [selectedPlatformId, setSelectedPlatformId] = useState(null);

  const togglePlatformFilter = useCallback((platformId) => {
    setSelectedPlatformId((currentPlatformId) => (
      currentPlatformId === platformId ? null : platformId
    ));
  }, []);

  useEffect(() => {
    if (!options.enabled || !options.hasAccessToken) {
      setStatistics(null);
      setStatisticsError("");
      setIsLoadingStatistics(false);
      setSelectedPlatformId(null);
      return undefined;
    }

    let isCancelled = false;
    setIsLoadingStatistics(true);
    setStatisticsError("");
    CollectionStatisticsApi.fetchStatistics({ platformId: selectedPlatformId })
      .then((payload) => {
        if (!isCancelled) {
          setStatistics(payload);
        }
      })
      .catch((error) => {
        if (!isCancelled) {
          setStatisticsError(error.message || "Impossible de charger les statistiques.");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoadingStatistics(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [options.enabled, options.hasAccessToken, options.reloadKey, selectedPlatformId]);

  return {
    statistics,
    statisticsError,
    isLoadingStatistics,
    selectedPlatformId,
    togglePlatformFilter,
  };
}

export default useCollectionStatisticsPage;
