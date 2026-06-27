/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-13
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React de chargement du detail d'un jeu.
 */
import { useEffect, useState } from "react";
import LibraryApi from "../../services/LibraryApi";
import VideoGamesApi from "../../services/VideoGamesApi";

/**
 * Charge le detail d'un jeu depuis la Bibliotheque ou la collection.
 *
 * @param {Object} options - Source, identifiant et etat d'acces.
 * @returns {Object} Etat de la page detail jeu.
 */
function useGameDetailPage(options) {
  const [gameDetail, setGameDetail] = useState(null);
  const [gameDetailError, setGameDetailError] = useState("");
  const [duplicateReportMessage, setDuplicateReportMessage] = useState("");
  const [duplicateReportError, setDuplicateReportError] = useState("");
  const [isLoadingGameDetail, setIsLoadingGameDetail] = useState(false);
  const [isReportingDuplicate, setIsReportingDuplicate] = useState(false);

  useEffect(() => {
    const loadGameDetail = async () => {
      if (options.currentView !== "gameDetail" || !options.gameId) {
        setGameDetail(null);
        setGameDetailError("");
        setDuplicateReportMessage("");
        setDuplicateReportError("");
        setIsLoadingGameDetail(false);
        return;
      }

      if (options.source === "collection" && !options.hasAccessToken) {
        setGameDetail(null);
        setGameDetailError("Connectez-vous pour consulter ce jeu de collection.");
        setDuplicateReportMessage("");
        setDuplicateReportError("");
        return;
      }

      try {
        setIsLoadingGameDetail(true);
        setGameDetailError("");
        setDuplicateReportMessage("");
        setDuplicateReportError("");
        const data = options.source === "collection"
          ? await VideoGamesApi.fetchGame(options.gameId)
          : await LibraryApi.fetchGame(options.gameId);
        setGameDetail(data.game || null);
      } catch (error) {
        setGameDetail(null);
        setGameDetailError(error.message || "Impossible de charger le detail du jeu.");
      } finally {
        setIsLoadingGameDetail(false);
      }
    };

    loadGameDetail();
  }, [options.currentView, options.gameId, options.hasAccessToken, options.source]);

  useEffect(() => {
    if (
      options.currentView !== "gameDetail" ||
      options.source !== "library" ||
      options.canReportDuplicate !== true ||
      options.isGuest ||
      options.hasCollection !== null ||
      typeof options.checkCurrentUserCollection !== "function"
    ) {
      return;
    }
    options.checkCurrentUserCollection().catch(() => {});
  }, [
    options.currentView,
    options.source,
    options.canReportDuplicate,
    options.isGuest,
    options.hasCollection,
    options.checkCurrentUserCollection,
  ]);

  const reportDuplicate = async () => {
    if (!gameDetail?.id) {
      return;
    }
    const confirmed = window.confirm(
      "Signaler ce jeu comme doublon informe les administrateurs qu'il pourrait "
      + "correspondre a un autre jeu de la meme plateforme. Aucun changement "
      + "n'est applique directement a votre collection. Confirmer le signalement ?"
    );
    if (!confirmed) {
      return;
    }
    try {
      setIsReportingDuplicate(true);
      setDuplicateReportMessage("");
      setDuplicateReportError("");
      const data = await LibraryApi.reportGameDuplicate(gameDetail.id);
      setGameDetail((currentGame) => currentGame ? { ...currentGame, duplicate_flag: true } : currentGame);
      setDuplicateReportMessage(data.message || "Merci, un administrateur verifiera ce signalement.");
    } catch (error) {
      setDuplicateReportError(error.message || "Impossible de signaler ce doublon.");
    } finally {
      setIsReportingDuplicate(false);
    }
  };

  return {
    canCorrectDuplicate: (
      options.source === "library" &&
      options.canCorrectDuplicate === true
    ),
    canReportDuplicate: (
      ["collection", "library"].includes(options.source) &&
      options.canReportDuplicate === true &&
      options.hasCollection === true &&
      !options.isGuest &&
      !gameDetail?.duplicate_flag
    ),
    duplicateReportError,
    duplicateReportMessage,
    gameDetail,
    gameDetailError,
    isLoadingGameDetail,
    isReportingDuplicate,
    reportDuplicate,
  };
}

export default useGameDetailPage;
