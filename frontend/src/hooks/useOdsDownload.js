/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-06
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook objet de telechargement du fichier ODS protege.
 */
import { useState } from "react";
import AuthApi from "../services/AuthApi";
import VideoGamesApi from "../services/VideoGamesApi";

/**
 * Gere le telechargement du fichier ODS depuis le frontend.
 *
 * @returns {Object} Etat et action de telechargement ODS.
 */
function useOdsDownload() {
  const [downloadError, setDownloadError] = useState("");
  const [isDownloadingOds, setIsDownloadingOds] = useState(false);

  /**
   * Lance le telechargement du fichier ODS.
   *
   * @param {void} Aucun - Appelle l'API backend protegee.
   * @returns {Promise<void>} Declenche le telechargement navigateur.
   */
  const downloadOdsFile = async () => {
    setDownloadError("");
    try {
      setIsDownloadingOds(true);
      await VideoGamesApi.downloadOdsFile();
    } catch (error) {
      if (AuthApi.isSessionExpiredError(error)) {
        return;
      }
      setDownloadError(error.message || "Impossible de telecharger le fichier de collection.");
    } finally {
      setIsDownloadingOds(false);
    }
  };

  return { downloadError, isDownloadingOds, downloadOdsFile };
}

export default useOdsDownload;
