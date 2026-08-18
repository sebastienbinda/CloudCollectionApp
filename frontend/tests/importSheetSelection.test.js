/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-18
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de deduction des onglets d'import de collection.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  resolveCollectionSheetNames,
  synchronizePerSheetConfigurations,
} from "../src/hooks/collection/importSheetSelection.js";
import { createDefaultImportConfiguration } from "../src/hooks/collection/importConfigurationBuilder.js";

test("deduit les onglets de collection depuis les onglets inclus", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.sharedSheetLayout.includedSheets = "Switch, PlayStation 2\nGameCube";

  assert.deepEqual(
    resolveCollectionSheetNames(["Switch", "Wishlist"], configuration.sharedSheetLayout),
    ["Switch", "PlayStation 2", "GameCube"]
  );
});

test("deduit les onglets de collection en excluant les onglets non collection", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.sharedSheetLayout.sheetSelectionMode = "excluded";
  configuration.sharedSheetLayout.excludedSheets = ["Wishlist", "Sommaire"];

  assert.deepEqual(
    resolveCollectionSheetNames(["Switch", "Wishlist", "Sommaire", "GameCube"], configuration.sharedSheetLayout),
    ["Switch", "GameCube"]
  );
});

test("synchronise les configurations par onglet en conservant les saisies existantes", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.sheets = [
    {
      sheetName: "Switch",
      sheetInformation: "platform",
      layout: { dataRange: "B2:D8", headerRow: "2", columns: { name: "B" } },
    },
  ];
  configuration.sharedSheetLayout.includedSheets = ["Switch", "GameCube"];

  const synchronizedConfiguration = synchronizePerSheetConfigurations(
    configuration,
    ["Switch", "GameCube", "Wishlist"],
    createDefaultImportConfiguration().sheets[0]
  );

  assert.deepEqual(
    synchronizedConfiguration.sheets.map((sheet) => sheet.sheetName),
    ["Switch", "GameCube"]
  );
  assert.equal(synchronizedConfiguration.sheets[0].layout.dataRange, "B2:D8");
  assert.equal(synchronizedConfiguration.sheets[0].layout.columns.name, "B");
  assert.equal(synchronizedConfiguration.sheets[1].layout.columns.name, "A");
});
