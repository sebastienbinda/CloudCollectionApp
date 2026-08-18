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
import { hasCsvImportColumn } from "../hooks/collection/importGlobalOptionsVisibility";
import { ImportGlobalOptions } from "./ImportGlobalOptions";
import ImportCollapsibleSection from "./ImportCollapsibleSection";
import ImportFieldHelp from "./ImportFieldHelp";
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
  const showPriceUnit = hasCsvImportColumn(configuration, "purchase_price");
  const showRatingBase = hasCsvImportColumn(configuration, "grade");
  return (
    <>
      <ImportCollapsibleSection title="1. Colonnes du CSV" description="Association des informations aux colonnes détectées.">
        <fieldset className="importConfiguration" disabled={disabled}>
          <legend>Colonnes du CSV</legend>
          <p className="importConfigurationIntro">
            Les champs marqués avec un astérisque sont obligatoires.
          </p>
          <div className="columnGrid">
            {[...REQUIRED_CSV_FIELDS, ...OPTIONAL_CSV_FIELDS].map((fieldName) => {
              const isRequired = requiredFields.includes(fieldName);
              return (
                <label className={isRequired ? "requiredColumnField" : ""} key={fieldName}>
                  <span className="fieldLabelText">
                    {FIELD_LABELS[fieldName]}{isRequired ? " *" : ""}
                  </span>
                  <ColumnNameField
                    required={isRequired}
                    value={configuration.csvMapping[fieldName] || ""}
                    availableColumnNames={availableColumnNames}
                    onChange={(value) => onCsvMappingChange(fieldName, value)}
                  />
                  <ImportFieldHelp fieldName={fieldName} />
                </label>
              );
            })}
          </div>
        </fieldset>
      </ImportCollapsibleSection>
      <ImportCollapsibleSection title="2. Liste de souhaits" description="Source éventuelle des jeux souhaités.">
        <CsvWishlistFields
          configuration={configuration}
          availableColumnNames={availableColumnNames}
          disabled={disabled}
          requiredFields={requiredFields}
          onCsvMappingChange={onCsvMappingChange}
          onWishlistConfigurationChange={onWishlistConfigurationChange}
        />
      </ImportCollapsibleSection>
      {showPriceUnit || showRatingBase ? (
        <ImportCollapsibleSection title="3. Options de prix et de note" description="Affichées seulement si les colonnes liées sont configurées.">
          <ImportGlobalOptions
            showPriceUnit={showPriceUnit}
            showRatingBase={showRatingBase}
            priceUnit={configuration.priceUnit}
            ratingBase={configuration.ratingBase}
            disabled={disabled}
            onConfigurationChange={onConfigurationChange}
          />
        </ImportCollapsibleSection>
      ) : null}
    </>
  );
}

/**
 * Affiche la configuration de liste de souhaits pour un import CSV.
 *
 * @param {Object} props - Etat CSV et callbacks wishlist.
 * @returns {import("react").JSX.Element} Section liste de souhaits CSV.
 * @throws {void} Ne leve pas d'exception.
 */
function CsvWishlistFields({
  configuration,
  availableColumnNames,
  disabled,
  requiredFields,
  onCsvMappingChange,
  onWishlistConfigurationChange,
}) {
  return (
    <fieldset className="wishlistConfiguration" disabled={disabled}>
      <legend>Liste de souhaits</legend>
      <p className="wishlistConfigurationIntro">
        Indiquez si une colonne du CSV signale les jeux à placer dans votre liste
        de souhaits. Sans colonne dédiée, toutes les lignes importées sont ajoutées
        à votre collection.
      </p>
      <div className="segmentedField" role="group" aria-label="Mode liste de souhaits">
        <span>Source</span>
        {["none", "column"].map((mode) => (
          <label key={mode}>
            <input
              type="radio"
              name="wishlistMode"
              checked={configuration.wishlist.mode === mode}
              onChange={() => onWishlistConfigurationChange("mode", mode)}
            />
            {mode === "column" ? "Colonne dédiée" : "Aucune"}
          </label>
        ))}
      </div>
      {configuration.wishlist.mode === "column" ? (
        <label className="requiredColumnField">
          <span className="fieldLabelText">Liste de souhaits *</span>
          <ColumnNameField
            required={requiredFields.includes("wishlist")}
            value={configuration.csvMapping.wishlist || ""}
            availableColumnNames={availableColumnNames}
            onChange={(value) => onCsvMappingChange("wishlist", value)}
          />
          <ImportFieldHelp fieldName="wishlist" />
        </label>
      ) : null}
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
        <option value="">Sélectionner une colonne</option>
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
