/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-10
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend des boutons de retour contextuels.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

test("la page plateforme collection expose un retour vers les plateformes", () => {
  const componentSource = readFileSync(
    new URL("../src/components/PlatformDetailView.jsx", import.meta.url),
    "utf8"
  );
  const switchSource = readFileSync(
    new URL("../src/components/AppViewSwitch.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(componentSource.includes("Retour aux plateformes"), true);
  assert.equal(componentSource.includes("onBackToPlatforms"), true);
  assert.equal(switchSource.includes("onBackToPlatforms={props.goHome}"), true);
});

test("les listes Bibliotheque exposent un retour vers la Bibliotheque", () => {
  const componentSource = readFileSync(
    new URL("../src/components/LibraryEntityListView.jsx", import.meta.url),
    "utf8"
  );
  const switchSource = readFileSync(
    new URL("../src/components/AppViewSwitch.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(componentSource.includes("Retour a la Bibliotheque"), true);
  assert.equal(componentSource.includes("onBackToLibrary"), true);
  assert.equal(
    switchSource.includes("onBackToLibrary={props.openLibrary}"),
    true
  );
  assert.equal(switchSource.includes("renderLibraryList(props, \"Plateformes\""), true);
  assert.equal(switchSource.includes("renderLibraryList(props, \"Studios\""), true);
  assert.equal(switchSource.includes("renderLibraryList(props, \"Jeux\""), true);
});
