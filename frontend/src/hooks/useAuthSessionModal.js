/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook de pilotage global de la modale de session expiree.
 */
import { useEffect, useState } from "react";
import AuthApi from "../services/AuthApi";

/**
 * Gere l'ouverture de la modale de reconnexion sur expiration du token.
 *
 * @param {void} Aucun - Ecoute les evenements globaux d'authentification.
 * @returns {Object} Etat et callbacks de la modale de session.
 */
function useAuthSessionModal() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    /**
     * Affiche la modale globale quand le backend refuse un token expire.
     *
     * @param {void} Aucun - Reagit a l'evenement du service API.
     * @returns {void} Ouvre la modale de reconnexion.
     */
    const openExpiredSessionModal = () => {
      setIsOpen(true);
    };

    window.addEventListener(AuthApi.sessionExpiredEventName, openExpiredSessionModal);
    return () => window.removeEventListener(
      AuthApi.sessionExpiredEventName,
      openExpiredSessionModal
    );
  }, []);

  useEffect(() => {
    /**
     * Programme l'ouverture automatique de la modale a l'expiration du token.
     *
     * @param {void} Aucun - Utilise l'expiration stockee par le service API.
     * @returns {number|null} Identifiant de timer ou `null`.
     */
    const scheduleSessionExpiration = () => {
      const accessToken = AuthApi.getAccessToken();
      if (!accessToken) {
        return null;
      }

      const timeToLiveMs = AuthApi.getAccessTokenTimeToLiveMs();
      if (timeToLiveMs <= 0) {
        AuthApi.handleExpiredSession();
        return null;
      }

      return window.setTimeout(() => {
        AuthApi.handleExpiredSession();
      }, timeToLiveMs);
    };

    let expirationTimer = scheduleSessionExpiration();
    const resetSessionExpirationTimer = () => {
      if (expirationTimer) {
        window.clearTimeout(expirationTimer);
      }
      expirationTimer = scheduleSessionExpiration();
    };

    window.addEventListener(AuthApi.authChangeEventName, resetSessionExpirationTimer);
    return () => {
      if (expirationTimer) {
        window.clearTimeout(expirationTimer);
      }
      window.removeEventListener(AuthApi.authChangeEventName, resetSessionExpirationTimer);
    };
  }, []);

  return {
    isOpen,
    close: () => setIsOpen(false),
    markAuthenticated: () => setIsOpen(false),
  };
}

export default useAuthSessionModal;
