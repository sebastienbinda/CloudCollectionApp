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
 * Description : vue d'onboarding pour importer la collection utilisateur initiale.
 */
import ImportConfigurationFields from "./ImportConfigurationFields";
import ImportSummary from "./ImportSummary";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche le parcours initial d'import de collection.
 *
 * @param {Object} props - Etat d'import, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue d'onboarding d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function UserCollectionOnboardingView({
  authenticatedUsername,
  authenticatedProfile,
  selectedCollectionFileName,
  availableImportSheets,
  hasAnalyzedImportFile,
  importResult,
  importConfiguration,
  onboardingError,
  isCheckingCollection,
  isAnalyzingCollection,
  isImportingCollection,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onFileChange,
  onConfigurationChange,
  onLayoutChange,
  onLayoutColumnChange,
  onSheetChange,
  onSheetLayoutChange,
  onSheetColumnChange,
  onWishlistConfigurationChange,
  onWishlistLayoutChange,
  onWishlistLayoutColumnChange,
  onCsvMappingChange,
  onAddSheet,
  onRemoveSheet,
  onSubmitImport,
}) {
  const isBusy = isCheckingCollection || isAnalyzingCollection || isImportingCollection;

  /**
   * Transmet le fichier selectionne au hook d'orchestration.
   *
   * @param {React.ChangeEvent<HTMLInputElement>} event - Evenement de selection fichier.
   * @returns {void} Met a jour le fichier selectionne.
   */
  const handleFileChange = (event) => {
    onFileChange(event.target.files?.[0] || null);
  };

  /**
   * Soumet le fichier selectionne au hook d'orchestration.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission du formulaire.
   * @returns {void} Lance l'import asynchrone.
   */
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmitImport();
  };

  return (
    <PageLayout
      shellClassName="appShell collectionOnboardingShell"
      eyebrow="Premiere collection"
      title="Importer votre collection"
      subtitle="Ajoutez votre collection pour initialiser vos plateformes, studios et jeux."
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <section className="collectionOnboardingContent" aria-label="Import de collection">
        <div className="collectionOnboardingSteps" aria-label="Parcours d'import">
          <article>
            <span>1</span>
            <h2>Selectionner</h2>
            <p>Choisissez le fichier qui contient votre collection.</p>
          </article>
          <article>
            <span>2</span>
            <h2>Importer</h2>
            <p>L'import cree les elements manquants et associe les jeux a votre compte.</p>
          </article>
          <article>
            <span>3</span>
            <h2>Consulter</h2>
            <p>Apres succes, ouvrez Ma collection depuis le resume.</p>
          </article>
        </div>

        {importResult ? (
          <ImportSummary result={importResult} onAction={onOpenHome} />
        ) : (
          <form className="collectionImportForm" onSubmit={handleSubmit}>
          <label>
            Type de fichier
            <select
              value={importConfiguration.fileType}
              disabled={isBusy || Boolean(selectedCollectionFileName)}
              onChange={(event) => onConfigurationChange("fileType", event.target.value)}
            >
              <option value="libreoffice_ods">LibreOffice ODS</option>
              <option value="excel_xlsx">Excel XLSX</option>
              <option value="csv">CSV</option>
            </select>
          </label>
          <label>
            Fichier de collection
            <input
              type="file"
              accept=".ods,.xlsx,.csv"
              onChange={handleFileChange}
              disabled={isBusy}
            />
          </label>
          {selectedCollectionFileName ? (
            <p className="collectionSelectedFile">{selectedCollectionFileName}</p>
          ) : null}
          {hasAnalyzedImportFile ? (
            <ImportConfigurationFields
              configuration={importConfiguration}
              availableSheetNames={availableImportSheets}
              disabled={isBusy}
              onConfigurationChange={onConfigurationChange}
              onLayoutChange={onLayoutChange}
              onLayoutColumnChange={onLayoutColumnChange}
              onSheetChange={onSheetChange}
              onSheetLayoutChange={onSheetLayoutChange}
              onSheetColumnChange={onSheetColumnChange}
              onWishlistConfigurationChange={onWishlistConfigurationChange}
              onWishlistLayoutChange={onWishlistLayoutChange}
              onWishlistLayoutColumnChange={onWishlistLayoutColumnChange}
              onCsvMappingChange={onCsvMappingChange}
              onAddSheet={onAddSheet}
              onRemoveSheet={onRemoveSheet}
            />
          ) : null}
          {onboardingError ? <p className="error">{onboardingError}</p> : null}
          {isCheckingCollection ? <ProgressBar label="Verification de votre collection" /> : null}
          {isAnalyzingCollection ? <ProgressBar label="Analyse de votre fichier" /> : null}
          {isImportingCollection ? <ProgressBar label="Import de votre collection" /> : null}
          <div className="formActions">
            <button type="submit" disabled={isBusy || !selectedCollectionFileName || !hasAnalyzedImportFile}>
              {isImportingCollection ? "Import..." : "Importer"}
            </button>
          </div>
          </form>
        )}
      </section>
    </PageLayout>
  );
}

export default UserCollectionOnboardingView;
