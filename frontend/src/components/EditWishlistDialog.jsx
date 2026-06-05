/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-06
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : composant objet de formulaire modal pour modifier un jeu wishlist.
 */
import { Component } from "react";
import DateInputFormatter from "../services/DateInputFormatter";
import ProgressBar from "./ProgressBar";

/**
 * Fenetre modale de modification d'un jeu de liste de souhaits.
 */
class EditWishlistDialog extends Component {
  /**
   * Initialise l'etat local du formulaire wishlist.
   *
   * @param {Object} props - Proprietes React du composant.
   * @returns {void} L'etat du formulaire est initialise.
   */
  constructor(props) {
    super(props);
    this.state = { form: this.buildForm(props.game) };
  }

  /**
   * Resynchronise le formulaire quand un autre jeu est ouvert.
   *
   * @param {Object} previousProps - Anciennes proprietes React.
   * @returns {void} Met a jour l'etat local si necessaire.
   */
  componentDidUpdate(previousProps) {
    if (previousProps.game !== this.props.game) {
      this.setState({ form: this.buildForm(this.props.game) });
    }
  }

  /**
   * Construit le formulaire a partir d'un jeu wishlist.
   *
   * @param {Object|null} game - Jeu selectionne pour modification.
   * @returns {Object} Donnees de formulaire normalisees.
   */
  buildForm(game) {
    const source = game || {};
    return {
      "Nom du jeu": source["Nom du jeu"] || "",
      Console: source.Console || source.Plateforme || "",
      Studio: source.Studio || "",
      "Date de sortie": DateInputFormatter.format(source["Date de sortie"]),
      "Date d'achat": DateInputFormatter.format(source["Date d'achat"]),
      "Lieu d'achat": source["Lieu d'achat"] || "",
      "Prix d'achat": source["Prix d'achat"] ?? source.Prix ?? "",
    };
  }

  /**
   * Met a jour un champ du formulaire.
   *
   * @param {string} field - Nom du champ modifie.
   * @param {string} value - Nouvelle valeur du champ.
   * @returns {void} Met a jour l'etat local.
   */
  updateField(field, value) {
    this.setState((previous) => ({ form: { ...previous.form, [field]: value } }));
  }

  /**
   * Soumet les valeurs modifiees au parent.
   *
   * @param {SubmitEvent} event - Evenement de soumission du formulaire.
   * @returns {void} Transmet le formulaire au callback parent.
   */
  submit(event) {
    event.preventDefault();
    this.props.onSubmit(this.props.game, this.state.form);
  }

  /**
   * Rend un champ de formulaire wishlist.
   *
   * @param {string} field - Nom du champ.
   * @param {string} type - Type HTML de l'input.
   * @param {boolean} required - Indique si le champ est obligatoire.
   * @returns {import("react").JSX.Element} Champ de formulaire.
   */
  renderInput(field, type = "text", required = false) {
    return (
      <label>
        {field}
        <input
          type={type}
          min={type === "number" ? "0" : undefined}
          step={type === "number" ? "0.01" : undefined}
          value={this.state.form[field]}
          onChange={(event) => this.updateField(field, event.target.value)}
          required={required}
        />
      </label>
    );
  }

  /**
   * Rend la modale complete de modification wishlist.
   *
   * @param {void} Aucun - Utilise les props et l'etat React.
   * @returns {import("react").JSX.Element|null} Modale ou rien.
   */
  render() {
    if (!this.props.game) return null;
    return (
      <div className="modalOverlay" role="presentation">
        <section className="editGameDialog" role="dialog" aria-modal="true">
          <header className="editGameDialogHeader">
            <div>
              <p className="eyebrow">Wishlist</p>
              <h2>{this.props.game["Nom du jeu"]}</h2>
            </div>
            <button type="button" className="secondaryButton" onClick={this.props.onCancel}>
              Fermer
            </button>
          </header>
          <form className="addGameForm" onSubmit={(event) => this.submit(event)}>
            {this.renderInput("Nom du jeu", "text", true)}
            {this.renderInput("Console", "text", true)}
            {this.renderInput("Studio", "text", true)}
            {this.renderInput("Date de sortie", "date")}
            {this.renderInput("Date d'achat", "date")}
            {this.renderInput("Lieu d'achat")}
            {this.renderInput("Prix d'achat", "number")}
            <div className="formActions">
              <button type="button" className="secondaryButton" onClick={this.props.onCancel}>
                Annuler
              </button>
              <button type="submit" disabled={this.props.isSaving}>
                Modifier le jeu
              </button>
            </div>
            {this.props.isSaving ? <ProgressBar label="Modification du jeu en cours" /> : null}
          </form>
        </section>
      </div>
    );
  }
}

export default EditWishlistDialog;
