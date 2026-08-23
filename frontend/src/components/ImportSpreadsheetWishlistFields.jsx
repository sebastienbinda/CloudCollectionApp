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
  onWishlistConfigurationChange,
  onWishlistLayoutChange,
  onWishlistLayoutColumnChange,
}) {
  return (
    <fieldset className="wishlistConfiguration" disabled={disabled}>
      <legend>Liste de souhaits</legend>
      <p className="wishlistConfigurationIntro">
        Indiquez comment reconnaître les jeux qui doivent aller dans votre liste
        de souhaits. Sans source dédiée, toutes les lignes importées sont ajoutées
        à votre collection.
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
    </fieldset>
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
