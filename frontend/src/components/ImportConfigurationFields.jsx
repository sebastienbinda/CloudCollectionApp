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

const FIELD_LABELS = Object.freeze({
  name: "Nom du jeu",
  platform: "Plateforme",
  studio: "Studio",
  release_date: "Date de sortie",
});

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
  onAddSheet,
  onRemoveSheet,
}) {
  const columnFields = configuration.multipleSheets ? ["name", "studio", "release_date"] : [
    "name",
    "platform",
    "studio",
    "release_date",
  ];

  return (
    <fieldset className="importConfiguration" disabled={disabled}>
      <legend>Configuration du fichier</legend>
      <label>
        Type de fichier
        <select value={configuration.fileType} disabled>
          <option value="libreoffice_ods">LibreOffice ODS</option>
        </select>
      </label>

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
        <LayoutFields
          layout={configuration.singleSheetLayout}
          layoutName="singleSheetLayout"
          columnFields={columnFields}
          onLayoutChange={onLayoutChange}
          onLayoutColumnChange={onLayoutColumnChange}
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
          <LayoutFields
            layout={configuration.sharedSheetLayout}
            layoutName="sharedSheetLayout"
            columnFields={["name", "studio", "release_date"]}
            onLayoutChange={onLayoutChange}
            onLayoutColumnChange={onLayoutColumnChange}
          />
        </>
      ) : (
        <PerSheetFields
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
          <LayoutFields
            layout={sheet.layout}
            sheetIndex={index}
            columnFields={["name", "studio", "release_date"]}
            onSheetLayoutChange={onSheetLayoutChange}
            onSheetColumnChange={onSheetColumnChange}
          />
        </section>
      ))}
      <button type="button" className="secondaryButton" onClick={onAddSheet}>
        Ajouter un onglet
      </button>
    </div>
  );
}

/**
 * Affiche un layout tableur configurable.
 *
 * @param {Object} props - Layout, champs colonnes et callbacks.
 * @returns {import("react").JSX.Element} Champs de layout.
 */
function LayoutFields({
  layout,
  layoutName,
  sheetIndex = null,
  columnFields,
  onLayoutChange,
  onLayoutColumnChange,
  onSheetLayoutChange,
  onSheetColumnChange,
}) {
  const updateLayout = (fieldName, value) => {
    if (sheetIndex === null) {
      onLayoutChange(layoutName, fieldName, value);
      return;
    }
    onSheetLayoutChange(sheetIndex, fieldName, value);
  };
  const updateColumn = (fieldName, value) => {
    if (sheetIndex === null) {
      onLayoutColumnChange(layoutName, fieldName, value);
      return;
    }
    onSheetColumnChange(sheetIndex, fieldName, value);
  };

  return (
    <div className="layoutFields">
      <label>
        Plage de donnees
        <input
          type="text"
          value={layout.dataRange}
          onChange={(event) => updateLayout("dataRange", event.target.value)}
        />
      </label>
      <label>
        Ligne d'en-tete
        <input
          type="number"
          min="1"
          value={layout.headerRow}
          onChange={(event) => updateLayout("headerRow", event.target.value)}
        />
      </label>
      <div className="columnGrid">
        {columnFields.map((fieldName) => (
          <label key={fieldName}>
            {FIELD_LABELS[fieldName]}
            <input
              type="text"
              value={layout.columns[fieldName] || ""}
              onChange={(event) => updateColumn(fieldName, event.target.value)}
            />
          </label>
        ))}
      </div>
    </div>
  );
}

export default ImportConfigurationFields;
