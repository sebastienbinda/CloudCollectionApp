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
 * Description : modale objet de reconnexion apres expiration du token frontend.
 */
import { Component } from "react";
import AuthApi from "../services/AuthApi";

/**
 * Modale globale proposant une reconnexion sans quitter la page courante.
 */
class AuthSessionModal extends Component {
  /**
   * Initialise l'etat local du formulaire de reconnexion.
   *
   * @param {Object} props - Callbacks d'ouverture, fermeture et reconnexion.
   * @returns {void} Prepare les champs du formulaire.
   */
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      error: "",
      isSubmitting: false,
    };
  }

  /**
   * Met a jour un champ du formulaire.
   *
   * @param {string} field - Nom du champ d'etat a modifier.
   * @param {string} value - Nouvelle valeur saisie.
   * @returns {void} Met a jour l'etat React.
   */
  updateField(field, value) {
    this.setState({ [field]: value });
  }

  /**
   * Soumet les identifiants et ferme la modale apres succes.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission.
   * @returns {Promise<void>} Renouvelle le token Bearer frontend.
   */
  async submitReconnectForm(event) {
    event.preventDefault();
    this.setState({ error: "", isSubmitting: true });

    try {
      await AuthApi.authenticate(this.state.username, this.state.password);
      this.setState({ password: "", isSubmitting: false });
      this.props.onAuthenticated();
    } catch (error) {
      this.setState({
        error: error.message || "Reconnexion impossible.",
        isSubmitting: false,
      });
    }
  }

  /**
   * Rend la modale de reconnexion si elle est ouverte.
   *
   * @param {void} Aucun - Utilise les props et l'etat du composant.
   * @returns {import("react").JSX.Element|null} Modale de reconnexion ou rien.
   */
  render() {
    if (!this.props.isOpen) {
      return null;
    }

    return (
      <div className="modalOverlay" role="presentation">
        <section
          className="authSessionDialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="auth-session-title"
        >
          <header className="authSessionHeader">
            <div>
              <p className="eyebrow">Session expiree</p>
              <h2 id="auth-session-title">Reconnexion requise</h2>
            </div>
            <button
              className="secondaryButton"
              type="button"
              onClick={this.props.onClose}
              aria-label="Fermer la modale de reconnexion"
            >
              Fermer
            </button>
          </header>

          <p className="subtitle">
            Votre session a expire. Reconnectez-vous pour continuer les actions protegees.
          </p>
          {this.state.error ? <p className="error">{this.state.error}</p> : null}

          <form className="authForm" onSubmit={(event) => this.submitReconnectForm(event)}>
            <label>
              Identifiant
              <input
                autoComplete="username"
                type="text"
                value={this.state.username}
                onChange={(event) => this.updateField("username", event.target.value)}
                required
              />
            </label>
            <label>
              Mot de passe
              <input
                autoComplete="current-password"
                type="password"
                value={this.state.password}
                onChange={(event) => this.updateField("password", event.target.value)}
                required
              />
            </label>
            <div className="formActions">
              <button className="secondaryButton" type="button" onClick={this.props.onClose}>
                Plus tard
              </button>
              <button type="submit" disabled={this.state.isSubmitting}>
                {this.state.isSubmitting ? "Reconnexion..." : "Se reconnecter"}
              </button>
            </div>
          </form>
        </section>
      </div>
    );
  }
}

export default AuthSessionModal;
