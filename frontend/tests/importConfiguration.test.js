/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-28
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de configuration d'import de collection.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildImportConfigurationDescription,
  collectionColumnFields,
  createDefaultImportConfiguration,
  wishlistSheetColumnFields,
} from "../src/hooks/collection/importConfigurationBuilder.js";
import {
  hasCsvImportColumn,
  hasSpreadsheetImportColumn,
} from "../src/hooks/collection/importGlobalOptionsVisibility.js";
import { readFileSync } from "node:fs";

test("expose les memes informations optionnelles pour la collection et la wishlist dediee", () => {
  const configuration = createDefaultImportConfiguration();

  assert.deepEqual(wishlistSheetColumnFields(), [
    "name",
    "platform",
    "studio",
    "release_date",
    "purchase_price",
    "buy_location",
    "buy_date",
    "grade",
    "condition",
    "has_manual",
    "is_collector",
    "has_steelbook",
    "is_digital",
    "region",
    "description",
  ]);
  assert.deepEqual(
    collectionColumnFields(configuration, true).filter((field) => field !== "wishlist"),
    wishlistSheetColumnFields()
  );
});

test("serialise les colonnes optionnelles wishlist sans fusionner celles de la collection", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.wishlist = {
    ...configuration.wishlist,
    mode: "sheet",
    sheetName: "Wishlist",
    layout: {
      ...configuration.wishlist.layout,
      columns: {
        ...configuration.wishlist.layout.columns,
        purchase_price: "E",
        buy_location: "F",
      },
    },
  };
  configuration.singleSheetLayout = {
    ...configuration.singleSheetLayout,
    columns: {
      ...configuration.singleSheetLayout.columns,
      grade: "G",
    },
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.equal(description.wishlist.column_information.purchase_price, "E");
  assert.equal(description.wishlist.column_information.buy_location, "F");
  assert.equal(description.wishlist.column_information.grade, undefined);
  assert.equal(description.single_sheet_conf.column_information.grade, "G");
  assert.equal(description.rating_base, 10);
  assert.equal(description.single_sheet_conf.column_information.purchase_price, undefined);
});

test("serialise une configuration Excel avec le meme contrat tableur que l'ODS", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.fileType = "excel_xlsx";

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.equal(description.file_type, "excel_xlsx");
  assert.equal(description.single_sheet_conf.data_range, "A1:D200");
  assert.equal(description.single_sheet_conf.column_information.name, "A");
  assert.equal(description.single_sheet_conf.column_information.platform, "B");
});

test("l'onboarding d'import detecte le type de fichier et guide la configuration", () => {
  const onboardingSource = readFileSync(
    new URL("../src/components/UserCollectionOnboardingView.jsx", import.meta.url),
    "utf8",
  );
  const layoutSource = readFileSync(
    new URL("../src/components/ImportLayoutFields.jsx", import.meta.url),
    "utf8",
  );
  const configurationSource = readFileSync(
    new URL("../src/components/ImportConfigurationFields.jsx", import.meta.url),
    "utf8",
  );
  const csvSource = readFileSync(
    new URL("../src/components/ImportCsvConfigurationFields.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(onboardingSource.includes("Type de fichier"), false);
  assert.equal(onboardingSource.includes("Fournir votre fichier de collection"), true);
  assert.equal(onboardingSource.includes("Configurer votre import"), true);
  assert.equal(onboardingSource.includes("collectionSelectedFile"), true);
  assert.equal(onboardingSource.includes("Changer le fichier de collection"), true);
  assert.equal(onboardingSource.includes("Format detecte"), false);
  assert.equal(onboardingSource.includes("Excel, LibreOffice ou CSV"), true);
  assert.equal(onboardingSource.includes("ODS, Excel XLSX ou CSV"), false);
  assert.equal(onboardingSource.includes("Le fichier doit contenir une ligne par jeu"), true);
  assert.equal(onboardingSource.includes("Il peut comporter"), true);
  assert.equal(onboardingSource.includes("liste de souhaits peut être indiquée"), true);
  assert.equal(layoutSource.includes("requiredColumnField"), true);
  assert.equal(layoutSource.includes("<ImportFieldHelp fieldName={fieldName} />"), true);
  assert.equal(csvSource.includes("<ImportFieldHelp fieldName={fieldName} />"), true);
  assert.equal(layoutSource.includes("FIELD_LABELS"), true);
  assert.equal(configurationSource.includes("<span>Wishlist</span>"), false);
  assert.equal(csvSource.includes("<span>Wishlist</span>"), false);
  assert.equal(configurationSource.includes("wishlistConfigurationIntro"), true);
  assert.equal(layoutSource.includes("Liste de souhaits"), true);
  assert.equal(csvSource.includes("Liste de souhaits"), true);
  assert.equal(csvSource.includes("wishlistConfigurationIntro"), true);
  assert.equal(
    configurationSource.includes("Votre fichier contient-il plusieurs onglets à importer ?"),
    true
  );
  assert.equal(configurationSource.includes("Le nom de chaque onglet correspond à"), true);
});

test("les aides d'import centralisent les listes longues des champs controles", () => {
  const fieldHelpSource = readFileSync(
    new URL("../src/components/ImportFieldHelp.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(fieldHelpSource.includes("function ImportFieldHelp"), true);
  assert.equal(fieldHelpSource.includes("Voir les valeurs acceptées"), true);
  assert.equal(fieldHelpSource.includes("État physique du jeu"), true);
  assert.equal(fieldHelpSource.includes("Les libellés proches sont rapprochés automatiquement"), true);
  assert.equal(fieldHelpSource.includes("Mauvais, Très mauvais, Abîmé"), false);
  assert.equal(fieldHelpSource.includes("Factory sealed, Unused"), false);
  assert.equal(fieldHelpSource.includes("\"JAP\", \"US\", \"EU-FR\", \"EU-UK\""), true);
  assert.equal(fieldHelpSource.includes("\"PAL - FR\", \"PAL - EUR\", \"EUR - PAL\""), true);
  assert.equal(fieldHelpSource.includes("\"Oui\", \"O\", \"Yes\", \"Y\", \"True\""), true);
  assert.equal(fieldHelpSource.includes("\"Non\", \"N\", \"No\", \"False\""), true);
});

test("affiche les options globales seulement quand prix ou note sont configures", () => {
  const configuration = createDefaultImportConfiguration();

  assert.equal(hasSpreadsheetImportColumn(configuration, "purchase_price"), false);
  assert.equal(hasSpreadsheetImportColumn(configuration, "grade"), false);

  configuration.singleSheetLayout.columns.purchase_price = "E";
  assert.equal(hasSpreadsheetImportColumn(configuration, "purchase_price"), true);
  assert.equal(hasSpreadsheetImportColumn(configuration, "grade"), false);

  configuration.singleSheetLayout.columns.purchase_price = "";
  configuration.wishlist.mode = "sheet";
  configuration.wishlist.layout.columns.grade = "F";
  assert.equal(hasSpreadsheetImportColumn(configuration, "grade"), true);

  configuration.wishlist.mode = "none";
  assert.equal(hasSpreadsheetImportColumn(configuration, "grade"), false);

  configuration.fileType = "csv";
  configuration.csvMapping.purchase_price = "Prix";
  assert.equal(hasCsvImportColumn(configuration, "purchase_price"), true);
  assert.equal(hasCsvImportColumn(configuration, "grade"), false);
});

test("ignore la base de notation invalide quand aucune colonne note n'est configuree", () => {
  const spreadsheetConfiguration = createDefaultImportConfiguration();
  spreadsheetConfiguration.ratingBase = "0";

  const spreadsheetResult = buildImportConfigurationDescription(spreadsheetConfiguration);

  assert.deepEqual(spreadsheetResult.errors, []);
  assert.equal(spreadsheetResult.description.rating_base, 10);

  const csvConfiguration = createDefaultImportConfiguration();
  csvConfiguration.fileType = "csv";
  csvConfiguration.csvMapping.name = "Jeu";
  csvConfiguration.csvMapping.platform = "Plateforme";
  csvConfiguration.ratingBase = "0";

  const csvResult = buildImportConfigurationDescription(csvConfiguration);

  assert.deepEqual(csvResult.errors, []);
  assert.equal(csvResult.description.rating_base, 10);
});
