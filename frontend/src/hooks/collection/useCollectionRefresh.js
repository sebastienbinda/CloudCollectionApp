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
 * Description : hook React de rechargement transversal de collection.
 */
import { useState } from "react";
import VideoGamesApi from "../../services/VideoGamesApi";

/**
 * Gere les cles de rechargement ODS et le reset du cache backend.
 *
 * @returns {Object} Etat et actions de rechargement de collection.
 */
function useCollectionRefresh() {
  const [cacheResetMessage, setCacheResetMessage] = useState("");
  const [cacheResetError, setCacheResetError] = useState("");
  const [isResettingCache, setIsResettingCache] = useState(false);
  const [odsReloadKey, setOdsReloadKey] = useState(0);
  const [gamesReloadKey, setGamesReloadKey] = useState(0);

  const reloadOds = () => setOdsReloadKey((previous) => previous + 1);
  const reloadGames = () => setGamesReloadKey((previous) => previous + 1);

  /**
   * Reinitialise le cache ODS backend puis demande le rechargement des vues.
   *
   * @returns {Promise<void>} Promesse resolue apres la mise a jour des messages.
   */
  const resetOdsCache = async () => {
    setCacheResetMessage("");
    setCacheResetError("");

    try {
      setIsResettingCache(true);
      await VideoGamesApi.resetCache();
      setCacheResetMessage("Cache reinitialise. Donnees rechargees.");
      reloadOds();
      reloadGames();
    } catch (e) {
      setCacheResetError(e.message || "Impossible de reinitialiser le cache.");
    } finally {
      setIsResettingCache(false);
    }
  };

  return {
    cacheResetMessage,
    cacheResetError,
    isResettingCache,
    odsReloadKey,
    gamesReloadKey,
    reloadOds,
    reloadGames,
    resetOdsCache,
  };
}

export default useCollectionRefresh;
