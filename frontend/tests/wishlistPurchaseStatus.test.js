/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-11-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : tests frontend de la vignette d'achat de la liste de souhaits.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import isWishlistPurchaseInProgress from "../src/hooks/games/wishlistBuyStatus.js";

test("detecte un achat en cours depuis chaque information d'achat", () => {
  assert.equal(isWishlistPurchaseInProgress({ "Date d'achat": "2026-11-05" }), true);
  assert.equal(isWishlistPurchaseInProgress({ "Lieu d'achat": "Boutique" }), true);
  assert.equal(isWishlistPurchaseInProgress({ "Prix d'achat": 0 }), true);
});

test("ignore les jeux sans information d'achat exploitable", () => {
  assert.equal(isWishlistPurchaseInProgress(null), false);
  assert.equal(isWishlistPurchaseInProgress({}), false);
  assert.equal(isWishlistPurchaseInProgress({ "Lieu d'achat": "   " }), false);
});

test("rend la vignette sur desktop et dans les cartes mobiles", () => {
  const viewSource = readFileSync(
    new URL("../src/components/WishlistView.jsx", import.meta.url),
    "utf8"
  );
  const styleSource = readFileSync(
    new URL("../src/styles/table-components.css", import.meta.url),
    "utf8"
  );

  assert.equal(viewSource.includes('actionColumnLabel="Statut"'), true);
  assert.equal(viewSource.includes("wishlistPurchaseStatusBadge"), true);
  assert.equal(viewSource.includes("Achat en cours"), true);
  assert.equal(styleSource.includes(".wishlistPurchaseStatusBadge"), true);
  assert.equal(styleSource.includes("table.wishlistGamesTable"), true);
  assert.equal(styleSource.includes("min-width: 7.5rem"), true);
  assert.equal(styleSource.includes("@media (max-width: 760px)"), true);
  assert.equal(styleSource.includes("grid-column: 3"), true);
  assert.equal(styleSource.includes("grid-column: 4"), true);
});
