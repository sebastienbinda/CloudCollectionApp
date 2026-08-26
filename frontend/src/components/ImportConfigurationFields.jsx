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
import { useState } from "react";
import ImportLayoutFields from "./ImportLayoutFields";
import ImportCsvConfigurationFields from "./ImportCsvConfigurationFields";
import ImportCollapsibleSection from "./ImportCollapsibleSection";
import { ImportGlobalOptions } from "./ImportGlobalOptions";
import ImportSpreadsheetWishlistFields from "./ImportSpreadsheetWishlistFields";
import {
  collectionColumnFields,
  collectionRequiredFields,
} from "../hooks/collection/importConfigurationBuilder";
import { hasSpreadsheetImportColumn } from "../hooks/collection/importGlobalOptionsVisibility";

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
  onCsvMappingChange,
  onAddSheet,
  onRemoveSheet,
}) {
  if (configuration.fileType === "csv") {
    return (
      <ImportCsvConfigurationFields
        configuration={configuration}
        availableColumnNames={availableSheetNames}
        disabled={disabled}
        onConfigurationChange={onConfigurationChange}
        onCsvMappingChange={onCsvMappingChange}
        onWishlistConfigurationChange={onWishlistConfigurationChange}
      />
    );
  }

  const columnFields = collectionColumnFields(configuration, !configuration.multipleSheets);
  const showPriceUnit = hasSpreadsheetImportColumn(configuration, "purchase_price");
  const showRatingBase = hasSpreadsheetImportColumn(configuration, "grade");

  return (
    <>
      <ImportCollapsibleSection title="1. Structure du fichier" description="Onglets et organisation du classeur.">
        <FileStructureFields configuration={configuration} disabled={disabled} availableSheetNames={availableSheetNames} onConfigurationChange={onConfigurationChange} onLayoutChange={onLayoutChange} />
      </ImportCollapsibleSection>
      <ImportCollapsibleSection title="2. Colonnes et plage de données" description="Emplacement des lignes et des informations à importer.">
        <fieldset className="importConfiguration" disabled={disabled}>
          <legend>Colonnes et plage de données</legend>
          <p className="importConfigurationIntro">
            Les colonnes marquées avec un astérisque sont indispensables pour créer votre collection.
          </p>
          {!configuration.multipleSheets ? (
            <ImportLayoutFields
              layout={configuration.singleSheetLayout}
              columnFields={columnFields}
              requiredFields={["name", "platform"]}
              onLayoutChange={(fieldName, value) => onLayoutChange("singleSheetLayout", fieldName, value)}
              onLayoutColumnChange={(fieldName, value) => onLayoutColumnChange("singleSheetLayout", fieldName, value)}
            />
          ) : (
            <MultipleSheetsLayoutFields
              configuration={configuration}
              onConfigurationChange={onConfigurationChange}
              onLayoutChange={onLayoutChange}
              onLayoutColumnChange={onLayoutColumnChange}
              onSheetChange={onSheetChange}
              onSheetLayoutChange={onSheetLayoutChange}
              onSheetColumnChange={onSheetColumnChange}
            />
          )}
        </fieldset>
      </ImportCollapsibleSection>
      <ImportCollapsibleSection title="3. Liste de souhaits" description="Source éventuelle des jeux souhaités.">
        <ImportSpreadsheetWishlistFields
          configuration={configuration}
          availableSheetNames={availableSheetNames}
          disabled={disabled}
          onLayoutColumnChange={onLayoutColumnChange}
          onSheetColumnChange={onSheetColumnChange}
          onWishlistConfigurationChange={onWishlistConfigurationChange}
          onWishlistLayoutChange={onWishlistLayoutChange}
          onWishlistLayoutColumnChange={onWishlistLayoutColumnChange}
        />
      </ImportCollapsibleSection>
      {showPriceUnit || showRatingBase ? (
      <ImportCollapsibleSection title="4. Options de prix et de note" description="Affichées seulement si les colonnes liées sont configurées.">
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
 * Affiche le choix des onglets a importer avec une configuration partagee.
 *
 * @param {Object} props - Etat et callbacks de selection des onglets.
 * @returns {import("react").JSX.Element} Champs de selection des onglets.
 * @throws {void} Ne leve pas d'exception.
 */
function SheetSelectionFields({ availableSheetNames, configuration, onLayoutChange }) {
  const selectionMode = configuration.sharedSheetLayout.sheetSelectionMode;
  return (
    <>
      <div className="segmentedField" role="group" aria-label="Sélection des onglets">
        <span>Onglets à importer</span>
        <label>
          <input
            type="radio"
            name="sheetSelectionMode"
            checked={selectionMode === "all"}
            onChange={() => onLayoutChange("sharedSheetLayout", "sheetSelectionMode", "all")}
          />
          Tous
        </label>
        <label>
          <input
            type="radio"
            name="sheetSelectionMode"
            checked={selectionMode === "included"}
            onChange={() => onLayoutChange("sharedSheetLayout", "sheetSelectionMode", "included")}
          />
          Choisir les onglets de collection
        </label>
        <label>
          <input
            type="radio"
            name="sheetSelectionMode"
            checked={selectionMode === "excluded"}
            onChange={() => onLayoutChange("sharedSheetLayout", "sheetSelectionMode", "excluded")}
          />
          Tout importer sauf certains onglets
        </label>
        <p className="segmentedFieldHelp">
          Sélectionnez uniquement les onglets contenant les jeux de votre collection.
          Un onglet dédié à la liste de souhaits doit être exclu ici, puis configuré
          dans la section Liste de souhaits.
        </p>
      </div>
      {selectionMode === "all" ? null : (
      <label>
        {selectionMode === "excluded"
          ? "Onglets exclus"
          : "Onglets inclus"}
        <SheetSelectionField
          availableSheetNames={availableSheetNames}
          configuration={configuration}
          onLayoutChange={onLayoutChange}
        />
        <span className="fieldHelpText">
          {selectionMode === "excluded"
            ? "Listez les onglets à ignorer, notamment un onglet dédié à la liste de souhaits. Laissez vide pour importer tous les onglets détectés."
            : "Listez seulement les onglets qui contiennent les jeux de votre collection, sans l'onglet dédié à la liste de souhaits."}
        </span>
      </label>
      )}
    </>
  );
}

/**
 * Affiche la section de structure du fichier tableur.
 *
 * @param {Object} props - Etat de structure et callbacks.
 * @returns {import("react").JSX.Element} Champs de structure.
 * @throws {void} Ne leve pas d'exception.
 */
function FileStructureFields({
  configuration,
  disabled,
  availableSheetNames,
  onConfigurationChange,
  onLayoutChange,
}) {
  const singleSheetName = availableSheetNames.length === 1 ? availableSheetNames[0] : "";
  return (
    <fieldset className="importConfiguration" disabled={disabled}>
      <legend>Structure du fichier</legend>
      {configuration.multipleSheets ? (
        <>
          <label>
            Le nom de chaque onglet correspond à *
            <select
              value={configuration.sheetInformation}
              onChange={(event) => onConfigurationChange("sheetInformation", event.target.value)}
            >
              <option value="platform">Plateforme</option>
              <option value="">Aucune information</option>
            </select>
            <span className="fieldHelpText">
              {configuration.sheetInformation === "platform"
                ? "Utilisez ce mode quand chaque onglet regroupe les jeux d'une plateforme, par exemple un onglet Switch et un onglet PlayStation 2."
                : "Utilisez ce mode quand le nom des onglets ne porte aucune information. La colonne Plateforme devient obligatoire dans chaque configuration d'onglet."}
            </span>
          </label>
          <SheetSelectionFields
            availableSheetNames={availableSheetNames}
            configuration={configuration}
            onLayoutChange={onLayoutChange}
          />
        </>
      ) : (
        <p className="importConfigurationIntro">
          Aucune configuration de structure n'est nécessaire car le fichier ne contient qu'un seul onglet
          {singleSheetName ? ` : ${singleSheetName}` : ""}.
        </p>
      )}
    </fieldset>
  );
}

/**
 * Affiche les champs de colonnes propres aux modes multi-onglets.
 *
 * @param {Object} props - Etat multi-onglets et callbacks.
 * @returns {import("react").JSX.Element} Champs de colonnes multi-onglets.
 * @throws {void} Ne leve pas d'exception.
 */
function MultipleSheetsLayoutFields({
  configuration,
  onConfigurationChange,
  onLayoutChange,
  onLayoutColumnChange,
  onSheetChange,
  onSheetLayoutChange,
  onSheetColumnChange,
}) {
  return (
    <>
      <div className="segmentedField" role="group" aria-label="Layout partage">
        <span>Mêmes plages sur chaque onglet</span>
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
        <p className="segmentedFieldHelp">
          Oui : configurez une seule plage de données et les mêmes colonnes pour tous les onglets
          importés. Non : configurez séparément la plage et les colonnes de chaque onglet.
        </p>
      </div>
      {configuration.sharedLayout ? (
        <ImportLayoutFields
          layout={configuration.sharedSheetLayout}
          columnFields={collectionColumnFields(configuration, false)}
          requiredFields={collectionRequiredFields(
            configuration,
            configuration.sheetInformation !== "platform"
          )}
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
      ) : (
        <PerSheetFields
          configuration={configuration}
          sheets={configuration.sheets}
          onSheetChange={onSheetChange}
          onSheetLayoutChange={onSheetLayoutChange}
          onSheetColumnChange={onSheetColumnChange}
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
    const visibleRows = availableSheetNames.length > 4 ? 8 : 4;
    return (
      <select
        multiple
        size={visibleRows}
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
}) {
  const [activeSheetIndex, setActiveSheetIndex] = useState(0);
  const activeIndex = Math.min(activeSheetIndex, Math.max(sheets.length - 1, 0));
  const activeSheet = sheets[activeIndex];
  if (!activeSheet) {
    return (
      <p className="segmentedFieldHelp">
        Sélectionnez les onglets de collection dans la section Structure du fichier.
      </p>
    );
  }
  return (
    <div className="sheetConfigurationList">
      <div className="sheetConfigurationTabs" role="tablist" aria-label="Onglets à configurer">
        {sheets.map((sheet, index) => (
          <button
            type="button"
            role="tab"
            className={index === activeIndex ? "activeSheetTab" : ""}
            aria-selected={index === activeIndex}
            key={sheet.sheetName || `sheet-${index + 1}`}
            onClick={() => setActiveSheetIndex(index)}
          >
            {sheet.sheetName || `Onglet ${index + 1}`}
          </button>
        ))}
      </div>
      <section className="sheetConfiguration" role="tabpanel">
        <div className="sheetConfigurationHeader">
          <h2>{activeSheet.sheetName || `Onglet ${activeIndex + 1}`}</h2>
        </div>
        <input type="hidden" value={activeSheet.sheetName} onChange={(event) => onSheetChange(activeIndex, "sheetName", event.target.value)} />
        <ImportLayoutFields
          layout={activeSheet.layout}
          columnFields={collectionColumnFields(configuration, false)}
          requiredFields={collectionRequiredFields(
            configuration,
            configuration.sheetInformation !== "platform"
          )}
          onLayoutChange={(fieldName, value) => onSheetLayoutChange(activeIndex, fieldName, value)}
          onLayoutColumnChange={(fieldName, value) => onSheetColumnChange(activeIndex, fieldName, value)}
        />
      </section>
    </div>
  );
}

export default ImportConfigurationFields;
