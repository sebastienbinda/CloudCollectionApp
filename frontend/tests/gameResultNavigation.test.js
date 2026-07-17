/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de la navigation precedent/suivant entre jeux.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildGameResultNavigationState,
  findAdjacentGameInCurrentRows,
  getAdjacentPageToLoad,
  normalizeGameResultContext,
  selectAdjacentGameFromLoadedPage,
} from "../src/hooks/navigation/gameResultNavigation.js";

test("calcule la position et les disponibilites dans une liste chargee", () => {
  const context = normalizeGameResultContext({
    rows: [{ id: 10 }, { id: 20 }, { id: 30 }],
  });

  assert.deepEqual(buildGameResultNavigationState(context, 20), {
    canOpenPreviousGame: true,
    canOpenNextGame: true,
    positionLabel: "2 / 3",
  });
  assert.equal(findAdjacentGameInCurrentRows(context, 20, "previous").id, 10);
  assert.equal(findAdjacentGameInCurrentRows(context, 20, "next").id, 30);
});

test("desactive la navigation quand le jeu courant n'appartient pas au contexte", () => {
  const context = normalizeGameResultContext({
    rows: [{ id: 10 }, { id: 20 }],
  });

  assert.deepEqual(buildGameResultNavigationState(context, 30), {
    canOpenPreviousGame: false,
    canOpenNextGame: false,
    positionLabel: "",
  });
});

test("detecte la page voisine a charger aux limites d'une page Bibliotheque", () => {
  const context = normalizeGameResultContext({
    rows: [{ id: 30 }, { id: 40 }],
    page: 1,
    size: 2,
    totalElements: 5,
  });

  assert.equal(getAdjacentPageToLoad(context, 30, "previous"), 0);
  assert.equal(getAdjacentPageToLoad(context, 40, "next"), 2);
  assert.equal(selectAdjacentGameFromLoadedPage([{ id: 50 }], "next").id, 50);
  assert.equal(selectAdjacentGameFromLoadedPage([{ id: 10 }, { id: 20 }], "previous").id, 20);
});
