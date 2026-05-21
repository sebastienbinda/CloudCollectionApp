/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
import { useEffect, useState } from "react";
import { filterGames, getStudioCount, sortGames } from "./collectionUtils";
import AppRouting from "./appRouting";
import AppFrame from "./components/AppFrame";
import AuthSessionModal from "./components/AuthSessionModal";
import AppViewSwitch from "./components/AppViewSwitch";
import useAuthSessionModal from "./hooks/useAuthSessionModal";
import useBackendActionPermissions from "./hooks/useBackendActionPermissions";
import useOdsDownload from "./hooks/useOdsDownload";
import usePlatformGameMutations from "./hooks/usePlatformGameMutations";
import useWishlistGameMutations from "./hooks/useWishlistGameMutations";
import AddGameChoicesApi from "./services/AddGameChoicesApi";
import AuthApi from "./services/AuthApi";
import JeuxVideoApi from "./services/JeuxVideoApi";
import WishlistAddApi from "./services/WishlistAddApi";
const initialGameForm = AppRouting.createInitialGameForm();
/** Composant racine React. @param {void} Aucun. @returns {import("react").JSX.Element} Interface. */
function App() {
  const [currentView, setCurrentView] = useState(AppRouting.getViewFromUrl);
  const [homeStats, setHomeStats] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState(() =>
    AppRouting.getViewFromUrl() === "wishlist"
      ? AppRouting.wishlistSheetName
      : AppRouting.getPlatformFromUrl()
  );
  const [games, setGames] = useState([]);
  const [valuesByColumn, setValuesByColumn] = useState({});
  const [columnFilters, setColumnFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ column: "Nom du jeu", direction: "asc" });
  const [homeSearchQuery, setHomeSearchQuery] = useState("");
  const [homeSearchResults, setHomeSearchResults] = useState([]);
  const [homeSearchError, setHomeSearchError] = useState("");
  const [hasSearchedGames, setHasSearchedGames] = useState(false);
  const [gameForm, setGameForm] = useState(initialGameForm);
  const [addGameMessage, setAddGameMessage] = useState("");
  const [addGameError, setAddGameError] = useState("");
  const [addGameColumnValues, setAddGameColumnValues] = useState({});
  const [cacheResetMessage, setCacheResetMessage] = useState("");
  const [cacheResetError, setCacheResetError] = useState("");
  const actionPermissions = useBackendActionPermissions();
  const [isLoadingHome, setIsLoadingHome] = useState(true);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [isLoadingGames, setIsLoadingGames] = useState(false);
  const [isSearchingGames, setIsSearchingGames] = useState(false);
  const [isAddingGame, setIsAddingGame] = useState(false);
  const [isResettingCache, setIsResettingCache] = useState(false);
  const [odsReloadKey, setOdsReloadKey] = useState(0);
  const [gamesReloadKey, setGamesReloadKey] = useState(0);
  const [error, setError] = useState("");
  const authSessionModal = useAuthSessionModal();

  const namedGames = games.filter((game) => String(game["Nom du jeu"] || "").trim() !== "");
  const columns = namedGames.length > 0
    ? ["Nom du jeu", ...Object.keys(namedGames[0]).filter((column) => column !== "Nom du jeu")]
    : [];
  const filteredGames = filterGames(namedGames, columns, columnFilters);
  const sortedGames = sortGames(filteredGames, sortConfig);
  const selectedPlatformStats = homeStats?.platforms?.find(
    (platform) => platform.sheet_name === selectedPlatform
  );
  const authenticatedUsername = actionPermissions.isAuthenticated
    ? AuthApi.getAuthenticatedUsername()
    : "";
  const reloadOds = () => setOdsReloadKey((previous) => previous + 1);
  const reloadGames = () => setGamesReloadKey((previous) => previous + 1);
  const gameMutations = usePlatformGameMutations(selectedPlatform, reloadOds, reloadGames);
  const wishlistMutations = useWishlistGameMutations(reloadOds, reloadGames);
  const odsDownload = useOdsDownload();
  const hasAccessToken = AuthApi.getAccessToken().trim().length > 0;
  /**
   * Synchronise l'URL avec la plateforme selectionnee.
   *
   * @param {string} platform - Nom de plateforme a placer dans `?platform=`.
   * @returns {void} Modifie l'historique navigateur sans recharger la page.
   */
  const updatePlatformUrl = (platform) => {
    const url = new URL(window.location.href);
    url.pathname = "/";
    if (platform) {
      url.searchParams.set("platform", platform);
    } else {
      url.searchParams.delete("platform");
    }
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  /**
   * Efface les messages lies a la suppression d'un jeu de plateforme.
   *
   * @param {void} Aucun - Utilise les setters React de feedback.
   * @returns {void} Vide le succes et l'erreur de suppression.
   */
  const clearDeleteGameFeedback = () => {
    gameMutations.clearDeleteGameFeedback();
  };

  /**
   * Revient a la page d'accueil authentifiee.
   *
   * @param {void} Aucun - Utilise l'etat React et l'historique navigateur.
   * @returns {void} Met `currentView` a `home` et remplace l'URL par `/accueil`.
   */
  const goHome = () => {
    clearDeleteGameFeedback();
    setCurrentView("home");
    window.history.pushState({}, "", "/accueil");
  };

  /**
   * Ouvre la page About publique.
   *
   * @param {void} Aucun - Utilise l'etat React et l'historique navigateur.
   * @returns {void} Met `currentView` a `about` et pousse `/about`.
   */
  const openAbout = () => {
    clearDeleteGameFeedback();
    setCurrentView("about");
    window.history.pushState({}, "", "/about");
  };

  /**
   * Ouvre la page d'ajout de jeu et initialise la plateforme du formulaire.
   *
   * @param {void} Aucun - Utilise la plateforme courante et la liste chargee.
   * @returns {void} Affiche la vue `addGame` et pousse `/add-game` dans l'historique.
   */
  const openAddGamePage = () => {
    clearDeleteGameFeedback();
    setCurrentView("addGame");
    setAddGameMessage("");
    setAddGameError("");
    setGameForm((previous) => ({
      ...previous,
      platform: previous.platform || selectedPlatform || platforms[0] || "",
    }));
    window.history.pushState({}, "", "/add-game");
  };

  /** Ouvre le tableau de bord administrateur.
   * @param {void} Aucun - Utilise l'etat React et l'historique navigateur.
   * @returns {void} Affiche la vue d'administration. */
  const openAdminDashboard = () => {
    clearDeleteGameFeedback();
    setCurrentView("adminDashboard");
    window.history.pushState({}, "", "/admin-dashboard");
  };
  /**
   * Ouvre la vue detail d'une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS de la plateforme.
   * @returns {void} Met a jour l'etat React et l'URL.
   */
  const openPlatform = (platform) => {
    clearDeleteGameFeedback();
    setSelectedPlatform(platform);
    setCurrentView("games");
    updatePlatformUrl(platform);
  };

  /**
   * Ouvre la vue dediee a l'onglet `Liste de souhaits`.
   *
   * @param {void} Aucun - Utilise le nom d'onglet configure dans `AppRouting`.
   * @returns {void} Met a jour l'etat React et l'URL.
   */
  const openWishlist = () => {
    clearDeleteGameFeedback();
    setSelectedPlatform(AppRouting.wishlistSheetName);
    setCurrentView("wishlist");
    window.history.pushState({}, "", "/wishlist");
  };

  /**
   * Met a jour un champ du formulaire d'ajout de jeu.
   *
   * @param {string} field - Nom du champ du formulaire.
   * @param {string} value - Nouvelle valeur saisie.
   * @returns {void} Met a jour `gameForm`.
   */
  const updateGameFormValue = (field, value) => {
    setGameForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  /**
   * Ferme et reinitialise le panneau de resultats de recherche de l'accueil.
   *
   * @param {void} Aucun - Utilise les setters React de recherche.
   * @returns {void} Vide la recherche et masque les resultats.
   */
  const closeHomeSearch = () => {
    setHomeSearchResults([]);
    setHomeSearchError("");
    setHasSearchedGames(false);
    setHomeSearchQuery("");
  };

  /**
   * Alterne le tri ascendant/descendant sur une colonne.
   *
   * @param {string} column - Nom de colonne a trier.
   * @returns {void} Met a jour `sortConfig`.
   */
  const toggleSort = (column) => {
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };

  useEffect(() => {
    const fetchHomeStats = async () => {
      if (!hasAccessToken || currentView !== "home") {
        setHomeStats(null);
        setIsLoadingHome(false);
        return;
      }

      try {
        setIsLoadingHome(true);
        setError("");
        const data = await JeuxVideoApi.fetchHomeStats();
        setHomeStats(data);
      } catch (e) {
        setError("Impossible de charger les statistiques de l'accueil.");
      } finally {
        setIsLoadingHome(false);
      }
    };

    fetchHomeStats();
  }, [odsReloadKey, actionPermissions.isAuthenticated, currentView, hasAccessToken]);

  useEffect(() => {
    const fetchPlatforms = async () => {
      if (!hasAccessToken) {
        setPlatforms([]);
        setIsLoadingPlatforms(false);
        return;
      }

      try {
        setIsLoadingPlatforms(true);
        setError("");
        const data = await JeuxVideoApi.fetchPlatforms();
        const loadedPlatforms = (data.platforms || [])
          .filter((platform) => !["Accueil", "Liste de souhaits"].includes(platform));
        setPlatforms(loadedPlatforms);

        const platformFromUrl = AppRouting.getPlatformFromUrl();
        if (currentView === "wishlist") {
          setSelectedPlatform(AppRouting.wishlistSheetName);
        } else if (platformFromUrl) {
          setSelectedPlatform(platformFromUrl);
          setCurrentView("games");
        } else if (loadedPlatforms.length > 0) {
          setSelectedPlatform(loadedPlatforms[0]);
          setGameForm((previous) => ({
            ...previous,
            platform: previous.platform || loadedPlatforms[0],
          }));
        }
      } catch (e) {
        setError("Impossible de charger les plateformes depuis le backend.");
      } finally {
        setIsLoadingPlatforms(false);
      }
    };

    fetchPlatforms();
  }, [currentView, odsReloadKey, actionPermissions.isAuthenticated, hasAccessToken]);

  useEffect(() => {
    const handlePopState = () => {
      clearDeleteGameFeedback();
      const pathname = window.location.pathname;
      if (pathname === "/about") {
        setCurrentView("about");
        return;
      }
      if (pathname === "/auth") {
        setCurrentView("auth");
        return;
      }
      if (!AppRouting.hasStoredAccessToken()) {
        setSelectedPlatform("");
        setCurrentView("about");
        window.history.replaceState({}, "", "/about");
        return;
      }
      if (pathname === "/accueil") {
        setCurrentView("home");
        return;
      }
      if (pathname === "/add-game") {
        setCurrentView("addGame");
        return;
      }
      if (pathname === "/admin-dashboard") {
        setCurrentView("adminDashboard");
        return;
      }
      if (pathname === "/wishlist") {
        setSelectedPlatform(AppRouting.wishlistSheetName);
        setCurrentView("wishlist");
        return;
      }

      const platformFromUrl = AppRouting.getPlatformFromUrl();
      if (platformFromUrl) {
        setSelectedPlatform(platformFromUrl);
        setCurrentView("games");
      } else {
        setCurrentView(AppRouting.hasStoredAccessToken() ? "home" : "about");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    const fetchGames = async () => {
      if (!hasAccessToken || !selectedPlatform) {
        setGames([]);
        setIsLoadingGames(false);
        return;
      }

      try {
        setIsLoadingGames(true);
        setError("");
        const data = await JeuxVideoApi.fetchGames(selectedPlatform);
        setGames(Array.isArray(data) ? data : []);
        setColumnFilters({});
      } catch (e) {
        setError("Impossible de charger les jeux video pour cette plateforme.");
        setGames([]);
      } finally {
        setIsLoadingGames(false);
      }
    };

    fetchGames();
  }, [selectedPlatform, gamesReloadKey, actionPermissions.isAuthenticated, hasAccessToken]);

  useEffect(() => {
    const fetchColumnValues = async () => {
      if (!hasAccessToken || !selectedPlatform) {
        setValuesByColumn({});
        return;
      }

      try {
        const data = await JeuxVideoApi.fetchColumnValues(selectedPlatform);
        setValuesByColumn(data.values_by_column || {});
      } catch (e) {
        setValuesByColumn({});
      }
    };

    fetchColumnValues();
  }, [selectedPlatform, gamesReloadKey, actionPermissions.isAuthenticated, hasAccessToken]);

  useEffect(() => {
    const refreshHomeSearchResults = async () => {
      const query = homeSearchQuery.trim();
      if (!hasSearchedGames || !query) {
        return;
      }

      try {
        setIsSearchingGames(true);
        setHomeSearchError("");
        const data = await JeuxVideoApi.searchGamesByName(query);
        setHomeSearchResults(Array.isArray(data.items) ? data.items : []);
      } catch (e) {
        setHomeSearchError("Impossible de rechercher dans la collection.");
        setHomeSearchResults([]);
      } finally {
        setIsSearchingGames(false);
      }
    };

    refreshHomeSearchResults();
  }, [actionPermissions.isAuthenticated]);

  useEffect(() => {
    /** Charge les suggestions du formulaire. @param {void} Aucun. @returns {Promise<void>} Met a jour les valeurs. */
    const fetchAddGameColumnValues = async () => {
      if (!hasAccessToken || currentView !== "addGame") {
        setAddGameColumnValues({});
        return;
      }

      try {
        const data = await AddGameChoicesApi.fetchChoices(gameForm.platform);
        setAddGameColumnValues(data.values_by_column || {});
      } catch (e) {
        setAddGameColumnValues({});
      }
    };

    fetchAddGameColumnValues();
  }, [currentView, gameForm.platform, odsReloadKey, hasAccessToken]);

  useEffect(() => {
    if (hasAccessToken || currentView === "about" || currentView === "auth") {
      return;
    }
    setCurrentView("about");
    window.history.replaceState({}, "", "/about");
  }, [currentView, hasAccessToken]);

  useEffect(() => {
    if (!hasAccessToken || currentView !== "home" || window.location.pathname !== "/") {
      return;
    }
    window.history.replaceState({}, "", "/accueil");
  }, [currentView, hasAccessToken]);

  useEffect(() => {
    if (hasAccessToken || currentView !== "about" || AppRouting.isPublicPath(window.location.pathname)) {
      return;
    }
    window.history.replaceState({}, "", "/about");
  }, [currentView, hasAccessToken]);

  /** Soumet un nouveau jeu. @param {React.FormEvent<HTMLFormElement>} event - Soumission. @returns {Promise<void>} Recharge la vue. */
  const submitNewGame = async (event) => {
    event.preventDefault();
    setAddGameMessage("");
    setAddGameError("");
    const isWishlistTarget = gameForm.addTarget === "wishlist";
    if (isWishlistTarget && !actionPermissions.canAddWishlistGame) return;
    if (!isWishlistTarget && !actionPermissions.canAddGame) return;

    try {
      setIsAddingGame(true);
      const data = isWishlistTarget ? await WishlistAddApi.addWishlistGame(gameForm) : await JeuxVideoApi.addGame(gameForm);
      setAddGameMessage(
        isWishlistTarget ? "Jeu ajoute a la liste de souhaits." : "Jeu ajoute avec succes."
      );
      setGameForm({
        ...initialGameForm,
        platform: gameForm.platform,
        addTarget: gameForm.addTarget,
      });
      reloadOds();
      reloadGames();
      if (isWishlistTarget) {
        openWishlist();
      } else {
        openPlatform(data.item.Plateforme);
      }
    } catch (e) {
      setAddGameError(e.message || "Impossible d'ajouter le jeu.");
    } finally {
      setIsAddingGame(false);
    }
  };

  /**
   * Ajoute un jeu de la wishlist dans l'onglet de sa plateforme cible.
   *
   * @param {Object} gamePayload - Donnees nettoyees a envoyer au backend.
   * @returns {Promise<Object>} Donnees retournees par l'API d'ajout.
   */
  const addWishlistGameToPlatform = async (gamePayload) => {
    const data = await JeuxVideoApi.addGame(gamePayload);
    reloadOds();
    reloadGames();
    return data;
  };

  /**
   * Supprime un jeu de la liste de souhaits puis recharge la vue courante.
   *
   * @param {Object} game - Jeu wishlist a supprimer.
   * @returns {Promise<Object>} Donnees retournees par l'API de suppression.
   */
  const deleteWishlistGame = async (game) => {
    const data = await JeuxVideoApi.deleteWishlistGame(game);
    reloadOds();
    reloadGames();
    return data;
  };

  /**
   * Reinitialise le cache ODS backend puis recharge les donnees de l'interface.
   *
   * @param {void} Aucun - Appelle l'endpoint de reset du cache.
   * @returns {Promise<void>} Met a jour les messages, les compteurs de rechargement et les erreurs.
   */
  const resetOdsCache = async () => {
    setCacheResetMessage("");
    setCacheResetError("");

    try {
      setIsResettingCache(true);
      await JeuxVideoApi.resetCache();

      setCacheResetMessage("Cache reinitialise. Donnees rechargees.");
      reloadOds();
      reloadGames();
    } catch (e) {
      setCacheResetError(e.message || "Impossible de reinitialiser le cache.");
    } finally {
      setIsResettingCache(false);
    }
  };

  /**
   * Recherche un jeu par nom depuis la page d'accueil.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission du formulaire.
   * @returns {Promise<void>} Met a jour les resultats et erreurs de recherche.
   */
  const searchGamesByName = async (event) => {
    event.preventDefault();
    const query = homeSearchQuery.trim();
    setHasSearchedGames(true);

    if (!query) {
      setHomeSearchResults([]);
      setHomeSearchError("");
      return;
    }

    try {
      setIsSearchingGames(true);
      setHomeSearchError("");
      const data = await JeuxVideoApi.searchGamesByName(query);
      setHomeSearchResults(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setHomeSearchError("Impossible de rechercher dans la collection.");
      setHomeSearchResults([]);
    } finally {
      setIsSearchingGames(false);
    }
  };

  return (
    <AppFrame>
      {AppViewSwitch.render({
        currentView, homeStats, platforms, selectedPlatform, error, isLoadingHome, isSearchingGames, hasSearchedGames,
        homeSearchQuery, homeSearchResults, homeSearchError, cacheResetMessage, cacheResetError, isResettingCache,
        gameForm, addGameColumnValues, addGameError, addGameMessage, isAddingGame, namedGames, columns,
        valuesByColumn, columnFilters, sortConfig, sortedGames, filteredGames, isLoadingGames, isLoadingPlatforms,
        actionPermissions, authenticatedUsername, selectedPlatformStats, studioCount: getStudioCount(namedGames),
        isSavingGame: gameMutations.isSavingGame, editingGame: gameMutations.editingGame, editingWishlistGame: wishlistMutations.editingWishlistGame,
        isSavingWishlistGame: wishlistMutations.isSavingWishlistGame,
        deleteGameMessage: gameMutations.deleteGameMessage, deleteGameError: gameMutations.deleteGameError,
        downloadError: odsDownload.downloadError, isDownloadingOds: odsDownload.isDownloadingOds,
        openAddGamePage, openAdminDashboard, openAbout, openWishlist, openPlatform, setHomeSearchQuery,
        logout: AuthApi.confirmAndClearAccessToken, searchGamesByName, closeHomeSearch,
        resetOdsCache, downloadOdsFile: odsDownload.downloadOdsFile, goHome, submitNewGame,
        updateGameFormValue, addWishlistGameToPlatform, deleteWishlistGame, toggleSort, setColumnFilters,
        openEditGame: gameMutations.openEditGame, saveEditedGame: gameMutations.saveEditedGame, cancelEditGame: gameMutations.cancelEditGame,
        openEditWishlistGame: wishlistMutations.openEditWishlistGame, saveEditedWishlistGame: wishlistMutations.saveEditedWishlistGame,
        cancelEditWishlistGame: wishlistMutations.cancelEditWishlistGame, deletePlatformGame: gameMutations.deletePlatformGame,
      })}
      <AuthSessionModal isOpen={authSessionModal.isOpen} onAuthenticated={authSessionModal.markAuthenticated} onClose={authSessionModal.close} />
    </AppFrame>
  );
}

export default App;
