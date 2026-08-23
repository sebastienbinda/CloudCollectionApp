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
  const summarySource = readFileSync(
    new URL("../src/components/ImportSummary.jsx", import.meta.url),
    "utf8",
  );
  const fieldLabelsSource = readFileSync(
    new URL("../src/hooks/collection/importFieldLabels.js", import.meta.url),
    "utf8",
  );
  const spreadsheetWishlistSource = readFileSync(
    new URL("../src/components/ImportSpreadsheetWishlistFields.jsx", import.meta.url),
    "utf8",
  );
  const collapsibleSource = readFileSync(
    new URL("../src/components/ImportCollapsibleSection.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(onboardingSource.includes("Type de fichier"), false);
  assert.equal(onboardingSource.includes("Fournir votre fichier de collection"), true);
  assert.equal(onboardingSource.includes("Configurer votre import"), true);
  assert.equal(onboardingSource.includes("collectionSelectedFile"), true);
  assert.equal(onboardingSource.includes("Changer le fichier de collection"), true);
  assert.equal(onboardingSource.includes("Changer"), true);
  assert.equal(onboardingSource.includes("Format detecte"), false);
  assert.equal(onboardingSource.includes("Excel, LibreOffice ou CSV"), true);
  assert.equal(onboardingSource.includes("ODS, Excel XLSX ou CSV"), false);
  assert.equal(onboardingSource.includes("Le fichier doit contenir une ligne par jeu"), true);
  assert.equal(onboardingSource.includes("Plus d'informations"), true);
  assert.equal(onboardingSource.includes("showFileExpectation"), true);
  assert.equal(onboardingSource.includes("Il peut comporter"), true);
  assert.equal(onboardingSource.includes("liste de souhaits peut être indiquée"), true);
  assert.equal(layoutSource.includes("requiredColumnField"), true);
  assert.equal(layoutSource.includes("première et la dernière cellule du tableau"), true);
  assert.equal(layoutSource.includes("sans les notes ou totaux"), true);
  assert.equal(layoutSource.includes("<ImportFieldHelp fieldName={fieldName} />"), true);
  assert.equal(csvSource.includes("<ImportFieldHelp fieldName={fieldName} />"), true);
  assert.equal(layoutSource.includes("IMPORT_FIELD_LABELS"), true);
  assert.equal(csvSource.includes("IMPORT_FIELD_LABELS"), true);
  assert.equal(summarySource.includes("getImportFieldLabel"), true);
  assert.equal(fieldLabelsSource.includes("Région"), true);
  assert.equal(configurationSource.includes("<span>Wishlist</span>"), false);
  assert.equal(csvSource.includes("<span>Wishlist</span>"), false);
  assert.equal(configurationSource.includes("ImportCollapsibleSection"), true);
  assert.equal(collapsibleSource.includes("<details"), true);
  assert.equal(spreadsheetWishlistSource.includes("wishlistConfigurationIntro"), true);
  assert.equal(fieldLabelsSource.includes("Liste de souhaits"), true);
  assert.equal(csvSource.includes("wishlistConfigurationIntro"), true);
  assert.equal(
    configurationSource.includes("Indiquez si les jeux sont dans un seul tableau"),
    false
  );
  assert.equal(
    configurationSource.includes("Votre fichier contient-il plusieurs onglets à importer ?"),
    false
  );
  assert.equal(
    configurationSource.includes("Aucune configuration de structure n'est nécessaire"),
    true
  );
  assert.equal(configurationSource.includes("singleSheetName"), true);
  assert.equal(configurationSource.includes("name=\"multipleSheets\""), false);
  assert.equal(configurationSource.includes("Le nom de chaque onglet correspond à"), true);
  assert.equal(configurationSource.includes("Tous"), true);
  assert.equal(configurationSource.includes("selectionMode === \"all\" ? null"), true);
  assert.equal(configurationSource.includes("availableSheetNames.length > 4 ? 8 : 4"), true);
  assert.equal(configurationSource.includes("configurez une seule plage de données"), true);
  assert.equal(configurationSource.includes("configurez séparément la plage et les colonnes"), true);
  assert.equal(configurationSource.includes("Onglets à importer"), true);
  assert.equal(configurationSource.includes("Choisir les onglets de collection"), true);
  assert.equal(configurationSource.includes("Tout importer sauf certains onglets"), true);
  assert.equal(configurationSource.includes("Listez les onglets à ignorer"), true);
  assert.equal(configurationSource.includes("Un onglet dédié à la liste de souhaits doit être exclu ici"), true);
  assert.equal(configurationSource.includes("role=\"tablist\""), true);
  assert.equal(configurationSource.includes("activeSheetTab"), true);
});

test("les aides d'import centralisent les listes longues des champs controles", () => {
  const fieldHelpSource = readFileSync(
    new URL("../src/components/ImportFieldHelp.jsx", import.meta.url),
    "utf8",
  );
  const onboardingStyleSource = readFileSync(
    new URL("../src/styles/collection-onboarding.css", import.meta.url),
    "utf8",
  );

  assert.equal(fieldHelpSource.includes("function ImportFieldHelp"), true);
  assert.equal(fieldHelpSource.includes("\"Plus d'info\""), true);
  assert.equal(fieldHelpSource.includes("formatAdditionalHelp"), true);
  assert.equal(fieldHelpSource.includes("État physique du jeu"), true);
  assert.equal(fieldHelpSource.includes("Les libellés proches sont rapprochés automatiquement"), true);
  assert.equal(fieldHelpSource.includes("Exemples : Mauvais, Correct, Bon"), true);
  assert.equal(fieldHelpSource.includes("Factory sealed, Unused"), false);
  assert.equal(fieldHelpSource.includes("\"JAP\", \"US\", \"EU-FR\", \"EU-UK\""), true);
  assert.equal(fieldHelpSource.includes("\"PAL - FR\", \"PAL - EUR\", \"EUR - PAL\""), true);
  assert.equal(fieldHelpSource.includes("\"Oui\", \"O\", \"Yes\", \"Y\", \"True\""), true);
  assert.equal(fieldHelpSource.includes("\"Non\", \"N\", \"No\", \"False\""), true);
  assert.equal(onboardingStyleSource.includes("-webkit-line-clamp: 2"), true);
  assert.equal(onboardingStyleSource.includes(".fieldHelpToggle:hover:not(:disabled)"), true);
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

test("serialise le formulaire tableur mono-onglet avec colonnes optionnelles et wishlist colonne", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.priceUnit = "USD";
  configuration.ratingBase = "20";
  configuration.wishlist.mode = "column";
  configuration.singleSheetLayout = {
    dataRange: "b2:r99",
    headerRow: "2",
    columns: {
      ...configuration.singleSheetLayout.columns,
      name: "b",
      platform: "c",
      studio: "d",
      release_date: "e",
      wishlist: "f",
      purchase_price: "g",
      buy_location: "h",
      buy_date: "i",
      grade: "j",
      condition: "k",
      has_manual: "l",
      is_collector: "m",
      has_steelbook: "n",
      is_digital: "o",
      region: "p",
      description: "q",
    },
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description, {
    file_type: "libreoffice_ods",
    price_unit: "USD",
    rating_base: 20,
    wishlist: { mode: "column" },
    single_sheet_conf: {
      data_range: "B2:R99",
      header_row: 2,
      column_information: {
        name: "B",
        platform: "C",
        wishlist: "F",
        studio: "D",
        release_date: "E",
        purchase_price: "G",
        buy_location: "H",
        buy_date: "I",
        grade: "J",
        condition: "K",
        has_manual: "L",
        is_collector: "M",
        has_steelbook: "N",
        is_digital: "O",
        region: "P",
        description: "Q",
      },
    },
  });
});

test("serialise le formulaire tableur multi-onglets avec layout partage et onglets inclus", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sharedLayout = true;
  configuration.sharedSheetLayout = {
    ...configuration.sharedSheetLayout,
    dataRange: "a3:f42",
    headerRow: "3",
    sheetSelectionMode: "included",
    includedSheets: "Switch, PlayStation 2\nGameCube",
    columns: {
      ...configuration.sharedSheetLayout.columns,
      name: "a",
      studio: "b",
      release_date: "c",
      purchase_price: "d",
      grade: "e",
    },
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description, {
    file_type: "libreoffice_ods",
    price_unit: "EUR",
    rating_base: 10,
    wishlist: { mode: "none" },
    multiple_sheets_conf: {
      sheet_information: "platform",
      shared_layout: {
        data_range: "A3:F42",
        header_row: 3,
        column_information: {
          name: "A",
          studio: "B",
          release_date: "C",
          purchase_price: "D",
          grade: "E",
        },
        included_sheets: ["Switch", "PlayStation 2", "GameCube"],
      },
    },
  });
});

test("serialise le formulaire tableur multi-onglets avec layout partage et onglets exclus", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sharedLayout = true;
  configuration.sharedSheetLayout = {
    ...configuration.sharedSheetLayout,
    sheetSelectionMode: "excluded",
    excludedSheets: ["Sommaire", "Statistiques"],
    columns: {
      ...configuration.sharedSheetLayout.columns,
      name: "a",
      region: "d",
    },
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description.multiple_sheets_conf.shared_layout, {
    data_range: "A1:D200",
    header_row: 1,
    column_information: {
      name: "A",
      studio: "B",
      release_date: "C",
      region: "D",
    },
    excluded_sheets: ["Sommaire", "Statistiques"],
  });
  assert.equal(description.multiple_sheets_conf.shared_layout.included_sheets, undefined);
});

test("serialise le formulaire tableur multi-onglets avec configuration par onglet", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sharedLayout = false;
  configuration.wishlist.mode = "column";
  configuration.sheets = [
    {
      sheetName: "Switch",
      sheetInformation: "platform",
      layout: {
        dataRange: "a1:e10",
        headerRow: "1",
        columns: { name: "a", wishlist: "b", grade: "c" },
      },
    },
    {
      sheetName: "PlayStation 2",
      sheetInformation: "platform",
      layout: {
        dataRange: "b4:h40",
        headerRow: "4",
        columns: { name: "b", wishlist: "c", condition: "d" },
      },
    },
  ];

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description.multiple_sheets_conf, {
    sheets: [
      {
        sheet_name: "Switch",
        sheet_information: "platform",
        data_range: "A1:E10",
        header_row: 1,
        column_information: { name: "A", wishlist: "B", grade: "C" },
      },
      {
        sheet_name: "PlayStation 2",
        sheet_information: "platform",
        data_range: "B4:H40",
        header_row: 4,
        column_information: { name: "B", wishlist: "C", condition: "D" },
      },
    ],
  });
});

test("serialise le formulaire CSV sans liste de souhaits", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.fileType = "csv";
  configuration.csvMapping = {
    ...configuration.csvMapping,
    name: "Nom",
    platform: "Plateforme",
    studio: "Studio",
    purchase_price: "Prix",
    grade: "Note",
  };
  configuration.priceUnit = "JPY";
  configuration.ratingBase = "100";

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description, {
    file_type: "csv",
    price_unit: "JPY",
    rating_base: 100,
    wishlist: { mode: "none" },
    mapping: {
      name: "Nom",
      platform: "Plateforme",
      studio: "Studio",
      purchase_price: "Prix",
      grade: "Note",
    },
  });
});

test("serialise le formulaire CSV avec liste de souhaits portee par une colonne", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.fileType = "csv";
  configuration.wishlist.mode = "column";
  configuration.csvMapping = {
    ...configuration.csvMapping,
    name: "Titre",
    platform: "Console",
    wishlist: "Liste de souhaits",
    release_date: "Sortie",
    condition: "Etat",
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.deepEqual(description, {
    file_type: "csv",
    price_unit: "EUR",
    rating_base: 10,
    wishlist: { mode: "column" },
    mapping: {
      name: "Titre",
      platform: "Console",
      wishlist: "Liste de souhaits",
      release_date: "Sortie",
      condition: "Etat",
    },
  });
});
