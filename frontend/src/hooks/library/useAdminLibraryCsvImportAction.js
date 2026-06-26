/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : hook dedie a l'import CSV admin Bibliotheque.
 */
import { useState } from "react";
import LibraryAdminApi from "../../services/LibraryAdminApi";

/**
 * Orchestre l'import CSV admin dans la Bibliotheque globale.
 *
 * @returns {Object} Etat et callbacks exposes a la page Configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function useAdminLibraryCsvImportAction() {
  const [selectedAdminLibraryImportFile, setSelectedAdminLibraryImportFile] = useState(null);
  const [adminLibraryImportResult, setAdminLibraryImportResult] = useState(null);
  const [adminLibraryImportError, setAdminLibraryImportError] = useState("");
  const [isImportingAdminLibrary, setIsImportingAdminLibrary] = useState(false);

  /**
   * Memorise le fichier CSV choisi par l'administrateur.
   *
   * @param {File|null} file - Fichier CSV selectionne ou absence.
   * @returns {void} Met a jour l'etat local.
   * @throws {void} Ne leve pas d'exception.
   */
  const selectAdminLibraryImportFile = (file) => {
    setSelectedAdminLibraryImportFile(file || null);
    setAdminLibraryImportResult(null);
    setAdminLibraryImportError("");
  };

  /**
   * Envoie le CSV admin au backend apres confirmation utilisateur.
   *
   * @returns {Promise<void>} Met a jour les messages de resultat.
   * @throws {void} Les erreurs sont converties en message lisible.
   */
  const importAdminLibraryCsv = async () => {
    setAdminLibraryImportResult(null);
    setAdminLibraryImportError("");
    if (!selectedAdminLibraryImportFile) {
      setAdminLibraryImportError("Selectionnez un fichier CSV.");
      return;
    }

    try {
      setIsImportingAdminLibrary(true);
      const result = await LibraryAdminApi.importLibraryCsv(selectedAdminLibraryImportFile);
      setAdminLibraryImportResult(result);
      setSelectedAdminLibraryImportFile(null);
    } catch (error) {
      setAdminLibraryImportError(
        error.message || "Impossible d'importer le CSV dans la Bibliotheque."
      );
    } finally {
      setIsImportingAdminLibrary(false);
    }
  };

  return {
    adminLibraryImportError,
    adminLibraryImportResult,
    importAdminLibraryCsv,
    isImportingAdminLibrary,
    selectedAdminLibraryImportFileName: selectedAdminLibraryImportFile?.name || "",
    selectAdminLibraryImportFile,
  };
}

export default useAdminLibraryCsvImportAction;
