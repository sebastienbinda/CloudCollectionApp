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
  assert.equal(onboardingSource.includes("UserImportContributionNotice"), true);
  assert.equal(onboardingSource.includes("collection privee"), true);
  assert.equal(onboardingSource.includes("Bibliotheque commune apres validation"), true);
  assert.equal(onboardingSource.includes("Merci pour votre contribution."), true);
  assert.equal(styleSource.includes(".importContributionNotice"), true);
});
