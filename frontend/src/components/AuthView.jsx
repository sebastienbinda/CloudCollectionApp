/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-05
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React d'authentification et de gestion du token Bearer.
 */
import { useState } from "react";
import AuthApi from "../services/AuthApi";
import ProjectIcon from "./ProjectIcon";

/**
 * Page d'authentification backend pour recuperer un token Bearer.
 *
 * @param {Object} props - Callbacks de navigation et etat d'authentification.
 * @returns {import("react").JSX.Element} Formulaire de connexion.
 */
function AuthView({ isAuthenticated, onBack, onAuthenticated }) {
  const [activeMode, setActiveMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [registrationEmail, setRegistrationEmail] = useState("");
  const [registrationPassword, setRegistrationPassword] = useState("");
  const [registrationPasswordConfirmation, setRegistrationPasswordConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("reason") === AuthApi.expiredSessionQuery
      ? "Votre session a expire. Veuillez vous reconnecter."
      : "";
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);

  /**
   * Soumet les identifiants au backend et stocke le token retourne.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission.
   * @returns {Promise<void>} Met a jour les messages de connexion.
   */
  const submitAuthForm = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      setIsSubmitting(true);
      await AuthApi.authenticate(username, password);
      setPassword("");
      setMessage("Connexion active.");
      onAuthenticated();
    } catch (e) {
      setError(e.message || "Identifiants invalides.");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Soumet la demande de creation de compte au backend.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission.
   * @returns {Promise<void>} Affiche le resultat de l'inscription.
   */
  const submitRegistrationForm = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    if (registrationPassword !== registrationPasswordConfirmation) {
      setError("Les mots de passe saisis ne correspondent pas.");
      return;
    }

    try {
      setIsRegistering(true);
      const data = await AuthApi.registerUser(registrationEmail, registrationPassword);
      const createdEmail = data.user?.email || registrationEmail;
      setRegistrationEmail("");
      setRegistrationPassword("");
      setRegistrationPasswordConfirmation("");
      setActiveMode("login");
      setUsername(createdEmail);
      setMessage("Compte cree. Consultez votre email pour valider votre adresse avant connexion.");
    } catch (e) {
      setError(e.message || "Inscription impossible.");
    } finally {
      setIsRegistering(false);
    }
  };

  /**
   * Deconnecte le frontend en supprimant le token local.
   *
   * @param {void} Aucun - Utilise le client API.
   * @returns {void} Vide le token et affiche un message.
   */
  const logout = () => {
    AuthApi.clearAccessToken();
    setMessage("Connexion fermee.");
    setError("");
  };

  /**
   * Change le formulaire affiche et remet a zero les messages.
   *
   * @param {"login"|"register"} nextMode - Mode de formulaire cible.
   * @returns {void} Met a jour le mode courant.
   */
  const switchMode = (nextMode) => {
    setActiveMode(nextMode);
    setMessage("");
    setError("");
  };

  return (
    <main className="container authContainer">
      <button className="backButton" type="button" onClick={onBack}>
        Accueil
      </button>
      <section className="authHeader">
        <p className="eyebrow">Acces protege</p>
        <h1>
          <span className="pageTitleWithIcon">
            <ProjectIcon />
            <span>Authentification</span>
          </span>
        </h1>
        <p className="subtitle">Connectez-vous pour afficher les actions de mise a jour.</p>
      </section>

      {error ? <p className="error">{error}</p> : null}
      {message ? <p className="success">{message}</p> : null}

      <div className="authModeSelector" aria-label="Choix du formulaire">
        <button
          className={activeMode === "login" ? "active" : ""}
          type="button"
          onClick={() => switchMode("login")}
        >
          Connexion
        </button>
        <button
          className={activeMode === "register" ? "active" : ""}
          type="button"
          onClick={() => switchMode("register")}
        >
          Creation de compte
        </button>
      </div>

      {activeMode === "login" ? (
        <form className="authForm" onSubmit={submitAuthForm}>
          <label>
            Identifiant
            <input
              autoComplete="username"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label>
            Mot de passe
            <input
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <div className="formActions">
            {isAuthenticated ? (
              <button className="secondaryButton" type="button" onClick={logout}>
                Deconnexion
              </button>
            ) : null}
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Connexion..." : "Se connecter"}
            </button>
          </div>
        </form>
      ) : (
        <form className="authForm" onSubmit={submitRegistrationForm}>
          <label>
            Email
            <input
              autoComplete="email"
              type="email"
              value={registrationEmail}
              onChange={(event) => setRegistrationEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Mot de passe
            <input
              autoComplete="new-password"
              type="password"
              value={registrationPassword}
              onChange={(event) => setRegistrationPassword(event.target.value)}
              required
            />
          </label>
          <label>
            Confirmation du mot de passe
            <input
              autoComplete="new-password"
              type="password"
              value={registrationPasswordConfirmation}
              onChange={(event) => setRegistrationPasswordConfirmation(event.target.value)}
              required
            />
          </label>
          <div className="formActions">
            <button type="submit" disabled={isRegistering}>
              {isRegistering ? "Creation..." : "Creer le compte"}
            </button>
          </div>
        </form>
      )}
    </main>
  );
}

export default AuthView;
