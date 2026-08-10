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
 * Description : page dediee a l'import CSV admin Bibliotheque.
 */
import ImportSummary, { formatImportDuration } from "./ImportSummary";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche l'ecran dedie d'import CSV admin Bibliotheque.
 *
 * @param {Object} props - Etat d'import admin, session et callbacks.
 * @returns {import("react").JSX.Element} Vue d'import admin.
 * @throws {void} Ne leve pas d'exception.
 */
function AdminLibraryImportView({
  adminLibraryImportError,
  adminLibraryImportResult,
  authenticatedProfile,
  authenticatedUsername,
  canAccessConfiguration,
  canImportLibraryCsv,
  canUseCollectionViews,
  canViewCollection,
  canViewStatistics,
  canViewWishlist,
  isAuthenticated,
  isImportingAdminLibrary,
  onImportAdminLibraryCsv,
  onLogout,
  onOpenAbout,
  onOpenAuth,
  onOpenConfiguration,
  onOpenHome,
  onOpenLibrary,
  onOpenStatistics,
  onOpenWishlist,
  onSelectAdminLibraryImportFile,
  selectedAdminLibraryImportFileName,
}) {
  const handleFileChange = (event) => {
    onSelectAdminLibraryImportFile(event.target.files?.[0] || null);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onImportAdminLibraryCsv();
  };

  return (
    <PageLayout
      shellClassName="appShell collectionOnboardingShell"
      eyebrow="Administration"
      title="Importer dans la Bibliotheque"
      subtitle="Ajoutez des jeux et studios au referentiel commun depuis un fichier CSV."
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
      <section className="collectionOnboardingContent" aria-label="Import admin Bibliotheque">
        <div className="collectionOnboardingSteps" aria-label="Parcours d'import admin">
          <article>
            <span>1</span>
            <h2>Selectionner</h2>
            <p>Choisissez le CSV a ajouter au referentiel commun.</p>
          </article>
          <article>
            <span>2</span>
            <h2>Importer</h2>
            <p>L'import utilise la configuration fixe du backend.</p>
          </article>
          <article>
            <span>3</span>
            <h2>Controler</h2>
            <p>Consultez le resume et les avertissements de matching.</p>
          </article>
        </div>

        <aside className="adminImportConfigurationHelp" aria-label="Configuration admin attendue">
          <h2>Configuration CSV admin attendue</h2>
          <p>
            Le backend utilise la configuration fixe
            {" "}
            <code>backend/resources/admin_import_conf.json</code>
            {" "}
            et lit les colonnes par position dans le fichier.
          </p>
          <dl>
            <div>
              <dt>Type de fichier</dt>
              <dd>CSV avec extension .csv, ligne d'en-tete obligatoire.</dd>
            </div>
            <div>
              <dt>Separateurs acceptes</dt>
              <dd>Virgule, point-virgule ou tabulation.</dd>
            </div>
            <div>
              <dt>Colonnes utilisees</dt>
              <dd>1 = Jeu, 2 = Plateforme, 3 = Studio, 4 = Date de sortie.</dd>
            </div>
          </dl>
          <p>
            Les colonnes Jeu et Plateforme sont obligatoires pour importer une ligne. Studio et
            Date de sortie peuvent rester vides, mais les colonnes doivent exister.
          </p>
        </aside>

        {adminLibraryImportResult ? (
          <ImportSummary
            actionLabel="Ouvrir la Bibliotheque"
            counters={buildAdminImportCounters(adminLibraryImportResult)}
            onAction={onOpenLibrary}
            result={adminLibraryImportResult}
          />
        ) : (
          <form className="collectionImportForm" onSubmit={handleSubmit}>
            <label>
              Fichier CSV Bibliotheque
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={handleFileChange}
                disabled={!canImportLibraryCsv || isImportingAdminLibrary}
              />
            </label>
            {selectedAdminLibraryImportFileName ? (
              <p className="collectionSelectedFile">{selectedAdminLibraryImportFileName}</p>
            ) : null}
            {adminLibraryImportError ? <p className="error">{adminLibraryImportError}</p> : null}
            {isImportingAdminLibrary ? (
              <ProgressBar label="Import CSV Bibliotheque en cours" />
            ) : null}
            <div className="formActions">
              <button
                type="submit"
                disabled={
                  !canImportLibraryCsv ||
                  !selectedAdminLibraryImportFileName ||
                  isImportingAdminLibrary
                }
              >
                {isImportingAdminLibrary ? "Import..." : "Importer"}
              </button>
            </div>
          </form>
        )}
      </section>
    </PageLayout>
  );
}

/**
 * Construit les compteurs affiches pour l'import admin Bibliotheque.
 *
 * @param {Object} result - Resultat backend d'import admin.
 * @returns {Array<Array<string|number>>} Compteurs affichables.
 * @throws {void} Ne leve pas d'exception.
 */
function buildAdminImportCounters(result) {
  return [
    ["Plateformes liees", result.linked_platforms],
    ["Studios crees", result.created_studios],
    ["Jeux crees", result.created_games],
    ["Duree totale", formatImportDuration(result.warnings?.total_import_duration_seconds)],
  ];
}

export default AdminLibraryImportView;
