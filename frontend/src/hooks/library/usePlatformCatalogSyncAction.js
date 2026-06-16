/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-16
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook dedie a la synchronisation admin du catalogue plateformes.
 */
import { useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

/**
 * Orchestre l'action frontend de synchronisation du catalogue plateformes.
 *
 * @returns {Object} Etat et callback exposes a la page Configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function usePlatformCatalogSyncAction() {
  const [platformCatalogSyncMessage, setPlatformCatalogSyncMessage] = useState("");
  const [platformCatalogSyncError, setPlatformCatalogSyncError] = useState("");
  const [isSyncingPlatformCatalog, setIsSyncingPlatformCatalog] = useState(false);

  /**
   * Demande confirmation puis appelle le backend de synchronisation catalogue.
   *
   * @returns {Promise<void>} Met a jour les messages de resultat.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const syncPlatformCatalog = async () => {
    setPlatformCatalogSyncMessage("");
    setPlatformCatalogSyncError("");
    const confirmed = window.confirm(
      "Mettre a jour les plateformes et alias manquants depuis les CSV backend ?"
    );
    if (!confirmed) {
      return;
    }

    try {
      setIsSyncingPlatformCatalog(true);
      const result = await LibraryAdminApi.syncPlatformCatalog();
      setPlatformCatalogSyncMessage(buildSuccessMessage(result));
    } catch (error) {
      setPlatformCatalogSyncError(
        error.message || "Impossible de mettre a jour le catalogue plateformes."
      );
    } finally {
      setIsSyncingPlatformCatalog(false);
    }
  };

  return {
    isSyncingPlatformCatalog,
    platformCatalogSyncError,
    platformCatalogSyncMessage,
    syncPlatformCatalog,
  };
}

/**
 * Construit le message de succes depuis les compteurs backend.
 *
 * @param {Object} result - Compteurs retournes par l'API.
 * @returns {string} Message lisible par l'interface.
 * @throws {void} Ne leve pas d'exception.
 */
function buildSuccessMessage(result = {}) {
  const insertedPlatforms = Number(result.inserted_platforms || 0);
  const insertedAliases = Number(result.inserted_aliases || 0);
  const totalInserted = Number(result.total_inserted || 0);
  if (totalInserted === 0) {
    return "Catalogue plateformes deja a jour.";
  }
  return (
    `Catalogue plateformes mis a jour : ${insertedPlatforms} plateforme(s), ` +
    `${insertedAliases} alias ajoute(s).`
  );
}

export default usePlatformCatalogSyncAction;
