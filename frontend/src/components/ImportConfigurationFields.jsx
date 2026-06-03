/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-27
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : champs de configuration d'import de collection.
 */
import ImportLayoutFields from "./ImportLayoutFields";

/**
 * Affiche les champs frontend de configuration d'import.
 *
 * @param {Object} props - Etat de configuration et callbacks de modification.
 * @returns {import("react").JSX.Element} Champs de configuration.
 */
function ImportConfigurationFields({
  configuration,
  availableSheetNames = [],
  disabled,
  onConfigurationChange,
  onLayoutChange,
  onLayoutColumnChange,
  onSheetChange,
  onSheetLayoutChange,
  onSheetColumnChange,
  onWishlistConfigurationChange,
  onWishlistLayoutChange,
  onWishlistLayoutColumnChange,
  onAddSheet,
  onRemoveSheet,
}) {
  const columnFields = collectionColumnFields(configuration, !configuration.multipleSheets);

  return (
    <fieldset className="importConfiguration" disabled={disabled}>
      <legend>Configuration du fichier</legend>

      <WishlistFields
        configuration={configuration}
        availableSheetNames={availableSheetNames}
        onWishlistConfigurationChange={onWishlistConfigurationChange}
        onWishlistLayoutChange={onWishlistLayoutChange}
        onWishlistLayoutColumnChange={onWishlistLayoutColumnChange}
      />

      <div className="segmentedField" role="group" aria-label="Import multi-onglets">
        <span>Multiple onglets</span>
        <label>
          <input
            type="radio"
            name="multipleSheets"
            checked={!configuration.multipleSheets}
            onChange={() => onConfigurationChange("multipleSheets", false)}
          />
          Non
        </label>
        <label>
          <input
            type="radio"
            name="multipleSheets"
            checked={configuration.multipleSheets}
            onChange={() => onConfigurationChange("multipleSheets", true)}
          />
          Oui
        </label>
      </div>

      {!configuration.multipleSheets ? (
        <ImportLayoutFields
          layout={configuration.singleSheetLayout}
          columnFields={columnFields}
          onLayoutChange={(fieldName, value) => onLayoutChange(
            "singleSheetLayout",
            fieldName,
            value
          )}
          onLayoutColumnChange={(fieldName, value) => onLayoutColumnChange(
            "singleSheetLayout",
            fieldName,
            value
          )}
        />
      ) : (
        <MultipleSheetsFields
          configuration={configuration}
          availableSheetNames={availableSheetNames}
          onConfigurationChange={onConfigurationChange}
          onLayoutChange={onLayoutChange}
          onLayoutColumnChange={onLayoutColumnChange}
          onSheetChange={onSheetChange}
          onSheetLayoutChange={onSheetLayoutChange}
          onSheetColumnChange={onSheetColumnChange}
          onAddSheet={onAddSheet}
          onRemoveSheet={onRemoveSheet}
        />
      )}
    </fieldset>
  );
}

/**
 * Affiche la configuration wishlist commune aux modes d'import.
 *
 * @param {Object} props - Etat wishlist et callbacks.
 * @returns {import("react").JSX.Element} Champs wishlist.
 */
function WishlistFields({
  configuration,
  availableSheetNames,
  onWishlistConfigurationChange,
  onWishlistLayoutChange,
  onWishlistLayoutColumnChange,
}) {
  return (
    <section className="wishlistConfiguration" aria-label="Configuration wishlist">
      <div className="segmentedField" role="group" aria-label="Mode wishlist">
        <span>Wishlist</span>
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
            Onglet wishlist
            <SheetNameField
              value={configuration.wishlist.sheetName}
              availableSheetNames={availableSheetNames}
              onChange={(value) => onWishlistConfigurationChange("sheetName", value)}
            />
          </label>
          <ImportLayoutFields
            layout={configuration.wishlist.layout}
            columnFields={["name", "platform", "studio", "release_date"]}
            onLayoutChange={onWishlistLayoutChange}
            onLayoutColumnChange={onWishlistLayoutColumnChange}
          />
        </>
      ) : null}
    </section>
  );
}

const modeLabels = Object.freeze({
  none: "Aucune",
  sheet: "Onglet dedie",
  column: "Colonne",
});

/**
 * Retourne les colonnes de collection a afficher.
 *
 * @param {Object} configuration - Configuration d'import courante.
 * @param {boolean} includePlatformColumn - Indique si la plateforme est une colonne.
 * @returns {string[]} Champs colonnes.
 */
function collectionColumnFields(configuration, includePlatformColumn) {
  const fields = includePlatformColumn
    ? ["name", "platform", "studio", "release_date"]
    : ["name", "studio", "release_date"];
  if (configuration.wishlist.mode === "column") {
    fields.push("wishlist");
  }
  return fields;
}

/**
 * Affiche une selection d'onglet simple.
 *
 * @param {Object} props - Valeur courante, options et callback.
 * @returns {import("react").JSX.Element} Champ onglet.
 */
function SheetNameField({ value, availableSheetNames, onChange }) {
  if (availableSheetNames.length) {
    return (
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Selectionner un onglet</option>
        {availableSheetNames.map((sheetName) => (
          <option key={sheetName} value={sheetName}>{sheetName}</option>
        ))}
      </select>
    );
  }
  return <input type="text" value={value} onChange={(event) => onChange(event.target.value)} />;
}

/**
 * Affiche les champs propres aux modes multi-onglets.
 *
 * @param {Object} props - Etat multi-onglets et callbacks.
 * @returns {import("react").JSX.Element} Champs multi-onglets.
 */
function MultipleSheetsFields({
  configuration,
  availableSheetNames,
  onConfigurationChange,
  onLayoutChange,
  onLayoutColumnChange,
  onSheetChange,
  onSheetLayoutChange,
  onSheetColumnChange,
  onAddSheet,
  onRemoveSheet,
}) {
  return (
    <>
      <label>
        Information portee par l'onglet
        <select value={configuration.sheetInformation} disabled>
          <option value="platform">Plateforme</option>
        </select>
      </label>
      <div className="segmentedField" role="group" aria-label="Layout partage">
        <span>Memes plages sur chaque onglet</span>
        <label>
          <input
            type="radio"
            name="sharedLayout"
            checked={configuration.sharedLayout}
            onChange={() => onConfigurationChange("sharedLayout", true)}
          />
          Oui
        </label>
        <label>
          <input
            type="radio"
            name="sharedLayout"
            checked={!configuration.sharedLayout}
            onChange={() => onConfigurationChange("sharedLayout", false)}
          />
          Non
        </label>
      </div>
      {configuration.sharedLayout ? (
        <>
          <div className="segmentedField" role="group" aria-label="Selection des onglets">
            <span>Selection des onglets</span>
            <label>
              <input
                type="radio"
                name="sheetSelectionMode"
                checked={configuration.sharedSheetLayout.sheetSelectionMode !== "excluded"}
                onChange={() => onLayoutChange(
                  "sharedSheetLayout",
                  "sheetSelectionMode",
                  "included"
                )}
              />
              Inclure
            </label>
            <label>
              <input
                type="radio"
                name="sheetSelectionMode"
                checked={configuration.sharedSheetLayout.sheetSelectionMode === "excluded"}
                onChange={() => onLayoutChange(
                  "sharedSheetLayout",
                  "sheetSelectionMode",
                  "excluded"
                )}
              />
              Exclure
            </label>
          </div>
          <label>
            {configuration.sharedSheetLayout.sheetSelectionMode === "excluded"
              ? "Onglets exclus"
              : "Onglets inclus"}
            <SheetSelectionField
              availableSheetNames={availableSheetNames}
              configuration={configuration}
              onLayoutChange={onLayoutChange}
            />
          </label>
          <ImportLayoutFields
            layout={configuration.sharedSheetLayout}
            columnFields={collectionColumnFields(configuration, false)}
            onLayoutChange={(fieldName, value) => onLayoutChange(
              "sharedSheetLayout",
              fieldName,
              value
            )}
            onLayoutColumnChange={(fieldName, value) => onLayoutColumnChange(
              "sharedSheetLayout",
              fieldName,
              value
            )}
          />
        </>
      ) : (
        <PerSheetFields
          configuration={configuration}
          sheets={configuration.sheets}
          onSheetChange={onSheetChange}
          onSheetLayoutChange={onSheetLayoutChange}
          onSheetColumnChange={onSheetColumnChange}
          onAddSheet={onAddSheet}
          onRemoveSheet={onRemoveSheet}
        />
      )}
    </>
  );
}

/**
 * Affiche la selection d'onglets analysee ou une saisie libre de secours.
 *
 * @param {Object} props - Onglets disponibles, configuration et callback.
 * @returns {import("react").JSX.Element} Champ de selection d'onglets.
 */
function SheetSelectionField({ availableSheetNames, configuration, onLayoutChange }) {
  const isExclusionMode = configuration.sharedSheetLayout.sheetSelectionMode === "excluded";
  const fieldName = isExclusionMode ? "excludedSheets" : "includedSheets";
  const value = configuration.sharedSheetLayout[fieldName];
  if (availableSheetNames.length) {
    const selectedValues = Array.isArray(value) ? value : splitSheetNames(value);
    return (
      <select
        multiple
        value={selectedValues}
        onChange={(event) => onLayoutChange(
          "sharedSheetLayout",
          fieldName,
          Array.from(event.target.selectedOptions).map((option) => option.value)
        )}
      >
        {availableSheetNames.map((sheetName) => (
          <option key={sheetName} value={sheetName}>{sheetName}</option>
        ))}
      </select>
    );
  }
  return (
    <textarea
      rows="2"
      value={value}
      onChange={(event) => onLayoutChange("sharedSheetLayout", fieldName, event.target.value)}
    />
  );
}

/**
 * Decoupe une saisie d'onglets libre.
 *
 * @param {string|string[]} value - Valeur source.
 * @returns {string[]} Noms d'onglets non vides.
 */
function splitSheetNames(value) {
  if (Array.isArray(value)) {
    return value.map((sheetName) => String(sheetName).trim()).filter(Boolean);
  }
  return String(value || "")
    .split(/[\n,]/)
    .map((sheetName) => sheetName.trim())
    .filter(Boolean);
}

/**
 * Affiche les configurations declarees par onglet.
 *
 * @param {Object} props - Onglets et callbacks de modification.
 * @returns {import("react").JSX.Element} Champs par onglet.
 */
function PerSheetFields({
  configuration,
  sheets,
  onSheetChange,
  onSheetLayoutChange,
  onSheetColumnChange,
  onAddSheet,
  onRemoveSheet,
}) {
  return (
    <div className="sheetConfigurationList">
      {sheets.map((sheet, index) => (
        <section className="sheetConfiguration" key={`sheet-${index + 1}`}>
          <div className="sheetConfigurationHeader">
            <h2>Onglet {index + 1}</h2>
            <button
              type="button"
              className="secondaryButton"
              disabled={sheets.length === 1}
              onClick={() => onRemoveSheet(index)}
            >
              Retirer
            </button>
          </div>
          <label>
            Nom de l'onglet
            <input
              type="text"
              value={sheet.sheetName}
              onChange={(event) => onSheetChange(index, "sheetName", event.target.value)}
            />
          </label>
          <ImportLayoutFields
            layout={sheet.layout}
            columnFields={collectionColumnFields(configuration, false)}
            onLayoutChange={(fieldName, value) => onSheetLayoutChange(index, fieldName, value)}
            onLayoutColumnChange={(fieldName, value) => onSheetColumnChange(index, fieldName, value)}
          />
        </section>
      ))}
      <button type="button" className="secondaryButton" onClick={onAddSheet}>
        Ajouter un onglet
      </button>
    </div>
  );
}

export default ImportConfigurationFields;
