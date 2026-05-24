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
 * Description : hook React des compteurs publics Bibliotheque.
 */
import { useCallback, useEffect, useState } from "react";
import LibraryApi from "../../services/LibraryApi";

/**
 * Charge les compteurs publics de la page Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Compteurs, etats de chargement, erreur et callback de rechargement.
 */
function useLibraryEntities(options = {}) {
  const [entities, setEntities] = useState({ platforms: 0, studios: 0, games: 0 });
  const [isLoadingEntities, setIsLoadingEntities] = useState(false);
  const [entitiesError, setEntitiesError] = useState("");
  const enabled = options.enabled !== false;

  const reloadEntities = useCallback(async () => {
    if (!enabled) {
      return;
    }

    try {
      setIsLoadingEntities(true);
      setEntitiesError("");
      setEntities(await LibraryApi.fetchEntities());
    } catch (error) {
      setEntities({ platforms: 0, studios: 0, games: 0 });
      setEntitiesError(error.message || "Impossible de charger les compteurs Bibliotheque.");
    } finally {
      setIsLoadingEntities(false);
    }
  }, [enabled]);

  useEffect(() => {
    reloadEntities();
  }, [reloadEntities]);

  return {
    entities,
    isLoadingEntities,
    entitiesError,
    reloadEntities,
  };
}

export default useLibraryEntities;
