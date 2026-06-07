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
  platforms,
  canAddGame,
  canDownloadOds,
  canReinitializeCollection,
  canSearchUsers,
  canUseCollectionViews,
  downloadError,
  isDownloadingOds,
  reinitializationError,
  isReinitializingCollection,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onAddGame,
  onOpenUsers,
  onOpenConfiguration,
  onDownloadOds,
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
      authenticatedUsername={username}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {downloadError ? <p className="error">{downloadError}</p> : null}
      {reinitializationError ? <p className="error">{reinitializationError}</p> : null}

      <section className="adminActionGrid" aria-label="Actions d'administration">
        {canUseCollectionViews ? (
          <article className="adminActionCard">
            <span>Collection</span>
            <h2>Ajouter un jeu</h2>
            <p>Ouvre le formulaire d'ajout dans la collection.</p>
            <button
              type="button"
              onClick={onAddGame}
              disabled={!canAddGame || platforms.length === 0}
            >
              Ajouter un jeu
            </button>
          </article>
        ) : null}

        {canUseCollectionViews ? (
          <article className="adminActionCard">
            <span>Export</span>
            <h2>Telecharger la collection</h2>
            <p>Recupere le fichier source de la collection.</p>
            <button
              className="downloadOdsButton"
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
            <h2>Reinitialiser la collection</h2>
            <p>
              Supprime la collection actuelle et son fichier serveur pour permettre un nouvel import.
            </p>
            <button
              className="secondaryButton"
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
            <span>Utilisateurs</span>
            <h2>Gerer les utilisateurs</h2>
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
      </section>
    </PageLayout>
  );
}

export default ConfigurationView;
