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
 * Description : hook React de session applicative et droits backend.
 */
import { useEffect, useState } from "react";
import AuthApi from "../../services/AuthApi";
import VideoGamesApi from "../../services/VideoGamesApi";
import useAuthSessionModal from "../useAuthSessionModal";
import useBackendActionPermissions from "../useBackendActionPermissions";
import GuestSessionViewPolicy from "../../services/GuestSessionViewPolicy";

/**
 * Lit l'identite authentifiee stockee cote navigateur.
 *
 * @returns {Object} Etat local de session avec presence, nom et profil.
 */
function getLocalAuthenticatedIdentity() {
  const localAccessToken = AuthApi.getUsableAccessToken();
  const hasLocalAccessToken = Boolean(localAccessToken);
  const payload = hasLocalAccessToken ? AuthApi.getAccessTokenPayload() : {};
  const defaultUsername = hasLocalAccessToken ? AuthApi.getAuthenticatedUsername() : "";
  const viewAccess = new GuestSessionViewPolicy(payload).toViewModel(defaultUsername);
  return {
    isAuthenticated: hasLocalAccessToken,
    username: hasLocalAccessToken ? viewAccess.identityLabel : "",
    profile: hasLocalAccessToken ? VideoGamesApi.getAuthenticatedProfile() : "",
    viewAccess,
  };
}

/**
 * Centralise la session frontend, les droits backend et la modale d'authentification.
 *
 * @returns {Object} Etat de session, droits d'action et proprietes de modale.
 */
function useSessionState() {
  const [authenticatedIdentity, setAuthenticatedIdentity] = useState(getLocalAuthenticatedIdentity);
  const actionPermissions = useBackendActionPermissions();
  const authSessionModal = useAuthSessionModal();

  useEffect(() => {
    const updateAuthenticatedIdentity = () => {
      setAuthenticatedIdentity(getLocalAuthenticatedIdentity());
    };

    window.addEventListener(AuthApi.authChangeEventName, updateAuthenticatedIdentity);
    updateAuthenticatedIdentity();
    return () => window.removeEventListener(AuthApi.authChangeEventName, updateAuthenticatedIdentity);
  }, []);

  const hasAccessToken = Boolean(AuthApi.getUsableAccessToken());
  return {
    actionPermissions,
    hasAccessToken,
    authenticatedUsername: authenticatedIdentity.isAuthenticated ? authenticatedIdentity.username : "",
    authenticatedProfile: authenticatedIdentity.isAuthenticated ? authenticatedIdentity.profile : "",
    viewAccess: authenticatedIdentity.viewAccess,
    logout: AuthApi.confirmAndClearAccessToken,
    authModalProps: {
      isOpen: authSessionModal.isOpen,
      onAuthenticated: authSessionModal.markAuthenticated,
      onClose: authSessionModal.close,
    },
  };
}

export default useSessionState;
