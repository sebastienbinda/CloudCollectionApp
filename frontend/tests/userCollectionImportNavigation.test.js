/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de navigation vers l'import de collection utilisateur.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

test("ouvrir un nouvel import depuis Configuration reinitialise le formulaire", () => {
  const onboardingHookSource = readFileSync(
    new URL("../src/hooks/collection/useUserCollectionOnboarding.js", import.meta.url),
    "utf8",
  );
  const viewModelSource = readFileSync(
    new URL("../src/hooks/app/useCloudCollectionViewModel.js", import.meta.url),
    "utf8",
  );

  assert.equal(
    onboardingHookSource.includes("prepareNewCollectionImport: resetOnboardingState"),
    true,
  );
  assert.equal(viewModelSource.includes("const openNewCollectionImport = () =>"), true);
  assert.equal(
    viewModelSource.includes("userCollectionOnboarding.prepareNewCollectionImport();"),
    true,
  );
  assert.equal(viewModelSource.includes("navigation.openCollectionOnboarding();"), true);
  assert.equal(viewModelSource.includes("openCollectionOnboarding: openNewCollectionImport"), true);
});
