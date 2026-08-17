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
  const isImportRefused = Boolean(importResult?.refusal?.refused);

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
            <h2>Sélectionner</h2>
            <p>Choisissez le fichier qui contient votre collection.</p>
          </article>
          <article>
            <span>2</span>
            <h2>Configurer votre import</h2>
            <p>Indiquez ou se trouvent les colonnes obligatoires et optionnelles.</p>
          </article>
          <article>
            <span>3</span>
            <h2>Importer et consulter</h2>
            <p>L'import associe les jeux à votre compte, puis affiche un résumé.</p>
          </article>
        </div>

        {importResult ? (
          <ImportSummary
            actionLabel={isImportRefused ? "Corriger et reimporter" : "Ouvrir Ma collection"}
            result={importResult}
            contributionNotice={isImportRefused ? null : <UserImportContributionNotice />}
            onAction={isImportRefused ? () => onFileChange(null) : onOpenHome}
          />
        ) : (
          <form className="collectionImportForm" onSubmit={handleSubmit}>
            <section
              className="importFormStep"
              aria-label={selectedCollectionFileName ? "Fichier de collection sélectionné" : undefined}
              aria-labelledby={selectedCollectionFileName ? undefined : "import-file-step-title"}
            >
              {selectedCollectionFileName ? (
                <div className="collectionSelectedFile">
                  <span>{selectedCollectionFileName}</span>
                  <button
                    type="button"
                    className="secondaryButton collectionSelectedFileChange"
                    aria-label="Changer le fichier de collection"
                    title="Changer le fichier"
                    onClick={() => onFileChange(null)}
                    disabled={isBusy}
                  >
                    <span aria-hidden="true">↺</span>
                  </button>
                </div>
              ) : (
                <>
                  <div className="importFormStepHeader">
                    <span>Étape 1</span>
                    <h2 id="import-file-step-title">Fournir votre fichier de collection</h2>
                    <p>
                      Sélectionnez un fichier Excel, LibreOffice ou CSV. Le format est
                      détecté automatiquement à partir du fichier fourni.
                    </p>
                  </div>
                  <p className="importFileExpectation">
                    Le fichier doit contenir une ligne par jeu, avec au minimum une
                    information de nom de jeu et de plateforme. Vous pouvez aussi y
                    ajouter des colonnes optionnelles comme studio, date de sortie,
                    prix, note, état, région ou description. Il peut comporter
                    plusieurs onglets. L'appartenance à votre collection ou à votre
                    liste de souhaits peut être indiquée par une colonne ou par un
                    onglet dédié.
                  </p>
                  <label>
                    Fichier de collection
                    <input
                      type="file"
                      accept=".ods,.xlsx,.csv"
                      onChange={handleFileChange}
                      disabled={isBusy}
                    />
                  </label>
                </>
              )}
            </section>
            {hasAnalyzedImportFile ? (
              <section className="importFormStep" aria-labelledby="import-config-step-title">
                <div className="importFormStepHeader">
                  <span>Étape 2</span>
                  <h2 id="import-config-step-title">Configurer votre import</h2>
                  <p>
                    Renseignez les emplacements ou les colonnes qui contiennent
                    les informations de vos jeux. Les champs obligatoires sont
                    mis en évidence.
                  </p>
                </div>
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
              </section>
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

/**
 * Affiche le message de contribution apres un import utilisateur reussi.
 *
 * @returns {import("react").JSX.Element} Message de validation Bibliotheque.
 * @throws {void} Ne leve pas d'exception.
 */
function UserImportContributionNotice() {
  return (
    <>
      <p>
        Tous les jeux que vous avez importés et qui n'existaient pas encore dans
        la Bibliothèque commune sont accessibles dans votre collection privée.
        Ils seront visibles dans la Bibliothèque commune après validation par un
        administrateur.
      </p>
      <p>Merci pour votre contribution.</p>
    </>
  );
}

export default UserCollectionOnboardingView;
