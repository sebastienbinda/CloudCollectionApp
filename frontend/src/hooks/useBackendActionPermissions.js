/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-05
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook chargeant les permissions d'actions depuis les routes backend.
 */
import { useEffect, useState } from "react";
import AuthApi from "../services/AuthApi";
import BackendRouteAccessService from "../services/BackendRouteAccessService";
import JeuxVideoApi from "../services/JeuxVideoApi";

/**
 * Charge les permissions applicatives exposees par le backend.
 *
 * @param {void} Aucun - Utilise le client API des jeux video.
 * @returns {Object} Permissions booleennes par action frontend.
 */
function useBackendActionPermissions() {
  const [actionPermissions, setActionPermissions] = useState(
    BackendRouteAccessService.getDefaultActionPermissions
  );

  useEffect(() => {
    const fetchBackendRoutes = async () => {
      try {
        const permissions = await BackendRouteAccessService.loadActionPermissions(JeuxVideoApi);
        setActionPermissions(permissions);
      } catch (e) {
        setActionPermissions(BackendRouteAccessService.getDefaultActionPermissions());
      }
    };

    fetchBackendRoutes();
    window.addEventListener(AuthApi.authChangeEventName, fetchBackendRoutes);
    return () => window.removeEventListener(AuthApi.authChangeEventName, fetchBackendRoutes);
  }, []);

  return actionPermissions;
}

export default useBackendActionPermissions;
