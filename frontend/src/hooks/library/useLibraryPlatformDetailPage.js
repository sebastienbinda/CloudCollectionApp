/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-15
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de chargement du detail d'une plateforme Bibliotheque.
 */
import { useEffect, useState } from "react";
import LibraryApi from "../../services/LibraryApi";

/**
 * Charge le detail d'une plateforme publique de la Bibliotheque.
 *
 * @param {Object} options - Identifiant et etat de vue courante.
 * @returns {Object} Etat de la page detail plateforme.
 */
function useLibraryPlatformDetailPage(options) {
  const [platformDetail, setPlatformDetail] = useState(null);
  const [platformDetailError, setPlatformDetailError] = useState("");
  const [isLoadingPlatformDetail, setIsLoadingPlatformDetail] = useState(false);

  useEffect(() => {
    const loadPlatformDetail = async () => {
      if (options.currentView !== "libraryPlatformDetail" || !options.platformId) {
        setPlatformDetail(null);
        setPlatformDetailError("");
        setIsLoadingPlatformDetail(false);
        return;
      }

      try {
        setIsLoadingPlatformDetail(true);
        setPlatformDetailError("");
        const data = await LibraryApi.fetchPlatform(options.platformId);
        setPlatformDetail(data.platform || null);
      } catch (error) {
        setPlatformDetail(null);
        setPlatformDetailError(error.message || "Impossible de charger le detail de la plateforme.");
      } finally {
        setIsLoadingPlatformDetail(false);
      }
    };

    loadPlatformDetail();
  }, [options.currentView, options.platformId]);

  return {
    platformDetail,
    platformDetailError,
    isLoadingPlatformDetail,
  };
}

export default useLibraryPlatformDetailPage;
