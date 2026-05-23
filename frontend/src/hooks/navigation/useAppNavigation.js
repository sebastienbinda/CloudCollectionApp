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

/**
 * Gere la vue courante, la plateforme selectionnee et l'historique navigateur.
 *
 * @param {Object} options - Dependances de navigation injectees par l'application.
 * @returns {Object} Etat et callbacks de navigation.
 */
function useAppNavigation(options) {
  const [currentView, setCurrentView] = useState(AppRouting.getViewFromUrl);
  const [selectedPlatform, setSelectedPlatform] = useState(() =>
    AppRouting.getViewFromUrl() === "wishlist"
      ? AppRouting.wishlistSheetName
      : AppRouting.getPlatformFromUrl()
  );

  const updatePlatformUrl = (platform) => {
    const url = new URL(window.location.href);
    url.pathname = "/";
    if (platform) url.searchParams.set("platform", platform);
    else url.searchParams.delete("platform");
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  const openView = (view, path) => {
    options.clearDeleteGameFeedback();
    setCurrentView(view);
    window.history.pushState({}, "", path);
  };

  const openAddGamePage = () => {
    options.clearDeleteGameFeedback();
    options.prepareAddGameForm(selectedPlatform);
    setCurrentView("addGame");
    window.history.pushState({}, "", "/add-game");
  };

  const openPlatform = (platform) => {
    options.clearDeleteGameFeedback();
    setSelectedPlatform(platform);
    setCurrentView("games");
    updatePlatformUrl(platform);
  };

  const openWishlist = () => {
    options.clearDeleteGameFeedback();
    setSelectedPlatform(AppRouting.wishlistSheetName);
    setCurrentView("wishlist");
    window.history.pushState({}, "", "/wishlist");
  };

  useEffect(() => {
    const handlePopState = () => {
      options.clearDeleteGameFeedback();
      const pathname = window.location.pathname;
      const mappedView = {
        "/about": "about",
        "/auth": "auth",
        "/accueil": "home",
        "/add-game": "addGame",
        "/admin-dashboard": "adminDashboard",
        "/users": "users",
      }[pathname];

      if (mappedView) {
        setCurrentView(mappedView);
        return;
      }
      if (!AppRouting.hasStoredAccessToken()) {
        setSelectedPlatform("");
        setCurrentView("about");
        window.history.replaceState({}, "", "/about");
        return;
      }
      if (pathname === "/wishlist") {
        setSelectedPlatform(AppRouting.wishlistSheetName);
        setCurrentView("wishlist");
        return;
      }
      const platformFromUrl = AppRouting.getPlatformFromUrl();
      setCurrentView(platformFromUrl ? "games" : "home");
      if (platformFromUrl) setSelectedPlatform(platformFromUrl);
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (options.hasAccessToken || currentView === "about" || currentView === "auth") return;
    setCurrentView("about");
    window.history.replaceState({}, "", "/about");
  }, [currentView, options.hasAccessToken]);

  useEffect(() => {
    if (currentView !== "users" || options.authenticatedProfile === "ADMIN") return;
    setCurrentView("home");
    window.history.replaceState({}, "", "/accueil");
  }, [options.authenticatedProfile, currentView]);

  useEffect(() => {
    if (!options.hasAccessToken || currentView !== "home" || window.location.pathname !== "/") return;
    window.history.replaceState({}, "", "/accueil");
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
    goHome: () => openView("home", "/accueil"),
    openAbout: () => openView("about", "/about"),
    openAddGamePage,
    openAdminDashboard: () => openView("adminDashboard", "/admin-dashboard"),
    openUsersPage: () => openView("users", "/users"),
    openPlatform,
    openWishlist,
  };
}

export default useAppNavigation;
