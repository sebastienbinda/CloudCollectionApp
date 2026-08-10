/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-10
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend des indications d'import CSV admin Bibliotheque.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

test("affiche les indications de configuration CSV admin", () => {
  const viewSource = readFileSync(
    new URL("../src/components/AdminLibraryImportView.jsx", import.meta.url),
    "utf8"
  );
  const styleSource = readFileSync(
    new URL("../src/styles/collection-onboarding.css", import.meta.url),
    "utf8"
  );

  assert.equal(viewSource.includes("Configuration CSV admin attendue"), true);
  assert.equal(viewSource.includes("backend/resources/admin_import_conf.json"), true);
  assert.equal(viewSource.includes("CSV avec extension .csv"), true);
  assert.equal(viewSource.includes("Virgule, point-virgule ou tabulation"), true);
  assert.equal(
    viewSource.includes("1 = Jeu, 2 = Plateforme, 3 = Studio, 4 = Date de sortie"),
    true
  );
  assert.equal(viewSource.includes("Jeu et Plateforme sont obligatoires"), true);
  assert.equal(styleSource.includes(".adminImportConfigurationHelp"), true);
});
