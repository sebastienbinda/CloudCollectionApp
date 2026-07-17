/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook React central de navigation entre jeux d'une liste.
 */
import { useMemo, useState } from "react";
import {
  buildGameResultNavigationState,
  findAdjacentGameInCurrentRows,
  getAdjacentPageToLoad,
  getGameNavigationId,
  normalizeGameResultContext,
  selectAdjacentGameFromLoadedPage,
} from "./gameResultNavigation";

/**
 * Memorise le contexte de liste et expose les actions precedent/suivant.
 *
 * @param {Object} options - Dependances de navigation detail jeu.
 * @returns {Object} Etat, actions et fonction d'enregistrement de contexte.
 */
function useGameResultNavigation(options) {
  const [resultContext, setResultContext] = useState(null);
  const [isLoadingAdjacentGame, setIsLoadingAdjacentGame] = useState(false);

  const registerGameResultContext = (context, game) => {
    const gameId = getGameNavigationId(game);
    if (!context || !gameId) {
      setResultContext(null);
      return;
    }
    const normalizedContext = normalizeGameResultContext(context);
    const hasOpenedGame = normalizedContext.rows.some(
      (row) => getGameNavigationId(row) === gameId
    );
    setResultContext(hasOpenedGame ? normalizedContext : null);
  };

  const navigationState = useMemo(
    () => buildGameResultNavigationState(resultContext, options.gameId),
    [resultContext, options.gameId]
  );

  const openAdjacentGame = async (direction) => {
    if (!resultContext || !options.gameId || typeof options.openGameDetail !== "function") {
      return;
    }

    const localAdjacentGame = findAdjacentGameInCurrentRows(
      resultContext,
      options.gameId,
      direction
    );
    if (localAdjacentGame) {
      options.openGameDetail(localAdjacentGame, resultContext.detailSource || options.source);
      return;
    }

    const pageToLoad = getAdjacentPageToLoad(resultContext, options.gameId, direction);
    if (pageToLoad === null || typeof resultContext.fetchPage !== "function") {
      return;
    }

    try {
      setIsLoadingAdjacentGame(true);
      const loadedContext = normalizeGameResultContext(
        await resultContext.fetchPage(pageToLoad)
      );
      const loadedGame = selectAdjacentGameFromLoadedPage(loadedContext.rows, direction);
      if (!loadedGame) {
        return;
      }
      setResultContext({
        ...resultContext,
        ...loadedContext,
        detailSource: resultContext.detailSource,
        fetchPage: resultContext.fetchPage,
      });
      options.openGameDetail(loadedGame, resultContext.detailSource || options.source);
    } finally {
      setIsLoadingAdjacentGame(false);
    }
  };

  return {
    ...navigationState,
    isLoadingAdjacentGame,
    openPreviousGame: () => openAdjacentGame("previous"),
    openNextGame: () => openAdjacentGame("next"),
    registerGameResultContext,
  };
}

export default useGameResultNavigation;
