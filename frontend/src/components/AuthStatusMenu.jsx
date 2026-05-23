/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : encart objet d'etat de connexion avec menu admin au survol.
 */

/**
 * Affiche l'etat d'authentification et les liens de session.
 */
class AuthStatusMenu {
  /**
   * Rend l'encart de connexion de la page d'accueil.
   *
   * @param {Object} props - Etat d'authentification et callbacks de menu.
   * @returns {import("react").JSX.Element} Encart de connexion ou lien de login.
   */
  static render(props) {
    if (!props.isAuthenticated) {
      return this.renderLoginLink();
    }
    return this.renderAuthenticatedMenu(props);
  }

  /**
   * Rend le lien de connexion public.
   *
   * @param {void} Aucun - Aucun etat requis.
   * @returns {import("react").JSX.Element} Lien vers la page de connexion.
   */
  static renderLoginLink() {
    return (
      <a
        className="authButtonLink pageHeaderAuthButton"
        href="/auth"
        aria-label="Connexion"
        title="Connexion"
      >
        <svg aria-hidden="true" className="authStatusIcon" viewBox="0 0 24 24">
          <path d="M12 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 12c4.42 0 8 2.24 8 5v2H4v-2c0-2.76 3.58-5 8-5Z" />
        </svg>
        <span>Connexion</span>
      </a>
    );
  }

  /**
   * Rend l'encart connecte avec menu deroulant.
   *
   * @param {Object} props - Nom utilisateur et callbacks admin/deconnexion.
   * @returns {import("react").JSX.Element} Menu de session connectee.
   */
  static renderAuthenticatedMenu(props) {
    const normalizedProfile = this.normalizeProfile(props.profile);
    const profileClassName = `authButtonProfile${normalizedProfile}`;
    return (
      <div className="authStatusMenu pageHeaderAuthButton">
        <button
          className={`authButtonLink authButtonConnected ${profileClassName} authStatusTrigger`}
          type="button"
          aria-haspopup="true"
          aria-label={`Connecte en tant que ${props.username || "utilisateur"} avec le profil ${normalizedProfile}`}
          title={`Profil ${normalizedProfile}`}
        >
          <svg aria-hidden="true" className="authStatusIcon" viewBox="0 0 24 24">
            <path d="M12 2a5 5 0 0 1 5 5v3h1a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h1V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v3h6V7a3 3 0 0 0-3-3Zm1 11.73A2 2 0 1 0 11 15.73V19h2v-3.27Z" />
          </svg>
          <span>{props.username || "Connecte"}</span>
        </button>
        <div className="authStatusDropdown" role="menu">
          <button type="button" role="menuitem" onClick={props.onOpenAdminDashboard}>
            Dashboard admin
          </button>
          <button type="button" role="menuitem" onClick={props.onLogout}>
            Deconnexion
          </button>
        </div>
      </div>
    );
  }

  /**
   * Normalise le profil applicatif recu depuis l'etat de session.
   *
   * @param {string} profile - Profil brut porte par le token frontend.
   * @returns {string} Profil reconnu pour le rendu visuel du bouton.
   */
  static normalizeProfile(profile) {
    const normalizedProfile = String(profile || "USER").trim().toUpperCase();
    return ["USER", "ADMIN"].includes(normalizedProfile) ? normalizedProfile : "USER";
  }
}

export default AuthStatusMenu;
