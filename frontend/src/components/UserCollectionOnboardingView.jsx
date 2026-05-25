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
  onboardingError,
  isCheckingCollection,
  isImportingCollection,
  isAuthenticated,
  onOpenAbout,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenPlatform,
  onOpenAdminDashboard,
  onLogout,
  onFileChange,
  onSubmitImport,
}) {
  const isBusy = isCheckingCollection || isImportingCollection;

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
          username={authenticatedUsername}
          profile={authenticatedProfile}
          platforms={platforms}
          selectedPlatform={selectedPlatform}
          onOpenAbout={onOpenAbout}
          onOpenHome={onOpenHome}
          onOpenLibrary={onOpenLibrary}
          onOpenWishlist={onOpenWishlist}
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
            <p>Apres succes, Ma collection s'ouvre automatiquement.</p>
          </article>
        </div>

        <form className="collectionImportForm" onSubmit={handleSubmit}>
          <label>
            Fichier de collection
            <input type="file" accept=".ods" onChange={handleFileChange} disabled={isBusy} />
          </label>
          {selectedCollectionFileName ? (
            <p className="collectionSelectedFile">{selectedCollectionFileName}</p>
          ) : null}
          {onboardingError ? <p className="error">{onboardingError}</p> : null}
          {isCheckingCollection ? <ProgressBar label="Verification de votre collection" /> : null}
          {isImportingCollection ? <ProgressBar label="Import de votre collection" /> : null}
          <div className="formActions">
            <button type="submit" disabled={isBusy || !selectedCollectionFileName}>
              {isImportingCollection ? "Import..." : "Importer"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default UserCollectionOnboardingView;
