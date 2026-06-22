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
import { useEffect, useRef, useState } from "react";
import AuthApi from "../services/AuthApi";
import PageLayout from "./PageLayout";

/**
 * Page d'authentification backend pour recuperer un token Bearer.
 *
 * @param {Object} props - Callbacks de navigation et etat d'authentification.
 * @returns {import("react").JSX.Element} Formulaire de connexion.
 */
function AuthView({
  isAuthenticated,
  canUseCollectionViews,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  onAuthenticated,
}) {
  const requestedLoginEmail = new URLSearchParams(window.location.search).get("email") || "";
  const [activeMode, setActiveMode] = useState("login");
  const [username, setUsername] = useState(requestedLoginEmail);
  const [password, setPassword] = useState("");
  const [registrationEmail, setRegistrationEmail] = useState("");
  const [registrationPseudonym, setRegistrationPseudonym] = useState("");
  const [pseudonymAvailability, setPseudonymAvailability] = useState("idle");
  const [pseudonymAvailabilityMessage, setPseudonymAvailabilityMessage] = useState("");
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
  const pseudonymCheckSequence = useRef(0);
  const normalizedRequestedLoginEmail = requestedLoginEmail.trim().toLowerCase();
  const normalizedAuthenticatedSubject = AuthApi.getAuthenticatedSubject().trim().toLowerCase();
  const isRequestedUserAlreadyConnected = Boolean(
    isAuthenticated
    && normalizedRequestedLoginEmail
    && normalizedRequestedLoginEmail === normalizedAuthenticatedSubject
  );

  useEffect(() => {
    if (isRequestedUserAlreadyConnected) {
      onOpenAbout();
    }
  }, [isRequestedUserAlreadyConnected, onOpenAbout]);

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
      await onAuthenticated();
      setMessage("Connexion active.");
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
      if (pseudonymAvailability !== "available") {
        setError("Veuillez choisir et valider un pseudonyme disponible.");
        return;
      }
      const data = await AuthApi.registerUser(
        registrationEmail,
        registrationPseudonym,
        registrationPassword,
      );
      const createdEmail = data.user?.email || registrationEmail;
      setRegistrationEmail("");
      setRegistrationPseudonym("");
      setPseudonymAvailability("idle");
      setPseudonymAvailabilityMessage("");
      setRegistrationPassword("");
      setRegistrationPasswordConfirmation("");
      setActiveMode("login");
      setUsername(createdEmail);
      setMessage(
        "Compte cree. Consultez votre email pour valider votre adresse avant connexion."
      );
    } catch (e) {
      if (String(e.message || "").toLowerCase().includes("pseudonyme")) {
        setPseudonymAvailability("unavailable");
        setPseudonymAvailabilityMessage(e.message);
      }
      setError(e.message || "Inscription impossible.");
    } finally {
      setIsRegistering(false);
    }
  };

  /**
   * Invalide le controle precedent lorsqu'un pseudonyme est modifie.
   *
   * @param {string} value - Nouvelle valeur saisie.
   * @returns {void} Replace la disponibilite dans son etat initial.
   */
  const updateRegistrationPseudonym = (value) => {
    pseudonymCheckSequence.current += 1;
    setRegistrationPseudonym(value);
    setPseudonymAvailability("idle");
    setPseudonymAvailabilityMessage("");
  };

  /**
   * Verifie la disponibilite du pseudonyme a la perte de focus.
   *
   * @returns {Promise<void>} Met a jour l'etat de validation du formulaire.
   */
  const checkRegistrationPseudonym = async () => {
    const pseudonym = registrationPseudonym.trim();
    if (!pseudonym) {
      setPseudonymAvailability("invalid");
      setPseudonymAvailabilityMessage("Le pseudonyme est obligatoire.");
      return;
    }

    const checkSequence = pseudonymCheckSequence.current + 1;
    pseudonymCheckSequence.current = checkSequence;
    setPseudonymAvailability("checking");
    setPseudonymAvailabilityMessage("Verification du pseudonyme...");
    try {
      const result = await AuthApi.checkPseudonymAvailability(pseudonym);
      if (pseudonymCheckSequence.current !== checkSequence) {
        return;
      }
      setRegistrationPseudonym(result.pseudonym || pseudonym);
      setPseudonymAvailability(result.available ? "available" : "unavailable");
      setPseudonymAvailabilityMessage(
        result.available ? "Pseudonyme disponible." : "Ce pseudonyme est deja utilise."
      );
    } catch (availabilityError) {
      if (pseudonymCheckSequence.current !== checkSequence) {
        return;
      }
      setPseudonymAvailability("invalid");
      setPseudonymAvailabilityMessage(
        availabilityError.message || "Verification du pseudonyme impossible."
      );
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
   * Deconnecte la session courante pour preparer une connexion avec le compte cible.
   *
   * @returns {void} Vide le token et pre-remplit l'identifiant cible.
   */
  const logoutForRequestedUser = () => {
    AuthApi.clearAccessToken();
    setActiveMode("login");
    setUsername(requestedLoginEmail);
    setPassword("");
    setMessage("Session fermee. Vous pouvez maintenant vous connecter avec le compte demande.");
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
  const authNavigationProps = {
    isAuthenticated: false,
    canUseCollectionViews: false,
    authenticatedUsername: "",
    authenticatedProfile: "",
    activeNavigationKey: "login",
  };

  if (isRequestedUserAlreadyConnected) {
    return (
      <PageLayout
        shellClassName="container authContainer"
        eyebrow="Session active"
        title="Connexion deja active"
        subtitle="Vous etes deja connecte avec le compte demande."
        {...authNavigationProps}
        onOpenAbout={onOpenAbout}
        onOpenAuth={onOpenAuth}
        onOpenHome={onOpenHome}
        onOpenLibrary={onOpenLibrary}
        onOpenWishlist={onOpenWishlist}
        onOpenConfiguration={onOpenConfiguration}
        onLogout={onLogout}
      >
        <p className="success">Redirection vers la page A propos.</p>
      </PageLayout>
    );
  }

  if (isAuthenticated) {
    const requestedAccountText = requestedLoginEmail
      ? `Le lien concerne le compte ${requestedLoginEmail}.`
      : "Vous pouvez fermer la session courante pour utiliser un autre compte.";
    return (
      <PageLayout
        shellClassName="container authContainer"
        eyebrow="Session active"
        title="Vous etes deja connecte"
        subtitle="Une session est deja ouverte dans ce navigateur."
        {...authNavigationProps}
        onOpenAbout={onOpenAbout}
        onOpenAuth={onOpenAuth}
        onOpenHome={onOpenHome}
        onOpenLibrary={onOpenLibrary}
        onOpenWishlist={onOpenWishlist}
        onOpenConfiguration={onOpenConfiguration}
        onLogout={onLogout}
      >
        <section className="authForm" aria-label="Session deja active">
          <p className="success">Vous etes connecte avec {authenticatedUsername}.</p>
          <p>{requestedAccountText}</p>
          <div className="formActions">
            <button className="secondaryButton" type="button" onClick={logoutForRequestedUser}>
              Se deconnecter
            </button>
            <button type="button" onClick={onOpenAbout}>
              Continuer avec ce compte
            </button>
          </div>
        </section>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      shellClassName="container authContainer"
      eyebrow="Acces protege"
      title="Authentification"
      subtitle="Connectez-vous pour afficher les actions de mise a jour."
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
            Pseudonyme
            <input
              autoComplete="nickname"
              type="text"
              value={registrationPseudonym}
              onChange={(event) => updateRegistrationPseudonym(event.target.value)}
              onBlur={checkRegistrationPseudonym}
              minLength={3}
              maxLength={32}
              pattern="[A-Za-z0-9_-]{3,32}"
              aria-describedby="registration-pseudonym-description registration-pseudonym-status"
              required
            />
            <small id="registration-pseudonym-description">
              Ce nom identifiera votre session et votre collection lors du futur partage.
            </small>
            {pseudonymAvailabilityMessage ? (
              <small
                id="registration-pseudonym-status"
                className={pseudonymAvailability === "available" ? "success" : "error"}
                aria-live="polite"
              >
                {pseudonymAvailabilityMessage}
              </small>
            ) : null}
          </label>
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
            <button
              type="submit"
              disabled={isRegistering || pseudonymAvailability !== "available"}
            >
              {isRegistering ? "Creation..." : "Creer le compte"}
            </button>
          </div>
        </form>
      )}
    </PageLayout>
  );
}

export default AuthView;
