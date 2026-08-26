/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : effets React de navigation pour l'onboarding d'import utilisateur.
 */
import { useEffect } from "react";

/**
 * Branche les effets de session et de redirection de l'onboarding d'import.
 *
 * @param {Object} options - Etat de session, navigation et callbacks.
 * @returns {void} Ne retourne aucune valeur.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function useUserCollectionOnboardingEffects(options) {
  const {
    authenticatedUsername,
    canUseCollectionViews,
    checkedUsername,
    currentView,
    hasAccessToken,
    hasCollection,
    openCollectionOnboarding,
    openOnboardingWhenCollectionIsMissing,
    resetOnboardingState,
    selectedGameSource,
  } = options;

  useEffect(() => {
    if (hasAccessToken) {
      return;
    }
    resetOnboardingState();
  }, [hasAccessToken, resetOnboardingState]);

  useEffect(() => {
    if (!hasAccessToken || !authenticatedUsername || !canUseCollectionViews) {
      return;
    }
    if (currentView === "gameDetail" && selectedGameSource === "library") {
      return;
    }
    if ([
      "about",
      "feedback",
      "auth",
      "library",
      "libraryPlatforms",
      "libraryStudios",
      "libraryGames",
    ].includes(currentView)) {
      return;
    }
    if (checkedUsername === authenticatedUsername) {
      if (hasCollection === false && currentView !== "collectionOnboarding") {
        openCollectionOnboarding();
      }
      return;
    }

    openOnboardingWhenCollectionIsMissing().catch(() => {});
  }, [
    checkedUsername,
    authenticatedUsername,
    currentView,
    hasCollection,
    hasAccessToken,
    canUseCollectionViews,
    openCollectionOnboarding,
    openOnboardingWhenCollectionIsMissing,
    selectedGameSource,
  ]);
}

export default useUserCollectionOnboardingEffects;
