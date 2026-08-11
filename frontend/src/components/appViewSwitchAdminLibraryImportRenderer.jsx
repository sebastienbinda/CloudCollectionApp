/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : rendu dedie de la page d'import CSV admin Bibliotheque.
 */
import AdminLibraryImportView from "./AdminLibraryImportView";

/**
 * Rend la page dediee a l'import CSV admin Bibliotheque.
 *
 * @param {Object} props - Etat applicatif de l'import admin.
 * @param {Object} pageLayoutProps - Proprietes communes du layout applicatif.
 * @returns {import("react").JSX.Element} Vue d'import admin.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function renderAdminLibraryImportView(props, pageLayoutProps) {
  return (
    <AdminLibraryImportView
      {...pageLayoutProps}
      adminLibraryImportError={props.adminLibraryImportError}
      adminLibraryImportResult={props.adminLibraryImportResult}
      canImportLibraryCsv={props.actionPermissions.canImportLibraryCsv}
      isImportingAdminLibrary={props.isImportingAdminLibrary}
      selectedAdminLibraryImportFileName={props.selectedAdminLibraryImportFileName}
      onImportAdminLibraryCsv={props.importAdminLibraryCsv}
      onPrepareNewImportAfterRefusal={props.prepareNewAdminLibraryImportAfterRefusal}
      onSelectAdminLibraryImportFile={props.selectAdminLibraryImportFile}
    />
  );
}

export default renderAdminLibraryImportView;
