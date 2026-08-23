/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-07
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : tests du message de contribution apres import utilisateur.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

test("user import summary displays private collection and admin validation notice", () => {
  const onboardingSource = readFileSync(
    new URL("../src/components/UserCollectionOnboardingView.jsx", import.meta.url),
    "utf8",
  );
  const summarySource = readFileSync(
    new URL("../src/components/ImportSummary.jsx", import.meta.url),
    "utf8",
  );
  const styleSource = readFileSync(
    new URL("../src/styles/collection-onboarding.css", import.meta.url),
    "utf8",
  );

  assert.equal(summarySource.includes("contributionNotice"), true);
  assert.equal(summarySource.includes("importContributionNotice"), true);
  assert.equal(summarySource.includes("Jeux avec erreur"), true);
  assert.equal(summarySource.includes("formatInvalidGamesRatio"), true);
  assert.equal(summarySource.includes("invalidGamesCount > 0"), true);
  assert.equal(styleSource.includes("importErrorCounterAccepted"), true);
  assert.equal(styleSource.includes("importErrorCounterRefused"), true);
  assert.equal(onboardingSource.includes("UserImportContributionNotice"), true);
  assert.equal(onboardingSource.includes("collection privée"), true);
  assert.equal(onboardingSource.includes("Bibliothèque commune après validation"), true);
  assert.equal(onboardingSource.includes("Merci pour votre contribution."), true);
  assert.equal(styleSource.includes(".importContributionNotice"), true);
});

test("user import summary displays readable skipped platform reason", () => {
  const summarySource = readFileSync(
    new URL("../src/components/ImportSummary.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(summarySource.includes("labels[reason] || reason"), true);
  assert.equal(summarySource.includes("groupSkippedGamesByPlatformAndCause"), true);
  assert.equal(summarySource.includes("warning.message || warning.reason"), true);
  assert.equal(summarySource.includes("Jeux non importés"), true);
  assert.equal(summarySource.includes("corriger votre fichier puis le réimporter"), true);
});

test("user import summary prefers simplified platform warnings", () => {
  const summarySource = readFileSync(
    new URL("../src/components/ImportSummary.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(summarySource.includes("user_platform_matches"), true);
  assert.equal(summarySource.includes("user_skipped_games"), true);
  assert.equal(summarySource.includes("groupPlatformWarningsByPlatformAndCause"), true);
  assert.equal(summarySource.includes("platformMatchesCount"), true);
  assert.equal(summarySource.includes("Jeux à vérifier"), true);
  assert.equal(summarySource.includes("formatPlatformRefusal"), true);
  assert.equal(summarySource.includes("invalidAssociatedGames"), true);
  assert.equal(summarySource.includes("Plateforme dans votre fichier"), true);
  assert.equal(summarySource.includes("Plateformes à vérifier par un admin"), true);
  assert.equal(summarySource.includes("ces jeux sont importés"), true);
  assert.equal(summarySource.includes("Jeux en attente de validation admin"), true);
});

test("user import summary marks invalid field values as refused", () => {
  const summarySource = readFileSync(
    new URL("../src/components/ImportSummary.jsx", import.meta.url),
    "utf8",
  );
  const styleSource = readFileSync(
    new URL("../src/styles/collection-onboarding.css", import.meta.url),
    "utf8",
  );

  assert.equal(summarySource.includes("groupInvalidFieldsByField"), true);
  assert.equal(summarySource.includes("Champ ignoré"), true);
  assert.equal(summarySource.includes("Valeurs refusées dans votre fichier"), true);
  assert.equal(summarySource.includes('"{game.value}" Valeur refusée'), true);
  assert.equal(styleSource.includes('list-style-type: "› "'), true);
  assert.equal(summarySource.includes("fetchImportInvalidValueHelp"), true);
  assert.equal(summarySource.includes("Plus d'info"), true);
  assert.equal(summarySource.includes("Masquer"), true);
  assert.equal(summarySource.includes("isOpen: !currentDetails.isOpen"), true);
});

test("user collection api exposes invalid value help endpoint", () => {
  const apiSource = readFileSync(
    new URL("../src/services/UserCollectionApi.js", import.meta.url),
    "utf8",
  );

  assert.equal(apiSource.includes("fetchImportInvalidValueHelp"), true);
  assert.equal(apiSource.includes("/api/users/import/invalid-value-help?"), true);
});
