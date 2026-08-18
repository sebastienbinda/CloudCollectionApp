/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-03
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : champs reutilisables de layout tableur pour les imports.
 */

import ImportFieldHelp from "./ImportFieldHelp";

const FIELD_LABELS = Object.freeze({
  name: "Nom du jeu",
  platform: "Plateforme",
  studio: "Studio",
  release_date: "Date de sortie",
  wishlist: "Liste de souhaits",
  purchase_price: "Prix d'achat",
  buy_location: "Lieu d'achat",
  buy_date: "Date d'achat",
  grade: "Note",
  condition: "État",
  has_manual: "Notice",
  is_collector: "Collector",
  has_steelbook: "Steelbook",
  is_digital: "Version dématérialisée",
  region: "Région",
  description: "Description",
});

/**
 * Affiche un layout tableur configurable.
 *
 * @param {Object} props - Layout, champs colonnes et callback de modification.
 * @returns {import("react").JSX.Element} Champs de layout.
 * @throws {void} Ne leve pas d'exception.
 */
function ImportLayoutFields({
  layout,
  columnFields,
  requiredFields = [],
  onLayoutChange,
  onLayoutColumnChange,
}) {
  return (
    <div className="layoutFields">
      <label>
        Plage de données
        <input
          type="text"
          value={layout.dataRange}
          onChange={(event) => onLayoutChange("dataRange", event.target.value)}
        />
        <span className="fieldHelpText">
          Indiquez la première et la dernière cellule du tableau à importer, par exemple A1:D200.
          La plage doit inclure la ligne d'en-tête et les lignes de jeux, sans les notes ou totaux.
        </span>
      </label>
      <label>
        Ligne d'en-tête
        <input
          type="number"
          min="1"
          value={layout.headerRow}
          onChange={(event) => onLayoutChange("headerRow", event.target.value)}
        />
        <span className="fieldHelpText">
          Numéro de la ligne qui contient les titres de colonnes.
        </span>
      </label>
      <div className="columnGrid">
        {columnFields.map((fieldName) => {
          const isRequired = requiredFields.includes(fieldName);
          return (
            <label
              className={isRequired ? "requiredColumnField" : ""}
              key={fieldName}
            >
              <span className="fieldLabelText">
                {FIELD_LABELS[fieldName]}{isRequired ? " *" : ""}
              </span>
              <input
                type="text"
                required={isRequired}
                value={layout.columns[fieldName] || ""}
                onChange={(event) => onLayoutColumnChange(fieldName, event.target.value)}
              />
              <ImportFieldHelp fieldName={fieldName} />
            </label>
          );
        })}
      </div>
    </div>
  );
}

export { FIELD_LABELS };
export default ImportLayoutFields;
