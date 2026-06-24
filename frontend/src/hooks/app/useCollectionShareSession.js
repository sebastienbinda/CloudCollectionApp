/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : orchestration frontend de l'activation d'une session GUEST.
 */
import { useLayoutEffect, useRef } from "react";
import AppRouting from "../../appRouting";
import AuthApi from "../../services/AuthApi";
import CollectionShareSessionApi from "../../services/CollectionShareSessionApi";

const INVALID_SHARE_MESSAGE = "Le lien de partage est invalide ou n'est plus disponible.";
const UNAVAILABLE_SHARE_MESSAGE = "Ce partage a expire ou a ete revoque.";

/**
 * Active une session GUEST depuis la route publique transitoire.
 *
 * @param {Object} options - Navigation et message applicatif injectes.
 * @returns {void} Le hook ne retourne aucune valeur.
 * @throws {void} Les erreurs d'echange sont converties en message About.
 */
function useCollectionShareSession(options) {
  const shareTokenRef = useRef(AppRouting.getCollectionShareTokenFromUrl());
  const hasStartedExchangeRef = useRef(false);

  useLayoutEffect(() => {
    const shareToken = shareTokenRef.current;
    if (!shareToken || hasStartedExchangeRef.current) {
      return;
    }
    hasStartedExchangeRef.current = true;

    const activateGuestSession = async () => {
      AuthApi.clearAccessToken();
      options.setError("");
      options.setCurrentView("about");
      window.history.replaceState({}, "", "/about");
      try {
        const session = await CollectionShareSessionApi.exchangeShareToken(shareToken);
        AuthApi.storeAccessToken(session.access_token, session.expires_in || null);
        const destination = CollectionShareSessionApi.resolveGuestDestination(
          AuthApi.getAccessTokenPayload()
        );
        if (!destination) {
          AuthApi.clearAccessToken();
          throw new Error(INVALID_SHARE_MESSAGE);
        }
        options.setCurrentView(destination.view);
        window.history.replaceState({}, "", destination.path);
      } catch (error) {
        AuthApi.clearAccessToken();
        options.setError(error?.status === 411 ? UNAVAILABLE_SHARE_MESSAGE : INVALID_SHARE_MESSAGE);
        options.setCurrentView("about");
        window.history.replaceState({}, "", "/about");
      }
    };

    activateGuestSession();
  }, [options]);
}

export { INVALID_SHARE_MESSAGE, UNAVAILABLE_SHARE_MESSAGE };
export default useCollectionShareSession;
