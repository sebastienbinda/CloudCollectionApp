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
 * Description : hook React de navigation et synchronisation URL.
 */
import { useEffect, useState } from "react";
import AppRouting from "../../appRouting";
import AuthApi from "../../services/AuthApi";

/**
 * Gere la vue courante, la plateforme selectionnee et l'historique navigateur.
 *
 * @param {Object} options - Dependances de navigation injectees par l'application.
 * @returns {Object} Etat et callbacks de navigation.
 */
function useAppNavigation(options) {
  const [currentView, setCurrentView] = useState(AppRouting.getViewFromUrl);
  const [selectedPlatform, setSelectedPlatform] = useState(() =>
    AppRouting.getPlatformIdFromUrl()
  );
  const [selectedLibraryPlatformId, setSelectedLibraryPlatformId] = useState(() =>
    AppRouting.getLibraryPlatformDetailIdFromUrl()
  );
  const [selectedGameId, setSelectedGameId] = useState(() => AppRouting.getGameIdFromUrl());
  const [selectedGameSource, setSelectedGameSource] = useState(() =>
    AppRouting.getGameDetailSourceFromUrl()
  );

  const updatePlatformUrl = (platformId) => {
    const url = new URL(window.location.href);
    url.pathname = "/";
    url.searchParams.delete("platform");
    if (platformId) url.searchParams.set("platform_id", platformId);
    else url.searchParams.delete("platform_id");
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  const openView = (view, path) => {
    options.clearDeleteGameFeedback();
    if (view !== "gameDetail") {
      setSelectedGameId("");
    }
    if (view !== "libraryPlatformDetail") {
      setSelectedLibraryPlatformId("");
    }
    setCurrentView(view);
    window.history.pushState({}, "", path);
  };

  const openAddGamePage = () => {
    if (!options.canUseCollectionViews) {
      openView("configuration", "/configuration");
      return;
    }
    options.clearDeleteGameFeedback();
    options.prepareAddGameForm(selectedPlatform);
    setCurrentView("addGame");
    window.history.pushState({}, "", "/add-game");
  };

  const openPlatform = (platform) => {
    if (!options.canUseCollectionViews) {
      openView("configuration", "/configuration");
      return;
    }
    const platformId = typeof platform === "object" && platform !== null ? platform.id : platform;
    options.clearDeleteGameFeedback();
    setSelectedPlatform(String(platformId || ""));
    setCurrentView("games");
    updatePlatformUrl(platformId);
  };

  const openGameDetail = (game, source = "library") => {
    const gameId = typeof game === "object" && game !== null ? game.id : game;
    if (!gameId) {
      return;
    }
    const resolvedSource = source === "collection" ? "collection" : "library";
    if (resolvedSource === "collection" && !options.canUseCollectionViews) {
      openView("configuration", "/configuration");
      return;
    }
    options.clearDeleteGameFeedback();
    setSelectedGameId(String(gameId));
    setSelectedLibraryPlatformId("");
    setSelectedGameSource(resolvedSource);
    setCurrentView("gameDetail");
    const path = resolvedSource === "collection"
      ? `/collection/jeux/${encodeURIComponent(gameId)}`
      : `/bibliotheque/jeux/${encodeURIComponent(gameId)}`;
    window.history.pushState({}, "", path);
  };

  const openLibraryPlatformDetail = (platform) => {
    const platformId = typeof platform === "object" && platform !== null ? platform.id : platform;
    if (!platformId) {
      return;
    }
    options.clearDeleteGameFeedback();
    setSelectedGameId("");
    setSelectedLibraryPlatformId(String(platformId));
    setCurrentView("libraryPlatformDetail");
    window.history.pushState({}, "", `/bibliotheque/plateformes/${encodeURIComponent(platformId)}`);
  };

  useEffect(() => {
    const handleGuestShareUnavailable = () => {
      options.clearDeleteGameFeedback();
      options.setGlobalError("Ce partage a expire ou a ete revoque.");
      setSelectedPlatform("");
      setSelectedGameId("");
      setSelectedGameSource("library");
      setCurrentView("about");
      window.history.replaceState({}, "", "/about");
    };

    window.addEventListener(AuthApi.guestShareUnavailableEventName, handleGuestShareUnavailable);
    return () => window.removeEventListener(
      AuthApi.guestShareUnavailableEventName,
      handleGuestShareUnavailable
    );
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      options.clearDeleteGameFeedback();
      const pathname = window.location.pathname;
      if (/^\/bibliotheque\/plateformes\/\d+$/.test(pathname)) {
        setSelectedLibraryPlatformId(AppRouting.getLibraryPlatformDetailIdFromUrl());
        setSelectedGameId("");
        setCurrentView("libraryPlatformDetail");
        return;
      }
      if (/^\/bibliotheque\/jeux\/\d+$/.test(pathname)) {
        setSelectedGameId(AppRouting.getGameIdFromUrl());
        setSelectedLibraryPlatformId("");
        setSelectedGameSource("library");
        setCurrentView("gameDetail");
        return;
      }
      if (/^\/collection\/jeux\/\d+$/.test(pathname)) {
        setSelectedGameId(AppRouting.getGameIdFromUrl());
        setSelectedLibraryPlatformId("");
        setSelectedGameSource("collection");
        setCurrentView("gameDetail");
        return;
      }
      const mappedView = {
        "/about": "about",
        "/auth": "auth",
        "/auth/verify-email": "emailVerificationResult",
        "/bibliotheque": "library",
        "/bibliotheque/plateformes": "libraryPlatforms",
        "/bibliotheque/studios": "libraryStudios",
        "/bibliotheque/jeux": "libraryGames",
        "/collection": "home",
        "/wishlist": "wishlist",
        "/add-game": "addGame",
        "/configuration": "configuration",
        "/configuration/images-plateformes": "platformImageModeration",
        "/users": "users",
        "/collection/import": "collectionOnboarding",
      }[pathname];

      if (mappedView) {
        setSelectedGameId("");
        setSelectedLibraryPlatformId("");
        setCurrentView(mappedView);
        return;
      }
      if (!AppRouting.hasStoredAccessToken()) {
        setSelectedPlatform("");
        setCurrentView("about");
        window.history.replaceState({}, "", "/about");
        return;
      }
      const platformIdFromUrl = AppRouting.getPlatformIdFromUrl();
      setCurrentView(platformIdFromUrl ? "games" : "home");
      if (platformIdFromUrl) setSelectedPlatform(platformIdFromUrl);
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (options.hasAccessToken || AppRouting.isPublicPath(window.location.pathname)) return;
    setCurrentView("about");
    window.history.replaceState({}, "", "/about");
  }, [currentView, options.hasAccessToken]);

  useEffect(() => {
    if (!["platformImageModeration", "users"].includes(currentView) || options.authenticatedProfile === "ADMIN") return;
    setCurrentView("home");
    window.history.replaceState({}, "", "/collection");
  }, [options.authenticatedProfile, currentView]);

  useEffect(() => {
    const collectionViews = ["home", "games", "wishlist", "addGame", "collectionOnboarding"];
    if (currentView === "gameDetail" && selectedGameSource === "collection" && !options.canUseCollectionViews) {
      const fallbackView = options.authenticatedProfile === "ADMIN" ? "configuration" : "about";
      const fallbackPath = options.authenticatedProfile === "ADMIN" ? "/configuration" : "/about";
      setSelectedGameId("");
      setSelectedGameSource("library");
      setCurrentView(fallbackView);
      window.history.replaceState({}, "", fallbackPath);
      return;
    }
    if (options.canUseCollectionViews || !collectionViews.includes(currentView)) return;
    const fallbackView = options.authenticatedProfile === "ADMIN" ? "configuration" : "about";
    const fallbackPath = options.authenticatedProfile === "ADMIN" ? "/configuration" : "/about";
    setSelectedPlatform("");
    setCurrentView(fallbackView);
    window.history.replaceState({}, "", fallbackPath);
  }, [currentView, options.authenticatedProfile, options.canUseCollectionViews, selectedGameSource]);

  useEffect(() => {
    if (!options.hasAccessToken || currentView !== "home" || window.location.pathname !== "/") return;
    window.history.replaceState({}, "", "/collection");
  }, [currentView, options.hasAccessToken]);

  useEffect(() => {
    if (options.hasAccessToken || currentView !== "about" || AppRouting.isPublicPath(window.location.pathname)) return;
    window.history.replaceState({}, "", "/about");
  }, [currentView, options.hasAccessToken]);

  return {
    currentView,
    setCurrentView,
    selectedPlatform,
    setSelectedPlatform,
    selectedLibraryPlatformId,
    selectedGameId,
    selectedGameSource,
    goHome: () => {
      if (!options.canUseCollectionViews) {
        openView("configuration", "/configuration");
        return;
      }
      openView("home", "/collection");
    },
    openVerifiedCollection: () => openView("home", "/collection"),
    openAbout: () => openView("about", "/about"),
    openAuth: () => openView("auth", "/auth"),
    openLibrary: () => openView("library", "/bibliotheque"),
    openLibraryPlatforms: () => openView("libraryPlatforms", "/bibliotheque/plateformes"),
    openLibraryStudios: () => openView("libraryStudios", "/bibliotheque/studios"),
    openLibraryGames: () => openView("libraryGames", "/bibliotheque/jeux"),
    openWishlist: () => {
      if (!options.canUseCollectionViews) {
        openView("configuration", "/configuration");
        return;
      }
      openView("wishlist", "/wishlist");
    },
    openAddGamePage,
    openConfiguration: () => openView("configuration", "/configuration"),
    openPlatformImageModeration: () => openView(
      "platformImageModeration",
      "/configuration/images-plateformes"
    ),
    openUsersPage: () => openView("users", "/users"),
    openCollectionOnboarding: () => {
      if (!options.canUseCollectionViews) {
        openView("configuration", "/configuration");
        return;
      }
      openView("collectionOnboarding", "/collection/import");
    },
    openPlatform,
    openGameDetail,
    openLibraryPlatformDetail,
  };
}

export default useAppNavigation;
