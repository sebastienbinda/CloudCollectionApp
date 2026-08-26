/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-18
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : configuration liste de souhaits pour les imports tableur.
 */

import { wishlistSheetColumnFields } from "../hooks/collection/importConfigurationBuilder";
import { IMPORT_FIELD_LABELS } from "../hooks/collection/importFieldLabels";
import ImportFieldHelp from "./ImportFieldHelp";
import ImportLayoutFields from "./ImportLayoutFields";

const modeLabels = Object.freeze({
  none: "Aucune",
  sheet: "Onglet dédié",
  column: "Colonne dédiée",
});

/**
 * Affiche la configuration liste de souhaits commune aux modes tableur.
 *
 * @param {Object} props - Etat liste de souhaits et callbacks.
 * @returns {import("react").JSX.Element} Champs liste de souhaits.
 * @throws {void} Ne leve pas d'exception.
 */
function ImportSpreadsheetWishlistFields({
  configuration,
  availableSheetNames,
  disabled,
  onLayoutColumnChange,
  onSheetColumnChange,
  onWishlistConfigurationChange,
  onWishlistLayoutChange,
  onWishlistLayoutColumnChange,
}) {
  return (
    <fieldset className="wishlistConfiguration" disabled={disabled}>
      <legend>Liste de souhaits</legend>
      <p className="wishlistConfigurationIntro">
        Choisissez la source des jeux à ajouter dans la section Liste de souhaits.
        Sans source dédiée, chaque ligne est importée dans votre collection.
      </p>
      <div className="segmentedField" role="group" aria-label="Mode liste de souhaits">
        <span>Source</span>
        {["none", "sheet", "column"].map((mode) => (
          <label key={mode}>
            <input
              type="radio"
              name="wishlistMode"
              checked={configuration.wishlist.mode === mode}
              onChange={() => onWishlistConfigurationChange("mode", mode)}
            />
            {modeLabels[mode]}
          </label>
        ))}
      </div>
      {configuration.wishlist.mode === "sheet" ? (
        <>
          <label>
            Onglet liste de souhaits *
            <SheetNameField
              value={configuration.wishlist.sheetName}
              availableSheetNames={availableSheetNames}
              onChange={(value) => onWishlistConfigurationChange("sheetName", value)}
            />
          </label>
          <ImportLayoutFields
            layout={configuration.wishlist.layout}
            columnFields={wishlistSheetColumnFields()}
            requiredFields={["name", "platform"]}
            onLayoutChange={onWishlistLayoutChange}
            onLayoutColumnChange={onWishlistLayoutColumnChange}
          />
        </>
      ) : null}
      {configuration.wishlist.mode === "column" ? (
        <WishlistColumnFields
          configuration={configuration}
          onLayoutColumnChange={onLayoutColumnChange}
          onSheetColumnChange={onSheetColumnChange}
        />
      ) : null}
    </fieldset>
  );
}

/**
 * Affiche la colonne wishlist a renseigner dans le layout de collection.
 *
 * @param {Object} props - Configuration courante et callbacks de layout.
 * @returns {import("react").JSX.Element} Champs de colonne wishlist.
 * @throws {void} Ne leve pas d'exception.
 */
function WishlistColumnFields({ configuration, onLayoutColumnChange, onSheetColumnChange }) {
  if (configuration.multipleSheets && !configuration.sharedLayout) {
    return (
      <div className="columnGrid">
        {configuration.sheets.map((sheet, index) => (
          <WishlistColumnField
            key={sheet.sheetName || `sheet-wishlist-${index + 1}`}
            label={sheet.sheetName || `Onglet ${index + 1}`}
            value={sheet.layout?.columns?.wishlist || ""}
            onChange={(value) => onSheetColumnChange(index, "wishlist", value)}
          />
        ))}
      </div>
    );
  }
  const layoutName = configuration.multipleSheets ? "sharedSheetLayout" : "singleSheetLayout";
  const layout = configuration.multipleSheets
    ? configuration.sharedSheetLayout
    : configuration.singleSheetLayout;
  return (
    <WishlistColumnField
      label={IMPORT_FIELD_LABELS.wishlist}
      value={layout.columns?.wishlist || ""}
      onChange={(value) => onLayoutColumnChange(layoutName, "wishlist", value)}
    />
  );
}

/**
 * Affiche un champ de saisie de colonne wishlist.
 *
 * @param {Object} props - Libelle, valeur et callback de modification.
 * @returns {import("react").JSX.Element} Champ de colonne.
 * @throws {void} Ne leve pas d'exception.
 */
function WishlistColumnField({ label, value, onChange }) {
  return (
    <label className="requiredColumnField">
      <span className="fieldLabelText">{label} *</span>
      <input
        type="text"
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <ImportFieldHelp fieldName="wishlist" />
    </label>
  );
}

/**
 * Affiche une selection d'onglet simple.
 *
 * @param {Object} props - Valeur courante, options et callback.
 * @returns {import("react").JSX.Element} Champ onglet.
 * @throws {void} Ne leve pas d'exception.
 */
function SheetNameField({ value, availableSheetNames, onChange }) {
  if (availableSheetNames.length) {
    return (
      <select required value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Sélectionner un onglet</option>
        {availableSheetNames.map((sheetName) => (
          <option key={sheetName} value={sheetName}>{sheetName}</option>
        ))}
      </select>
    );
  }
  return <input type="text" required value={value} onChange={(event) => onChange(event.target.value)} />;
}

export default ImportSpreadsheetWishlistFields;
