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
import MainMenu from "./MainMenu";
import ImportConfigurationFields from "./ImportConfigurationFields";
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";

/**
 * Affiche le parcours initial d'import de collection ODS.
 *
 * @param {Object} props - Etat d'import, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue d'onboarding d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function UserCollectionOnboardingView({
  authenticatedUsername,
  authenticatedProfile,
  platforms,
  selectedPlatform,
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
  onOpenAbout,
  onOpenHome,
  onOpenLibrary,
  onOpenPlatform,
  onOpenAdminDashboard,
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
    <main className="appShell collectionOnboardingShell">
      <header className="pageHeader collectionOnboardingHeader">
        <MainMenu
          isAuthenticated={isAuthenticated}
          canUseCollectionViews={canUseCollectionViews}
          username={authenticatedUsername}
          profile={authenticatedProfile}
          platforms={platforms}
          selectedPlatform={selectedPlatform}
          onOpenAbout={onOpenAbout}
          onOpenHome={onOpenHome}
          onOpenLibrary={onOpenLibrary}
          onOpenPlatform={onOpenPlatform}
          onOpenAdminDashboard={onOpenAdminDashboard}
          onLogout={onLogout}
        />
        <div>
          <p className="eyebrow">Premiere collection</p>
          <h1>
            <span className="pageTitleWithIcon">
              <ProjectIcon />
              <span>Importer votre collection</span>
            </span>
          </h1>
          <p className="subtitle">
            Ajoutez votre collection pour initialiser vos plateformes, studios et jeux.
          </p>
        </div>
      </header>

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
          <ImportSummary result={importResult} onOpenHome={onOpenHome} />
        ) : (
          <form className="collectionImportForm" onSubmit={handleSubmit}>
          <label>
            Fichier de collection
            <input type="file" accept=".ods" onChange={handleFileChange} disabled={isBusy} />
          </label>
          {selectedCollectionFileName ? (
            <p className="collectionSelectedFile">{selectedCollectionFileName}</p>
          ) : null}
          <label>
            Type de fichier
            <select value={importConfiguration.fileType} disabled>
              <option value="libreoffice_ods">LibreOffice ODS</option>
            </select>
          </label>
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
    </main>
  );
}

/**
 * Affiche le resume d'un import termine.
 *
 * @param {Object} props - Resultat d'import et callback de navigation.
 * @returns {import("react").JSX.Element} Resume d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function ImportSummary({ result, onOpenHome }) {
  const counters = [
    ["Plateformes creees", result.created_platforms],
    ["Studios crees", result.created_studios],
    ["Jeux crees", result.created_games],
    ["Jeux associes", result.associated_games],
    ["Souhaits importes", result.wishlisted_games],
  ];
  const invalidWishlist = result.warnings?.invalid_wishlist || 0;
  return (
    <section className="importSummary" aria-label="Resume de l'import">
      <h2>Import termine</h2>
      <dl>
        {counters.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{Number(value || 0)}</dd>
          </div>
        ))}
      </dl>
      {invalidWishlist ? (
        <p className="warningText">
          {invalidWishlist} ligne(s) wishlist ignoree(s).
        </p>
      ) : null}
      <button type="button" onClick={onOpenHome}>
        Ouvrir Ma collection
      </button>
    </section>
  );
}

export default UserCollectionOnboardingView;
