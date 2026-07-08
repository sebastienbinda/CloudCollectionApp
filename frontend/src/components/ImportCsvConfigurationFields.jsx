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
 * Description : champs de mapping CSV pour l'import de collection.
 */

import {
  OPTIONAL_CSV_FIELDS,
  REQUIRED_CSV_FIELDS,
} from "../hooks/collection/csvImportConfigurationBuilder";
import { FIELD_LABELS } from "./ImportLayoutFields";

/**
 * Affiche les champs frontend de configuration CSV.
 *
 * @param {Object} props - Etat de configuration et callbacks de modification.
 * @returns {import("react").JSX.Element} Champs de configuration CSV.
 */
function ImportCsvConfigurationFields({
  configuration,
  availableColumnNames = [],
  disabled,
  onConfigurationChange,
  onCsvMappingChange,
  onWishlistConfigurationChange,
}) {
  const requiredFields = csvRequiredFields(configuration);
  return (
    <fieldset className="importConfiguration" disabled={disabled}>
      <legend>Configuration du fichier</legend>
      <p>* Champs obligatoires</p>

      <label>
        Unite des prix
        <select
          value={configuration.priceUnit}
          onChange={(event) => onConfigurationChange("priceUnit", event.target.value)}
        >
          {["EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "KRW"].map(
            (priceUnit) => <option key={priceUnit} value={priceUnit}>{priceUnit}</option>
          )}
        </select>
      </label>

      <label>
        Base de notation
        <input
          type="number"
          min="1"
          value={configuration.ratingBase}
          onChange={(event) => onConfigurationChange("ratingBase", event.target.value)}
        />
      </label>

      <div className="segmentedField" role="group" aria-label="Mode wishlist">
        <span>Wishlist</span>
        {["none", "column"].map((mode) => (
          <label key={mode}>
            <input
              type="radio"
              name="wishlistMode"
              checked={configuration.wishlist.mode === mode}
              onChange={() => onWishlistConfigurationChange("mode", mode)}
            />
            {mode === "column" ? "Colonne" : "Aucune"}
          </label>
        ))}
      </div>

      <div className="columnGrid">
        {[...REQUIRED_CSV_FIELDS, ...OPTIONAL_CSV_FIELDS, "wishlist"].map((fieldName) => {
          if (fieldName === "wishlist" && configuration.wishlist.mode !== "column") {
            return null;
          }
          return (
            <label key={fieldName}>
              {FIELD_LABELS[fieldName]}{requiredFields.includes(fieldName) ? " *" : ""}
              <ColumnNameField
                required={requiredFields.includes(fieldName)}
                value={configuration.csvMapping[fieldName] || ""}
                availableColumnNames={availableColumnNames}
                onChange={(value) => onCsvMappingChange(fieldName, value)}
              />
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

/**
 * Affiche une selection de colonne detectee ou une saisie libre de secours.
 *
 * @param {Object} props - Valeur, options et callback.
 * @returns {import("react").JSX.Element} Champ de colonne.
 */
function ColumnNameField({ required, value, availableColumnNames, onChange }) {
  if (availableColumnNames.length) {
    return (
      <select required={required} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Selectionner une colonne</option>
        {availableColumnNames.map((columnName) => (
          <option key={columnName} value={columnName}>{columnName}</option>
        ))}
      </select>
    );
  }
  return (
    <input
      type="text"
      required={required}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

/**
 * Retourne les champs CSV obligatoires selon le mode wishlist.
 *
 * @param {Object} configuration - Configuration d'import courante.
 * @returns {string[]} Champs requis.
 */
function csvRequiredFields(configuration) {
  const fields = [...REQUIRED_CSV_FIELDS];
  if (configuration.wishlist.mode === "column") {
    fields.push("wishlist");
  }
  return fields;
}

export default ImportCsvConfigurationFields;
