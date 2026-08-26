/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de disponibilite du bouton d'import.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import {
  canSubmitImportConfiguration,
  createDefaultImportConfiguration,
} from "../src/hooks/collection/importConfigurationBuilder.js";

test("indique si la configuration d'import peut etre soumise", () => {
  const validConfiguration = createDefaultImportConfiguration();
  assert.equal(canSubmitImportConfiguration(validConfiguration), true);

  const missingRequiredColumnConfiguration = createDefaultImportConfiguration();
  missingRequiredColumnConfiguration.singleSheetLayout.columns.name = "";
  assert.equal(canSubmitImportConfiguration(missingRequiredColumnConfiguration), false);

  const incompleteWishlistConfiguration = createDefaultImportConfiguration();
  incompleteWishlistConfiguration.wishlist.mode = "sheet";
  incompleteWishlistConfiguration.wishlist.sheetName = "";
  assert.equal(canSubmitImportConfiguration(incompleteWishlistConfiguration), false);

  const missingPerSheetWishlistColumnConfiguration = createDefaultImportConfiguration();
  missingPerSheetWishlistColumnConfiguration.multipleSheets = true;
  missingPerSheetWishlistColumnConfiguration.sharedLayout = false;
  missingPerSheetWishlistColumnConfiguration.wishlist.mode = "column";
  missingPerSheetWishlistColumnConfiguration.sheets[0].sheetName = "Switch";
  missingPerSheetWishlistColumnConfiguration.sheets[0].layout.columns.wishlist = "";
  assert.equal(canSubmitImportConfiguration(missingPerSheetWishlistColumnConfiguration), false);
});

test("branche la disponibilite du bouton d'import sur le formulaire", () => {
  const onboardingSource = readFileSync(
    new URL("../src/components/UserCollectionOnboardingView.jsx", import.meta.url),
    "utf8",
  );
  const viewModelSource = readFileSync(
    new URL("../src/hooks/app/useCloudCollectionViewModel.js", import.meta.url),
    "utf8",
  );
  const styleSource = readFileSync(
    new URL("../src/styles/mobile-fixes.css", import.meta.url),
    "utf8",
  );
  const spreadsheetWishlistSource = readFileSync(
    new URL("../src/components/ImportSpreadsheetWishlistFields.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(onboardingSource.includes("scrollBottomButton"), true);
  assert.equal(onboardingSource.includes("isScrollBottomVisible"), true);
  assert.equal(onboardingSource.includes("getBoundingClientRect"), true);
  assert.equal(onboardingSource.includes("canSubmitImport"), true);
  assert.equal(onboardingSource.includes("!hasReusableSavedImportConfiguration"), true);
  assert.equal(onboardingSource.includes("Configuration sauvegardée"), true);
  assert.equal(viewModelSource.includes("hasReusableSavedImportConfiguration"), true);
  assert.equal(viewModelSource.includes("canSubmitImport"), true);
  assert.equal(styleSource.includes("color: #86efac"), true);
  assert.equal(spreadsheetWishlistSource.includes("WishlistColumnFields"), true);
  assert.equal(spreadsheetWishlistSource.includes("onSheetColumnChange(index, \"wishlist\", value)"), true);
});
