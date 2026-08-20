/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-20
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests du mode multi-onglets sans information portee par l'onglet.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildImportConfigurationDescription,
  collectionColumnFields,
  createDefaultImportConfiguration,
} from "../src/hooks/collection/importConfigurationBuilder.js";

test("serialise un layout partage multi-onglets sans information d'onglet", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sheetInformation = "";
  configuration.sharedSheetLayout.columns.platform = "B";

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.equal(description.multiple_sheets_conf.sheet_information, undefined);
  assert.equal(
    description.multiple_sheets_conf.shared_layout.column_information.platform,
    "B"
  );
  assert.equal(collectionColumnFields(configuration, false).includes("platform"), true);
});

test("serialise des layouts par onglet sans information d'onglet", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sharedLayout = false;
  configuration.sheetInformation = "";
  configuration.sheets = [{
    sheetName: "Jeux 2026",
    layout: {
      dataRange: "A1:C50",
      headerRow: "1",
      columns: { name: "A", platform: "B", studio: "C" },
    },
  }];

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.equal(description.multiple_sheets_conf.sheets[0].sheet_information, undefined);
  assert.deepEqual(description.multiple_sheets_conf.sheets[0].column_information, {
    name: "A",
    platform: "B",
    studio: "C",
  });
});

test("refuse le mode sans information quand la colonne plateforme manque", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.multipleSheets = true;
  configuration.sheetInformation = "";

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.equal(description, null);
  assert.equal(errors.includes("Renseignez la colonne platform."), true);
});
