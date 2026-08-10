/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page objet de configuration des actions protegees.
 */
import ProgressBar from "./ProgressBar";
import PageLayout from "./PageLayout";

/**
 * Page dediee aux actions protegees de l'application.
 *
 * @param {Object} props - Permissions, messages et callbacks de configuration.
 * @returns {import("react").JSX.Element} Vue de configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function ConfigurationView({
  username,
  authenticatedProfile,
  isAuthenticated,
  canDownloadOds,
  canResetLibrary,
  canImportLibraryCsv,
  canSyncPlatformCatalog,
  canModeratePlatformImages,
  canReinitializeCollection,
  canSearchUsers,
  canManageCollectionShares,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  downloadError,
  isDownloadingOds,
  libraryResetError,
  libraryResetMessage,
  isResettingLibrary,
  isLibraryResetConfirmationOpen,
  waitingValidationResetCount,
  platformCatalogSyncError,
  platformCatalogSyncMessage,
  isSyncingPlatformCatalog,
  reinitializationError,
  isReinitializingCollection,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenUsers,
  onOpenAdminLibraryImport,
  onOpenPlatformImageModeration,
  onOpenConfiguration,
  onOpenCollectionOnboarding,
  onOpenCollectionShares,
  onDownloadOds,
  onResetLibrary,
  onCancelLibraryReset,
  onConfirmLibraryReset,
  onSyncPlatformCatalog,
  onReinitializeCollection,
  onLogout,
}) {
  const isAdmin = authenticatedProfile === "ADMIN";

  return (
    <PageLayout
      shellClassName="appShell configuration"
      eyebrow="Administration"
      title="Configuration"
      subtitle="Accedez aux actions d'administration disponibles pour votre profil."
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={username}
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
      {downloadError ? <p className="error">{downloadError}</p> : null}
      {libraryResetError ? <p className="error">{libraryResetError}</p> : null}
      {libraryResetMessage ? <p className="success">{libraryResetMessage}</p> : null}
      {platformCatalogSyncError ? <p className="error">{platformCatalogSyncError}</p> : null}
      {platformCatalogSyncMessage ? <p className="success">{platformCatalogSyncMessage}</p> : null}
      {reinitializationError ? <p className="error">{reinitializationError}</p> : null}

      <section className="adminActionGrid" aria-label="Actions d'administration">
        {canManageCollectionShares ? (
          <article className="adminActionCard">
            <span>Partage</span>
            <h2>Partager</h2>
            <p>Cree et revoque les liens temporaires donnant acces a votre collection.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onOpenCollectionShares}
            >
              Gerer les partages
            </button>
          </article>
        ) : null}

        {canUseCollectionViews ? (
          <article className="adminActionCard">
            <span>Import</span>
            <h2>Importer</h2>
            <p>Ajoute les jeux d'un nouveau fichier a la collection actuelle.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onOpenCollectionOnboarding}
            >
              Importer un fichier
            </button>
          </article>
        ) : null}

        {canUseCollectionViews ? (
          <article className="adminActionCard">
            <span>Export</span>
            <h2>Exporter</h2>
            <p>Recupere le fichier source de la collection.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onDownloadOds}
              disabled={!canDownloadOds || isDownloadingOds}
            >
              Telecharger la collection
            </button>
            {isDownloadingOds ? <ProgressBar label="Telechargement de la collection en cours" /> : null}
          </article>
        ) : null}

        {canUseCollectionViews && !isAdmin ? (
          <article className="adminActionCard">
            <span>Collection</span>
            <h2>Reinitialiser</h2>
            <p>
              Supprime la collection actuelle et son fichier serveur pour permettre un nouvel import.
            </p>
            <button
              className="dangerButton"
              type="button"
              onClick={onReinitializeCollection}
              disabled={!canReinitializeCollection || isReinitializingCollection}
            >
              Reinitialiser la collection
            </button>
            {isReinitializingCollection ? (
              <ProgressBar label="Reinitialisation de la collection en cours" />
            ) : null}
          </article>
        ) : null}

        {isAdmin ? (
          <article className="adminActionCard">
            <span>Bibliotheque</span>
            <h2>Importer CSV</h2>
            <p>Ajoute des jeux et studios dans la Bibliotheque globale.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onOpenAdminLibraryImport}
              disabled={!canImportLibraryCsv}
            >
              Ouvrir l'import
            </button>
          </article>
        ) : null}

        {isAdmin ? (
          <article className="adminActionCard">
            <span>Plateformes</span>
            <h2>Mettre a jour</h2>
            <p>Ajoute en base les plateformes et alias manquants depuis les CSV backend.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onSyncPlatformCatalog}
              disabled={!canSyncPlatformCatalog || isSyncingPlatformCatalog}
            >
              Mettre a jour
            </button>
            {isSyncingPlatformCatalog ? (
              <ProgressBar label="Mise a jour du catalogue plateformes en cours" />
            ) : null}
          </article>
        ) : null}

        {isAdmin ? (
          <article className="adminActionCard dangerActionCard">
            <span>Bibliotheque</span>
            <h2>Reset</h2>
            <p>
              Supprime et reconstruit toute la Bibliotheque globale depuis les imports utilisateur.
            </p>
            <button
              className="dangerButton"
              type="button"
              onClick={onResetLibrary}
              disabled={!canResetLibrary || isResettingLibrary}
            >
              Lancer le reset
            </button>
            {isResettingLibrary ? (
              <ProgressBar label="Reset Bibliotheque en cours de lancement" />
            ) : null}
          </article>
        ) : null}

        {isAdmin ? (
          <article className="adminActionCard">
            <span>Utilisateurs</span>
            <h2>Utilisateurs</h2>
            <p>Consulte les comptes applicatifs et leurs statuts.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onOpenUsers}
              disabled={!canSearchUsers}
            >
              Gerer les utilisateurs
            </button>
          </article>
        ) : null}

        {isAdmin ? (
          <article className="adminActionCard">
            <span>Images</span>
            <h2>Images de plateformes</h2>
            <p>Ouvre la page de moderation des images proposees par les utilisateurs.</p>
            <button
              className="secondaryButton"
              type="button"
              onClick={onOpenPlatformImageModeration}
              disabled={!canModeratePlatformImages}
            >
              Moderer les images
            </button>
          </article>
        ) : null}
      </section>

      <LibraryResetConfirmationDialog
        isOpen={isLibraryResetConfirmationOpen}
        isResettingLibrary={isResettingLibrary}
        waitingValidationCount={waitingValidationResetCount}
        onCancel={onCancelLibraryReset}
        onConfirm={onConfirmLibraryReset}
      />
    </PageLayout>
  );
}

/**
 * Affiche la confirmation du reset Bibliotheque.
 *
 * @param {Object} props - Etat de la pop-up et callbacks de confirmation.
 * @returns {import("react").JSX.Element|null} Pop-up de confirmation ou rien.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function LibraryResetConfirmationDialog({
  isOpen,
  isResettingLibrary,
  waitingValidationCount,
  onCancel,
  onConfirm,
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modalOverlay" role="presentation">
      <section
        className="adminResetConfirmationDialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="admin-reset-confirmation-title"
      >
        <header>
          <p className="eyebrow">Confirmation</p>
          <h2 id="admin-reset-confirmation-title">Confirmer le reset Bibliotheque</h2>
        </header>
        <p>
          ATTENTION : ce reset supprime et reconstruit toute la Bibliotheque globale a partir des
          imports utilisateur.
        </p>
        {Number(waitingValidationCount) > 0 ? (
          <p className="adminResetValidationWarning">
            <strong>{waitingValidationCount} jeu(x)</strong>
            {" "}
            marque(s) comme en attente de validation seront automatiquement acceptes si le reset est
            lance.
          </p>
        ) : null}
        <div className="formActions">
          <button
            className="secondaryButton"
            type="button"
            onClick={onCancel}
            disabled={isResettingLibrary}
          >
            Annuler
          </button>
          <button
            className="dangerButton"
            type="button"
            onClick={onConfirm}
            disabled={isResettingLibrary}
          >
            Confirmer le reset
          </button>
        </div>
      </section>
    </div>
  );
}

export default ConfigurationView;
