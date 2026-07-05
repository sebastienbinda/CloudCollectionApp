/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests de l'indicateur de detail d'un jeu associe a l'utilisateur.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import { buildGameDetailOwnershipIndicator } from "../src/gameDetailOwnershipIndicator.js";
import VideoGamesApi from "../src/services/VideoGamesApi.js";

test("affiche l'indicateur wishlist quand le jeu associe est dans la liste de souhaits", () => {
  const indicator = buildGameDetailOwnershipIndicator(true, true);

  assert.equal(indicator.label, "Dans votre liste de souhaits");
  assert.equal(indicator.ariaLabel, "Jeu dans votre liste de souhaits");
  assert.match(indicator.className, /Wishlist/);
});

test("conserve l'indicateur collection quand le jeu associe n'est pas en wishlist", () => {
  const indicator = buildGameDetailOwnershipIndicator(true, false);

  assert.equal(indicator.label, "Vous possedez ce jeu");
  assert.equal(indicator.className, "gameCollectionOwnershipIndicator");
});

test("masque l'indicateur quand le jeu n'est pas associe a l'utilisateur", () => {
  assert.equal(buildGameDetailOwnershipIndicator(false, true), null);
});

test("normalise l'attribut wishlist des jeux de collection", () => {
  const [wishlistedGame, ownedGame] = VideoGamesApi.normalizeCollectionGames([
    { id: 7, name: "Chrono", wishlist: true },
    { id: 8, name: "Sonic", wishlist: false },
  ]);

  assert.equal(wishlistedGame.wishlist, true);
  assert.equal(ownedGame.wishlist, false);
});
