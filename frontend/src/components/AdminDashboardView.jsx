/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page objet de tableau de bord des actions d'administration.
 */
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";

/**
 * Page dediee aux actions protegees de l'application.
 *
 * @param {Object} props - Permissions, messages et callbacks d'administration.
 * @returns {import("react").JSX.Element} Tableau de bord administrateur.
 */
function AdminDashboardView({
  username,
  authenticatedProfile,
  platforms,
  canAddGame,
  canResetCache,
  canDownloadOds,
  canSearchUsers,
  cacheResetMessage,
  cacheResetError,
  isResettingCache,
  downloadError,
  isDownloadingOds,
  onBack,
  onAddGame,
  onOpenUsers,
  onResetCache,
  onDownloadOds,
}) {
  const isAdmin = authenticatedProfile === "ADMIN";

  return (
    <main className="container adminDashboard">
      <button className="backButton" type="button" onClick={onBack}>
        Accueil
      </button>
      <section className="addGameHeader">
        <p className="eyebrow">Administration</p>
        <h1>
          <span className="pageTitleWithIcon">
            <ProjectIcon />
            <span>Dashboard admin</span>
          </span>
        </h1>
        <p className="subtitle">
          Session active : {username || "utilisateur connecte"}.
        </p>
      </section>

      {cacheResetError ? <p className="error">{cacheResetError}</p> : null}
      {downloadError ? <p className="error">{downloadError}</p> : null}
      {cacheResetMessage ? <p className="success">{cacheResetMessage}</p> : null}

      <section className="adminActionGrid" aria-label="Actions d'administration">
        <article className="adminActionCard">
          <span>Collection</span>
          <h2>Ajouter un jeu</h2>
          <p>Ouvre le formulaire d'ajout dans le fichier ODS.</p>
          <button
            type="button"
            onClick={onAddGame}
            disabled={!canAddGame || platforms.length === 0}
          >
            Ajouter un jeu
          </button>
        </article>

        <article className="adminActionCard">
          <span>Cache</span>
          <h2>Reset cache</h2>
          <p>Force le backend a relire les donnees ODS.</p>
          <button
            className="secondaryButton"
            type="button"
            onClick={onResetCache}
            disabled={!canResetCache || isResettingCache}
          >
            Reset cache
          </button>
          {isResettingCache ? <ProgressBar label="Reset du cache en cours" /> : null}
        </article>

        <article className="adminActionCard">
          <span>Export</span>
          <h2>Telecharger ODS</h2>
          <p>Recupere le fichier source de la collection.</p>
          <button
            className="downloadOdsButton"
            type="button"
            onClick={onDownloadOds}
            disabled={!canDownloadOds || isDownloadingOds}
          >
            Telecharger ODS
          </button>
          {isDownloadingOds ? <ProgressBar label="Telechargement ODS en cours" /> : null}
        </article>

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
    </main>
  );
}

export default AdminDashboardView;
