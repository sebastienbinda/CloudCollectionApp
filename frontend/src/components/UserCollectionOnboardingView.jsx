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
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

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
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
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
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
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
    </PageLayout>
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
    ["Plateformes liees", result.linked_platforms],
    ["Studios crees", result.created_studios],
    ["Jeux crees", result.created_games],
    ["Jeux associes", result.associated_games],
    ["Souhaits importes", result.wishlisted_games],
  ];
  const invalidWishlist = result.warnings?.invalid_wishlist || 0;
  const invalidGames = Array.isArray(result.warnings?.invalid_games)
    ? result.warnings.invalid_games
    : [];
  const platformMatches = Array.isArray(result.warnings?.platform_matches)
    ? result.warnings.platform_matches
    : [];
  const skippedGames = Array.isArray(result.warnings?.skipped_games)
    ? result.warnings.skipped_games
    : [];
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
      {invalidGames.length > 0 ? (
        <InvalidImportedGamesList invalidGames={invalidGames} />
      ) : null}
      {platformMatches.length > 0 ? (
        <PlatformMatchWarningsList platformMatches={platformMatches} />
      ) : null}
      {skippedGames.length > 0 ? (
        <SkippedGamesWarningsList skippedGames={skippedGames} />
      ) : null}
      <button type="button" onClick={onOpenHome}>
        Ouvrir Ma collection
      </button>
    </section>
  );
}

/**
 * Affiche les plateformes rattachees avec verification manuelle.
 *
 * @param {Object} props - Warnings de plateformes incertaines.
 * @returns {import("react").JSX.Element} Liste des rattachements incertains.
 * @throws {void} Ne leve pas d'exception.
 */
function PlatformMatchWarningsList({ platformMatches }) {
  return (
    <section className="invalidImportedGames" aria-label="Plateformes a verifier">
      <h3>Plateformes a verifier</h3>
      <ul>
        {platformMatches.map((warning) => (
          <li key={`${warning.game_name}-${warning.imported_platform}-${warning.matched_platform}`}>
            <strong>{warning.game_name}</strong>
            <span>{formatPlatformMatchWarning(warning)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Affiche les jeux ignores faute de plateforme fiable.
 *
 * @param {Object} props - Warnings de jeux ignores.
 * @returns {import("react").JSX.Element} Liste des jeux ignores.
 * @throws {void} Ne leve pas d'exception.
 */
function SkippedGamesWarningsList({ skippedGames }) {
  return (
    <section className="invalidImportedGames" aria-label="Jeux ignores">
      <h3>Jeux ignores</h3>
      <ul>
        {skippedGames.map((warning) => (
          <li key={`${warning.game_name}-${warning.imported_platform}-${warning.reason}`}>
            <strong>{warning.game_name}</strong>
            <span>{formatSkippedGameWarning(warning)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Affiche les jeux importes avec des informations invalides ignorees.
 *
 * @param {Object} props - Warnings de jeux invalides.
 * @returns {import("react").JSX.Element} Liste des informations invalides.
 * @throws {void} Ne leve pas d'exception.
 */
function InvalidImportedGamesList({ invalidGames }) {
  return (
    <section className="invalidImportedGames" aria-label="Informations invalides importees">
      <h3>Informations ignorees</h3>
      <ul>
        {invalidGames.map((gameWarning) => (
          <li key={`${gameWarning.name}-${JSON.stringify(gameWarning.invalid_fields || [])}`}>
            <strong>{gameWarning.name}</strong>
            <span>{formatInvalidFields(gameWarning.invalid_fields || [])}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Formate les champs invalides d'un jeu pour affichage.
 *
 * @param {Array<Object>} invalidFields - Champs invalides retournes par l'API.
 * @returns {string} Description courte des champs invalides.
 * @throws {void} Ne leve pas d'exception.
 */
function formatInvalidFields(invalidFields) {
  return invalidFields
    .map((field) => {
      const label = field.field === "release_date" ? "Date de sortie" : field.field;
      return field.value ? `${label}: ${field.value}` : label;
    })
    .join(", ");
}

/**
 * Formate un warning de rattachement de plateforme incertain.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise du rattachement.
 * @throws {void} Ne leve pas d'exception.
 */
function formatPlatformMatchWarning(warning) {
  return `${warning.imported_platform || "-"} -> ${warning.matched_platform || "-"} (${Number(warning.score || 0)}%)`;
}

/**
 * Formate un warning de jeu ignore.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise du refus.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSkippedGameWarning(warning) {
  return `${warning.imported_platform || "-"} - ${formatSkippedGameReason(warning.reason)} (${Number(warning.score || 0)}%)`;
}

/**
 * Traduit la raison technique d'un jeu ignore.
 *
 * @param {string} reason - Raison backend.
 * @returns {string} Raison lisible.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSkippedGameReason(reason) {
  const labels = {
    ambiguous: "correspondance ambigue",
    low_score: "score trop faible",
    no_match: "aucune correspondance",
  };
  return labels[reason] || "plateforme non fiable";
}

export default UserCollectionOnboardingView;
