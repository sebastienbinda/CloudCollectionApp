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
 * Description : hook React de la liste publique des jeux Bibliotheque.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import LibraryApi from "../../services/LibraryApi";
import useLibraryEntityList from "./useLibraryEntityList";

const GAME_CONFIGURATION = {
  rowsKey: "games",
  columns: ["name", "release_date", "developer", "editor", "platform", "status"],
  columnLabels: {
    name: "Nom",
    release_date: "Sortie",
    developer: "Developpeur",
    editor: "Editeur",
    platform: "Plateforme",
    status: "Statut",
  },
  mobileVisibleColumns: ["name", "release_date"],
  sortableColumns: ["name", "release_date", "developer", "platform"],
  tableClassName: "libraryGamesTable",
  defaultSortColumn: "name",
  errorMessage: "Impossible de charger les jeux Bibliotheque.",
  fetchList: (criteria) => LibraryApi.fetchGames(criteria),
};
const PLATFORM_PAGE_SIZE = 500;

/**
 * Charge et pilote la table publique des jeux Bibliotheque.
 *
 * @param {Object} options - Options de chargement du hook.
 * @returns {Object} Etat et callbacks de la table jeux.
 */
function useLibraryGames(options = {}) {
  const enabled = options.enabled !== false;
  const [platformOptions, setPlatformOptions] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(false);
  const [platformError, setPlatformError] = useState("");
  const extraCriteria = useMemo(
    () => ({ platform: selectedPlatform }),
    [selectedPlatform]
  );

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
          setPlatformOptions(Array.isArray(data.platforms) ? data.platforms : []);
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

  const handlePlatformChange = useCallback((platformName) => {
    setSelectedPlatform(platformName);
  }, []);

  const listState = useLibraryEntityList({
    ...GAME_CONFIGURATION,
    autoSearchEnabled: true,
    enabled,
    extraCriteria,
  });

  return {
    ...listState,
    platformFilter: {
      error: platformError,
      isLoading: isLoadingPlatforms,
      options: platformOptions,
      selectedValue: selectedPlatform,
      onChange: handlePlatformChange,
    },
  };
}

export default useLibraryGames;
