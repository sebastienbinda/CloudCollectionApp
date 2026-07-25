/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-25
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de la consultation collection toutes plateformes.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { beforeEach, test } from "node:test";
import AuthApi from "../src/services/AuthApi.js";
import BackendAvailabilityGuard from "../src/services/BackendAvailabilityGuard.js";
import VideoGamesApi from "../src/services/VideoGamesApi.js";

class MemoryStorage {
  /** Initialise un stockage navigateur en memoire. */
  constructor() {
    this.values = new Map();
  }

  /** @returns {string|null} Valeur stockee ou absence. */
  getItem(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  }

  /** @returns {void} Stocke une valeur textuelle. */
  setItem(key, value) {
    this.values.set(key, String(value));
  }

  /** @returns {void} Supprime une valeur. */
  removeItem(key) {
    this.values.delete(key);
  }
}

beforeEach(() => {
  global.window = {
    atob: (value) => Buffer.from(value, "base64").toString("binary"),
    dispatchEvent: () => {},
    fetch: async () => new Response("{}", { status: 500 }),
    localStorage: new MemoryStorage(),
  };
  AuthApi.storeAccessToken("user-token", 3600);
  BackendAvailabilityGuard.consecutiveFailures = 0;
  BackendAvailabilityGuard.blockedUntil = 0;
});

test("charge les jeux toutes plateformes sans parametre platform_id", async () => {
  let receivedUrl = "";
  window.fetch = async (url) => {
    receivedUrl = url;
    return Response.json({ games: [] });
  };

  await VideoGamesApi.fetchGames({ wishlist: false, sort: "name,asc" });

  assert.equal(receivedUrl, "/collections/videogames/games/search?wishlist=false&sort=name%2Casc");
  assert.equal(receivedUrl.includes("platform_id"), false);
});

test("expose une entree collection globale dans les listes de plateformes", () => {
  const homeSource = readFileSync(new URL("../src/components/HomeView.jsx", import.meta.url), "utf8");
  const detailSource = readFileSync(
    new URL("../src/components/PlatformDetailView.jsx", import.meta.url),
    "utf8"
  );
  const switchSource = readFileSync(
    new URL("../src/components/AppViewSwitch.jsx", import.meta.url),
    "utf8"
  );
  const navigationSource = readFileSync(
    new URL("../src/hooks/navigation/useAppNavigation.js", import.meta.url),
    "utf8"
  );
  const homeStyleSource = readFileSync(new URL("../src/styles/home.css", import.meta.url), "utf8");
  const libraryStyleSource = readFileSync(
    new URL("../src/styles/library.css", import.meta.url),
    "utf8"
  );

  assert.equal(homeSource.includes("Toutes les plateformes"), true);
  assert.equal(homeSource.includes("onOpenPlatform(\"\")"), true);
  assert.equal(homeSource.includes("Prix total"), true);
  assert.equal(homeSource.includes("Prix moyen"), true);
  assert.equal(homeSource.includes("Nombre de jeux"), false);
  assert.equal(homeSource.includes("Filtre"), false);
  assert.equal(homeStyleSource.includes(".platformCardAllGames"), true);
  assert.equal(homeStyleSource.includes("background: #f0fdf4"), true);
  assert.equal(detailSource.includes("<option value=\"\">Toutes les plateformes</option>"), true);
  assert.equal(detailSource.includes("Toutes plateformes confondues"), true);
  assert.equal(detailSource.includes("mobileCollectionSortButton"), true);
  assert.equal(detailSource.includes("<SortIcon column={activeSortLabel} sortConfig={sortConfig} />"), true);
  assert.equal(detailSource.includes("mobileCollectionSortMenu"), true);
  assert.equal(detailSource.includes("Critere de tri"), true);
  assert.equal(libraryStyleSource.includes(".mobileCollectionSortControl"), true);
  assert.equal(libraryStyleSource.includes(".mobileCollectionSortMenuHeader"), true);
  assert.equal(libraryStyleSource.includes("display: none"), true);
  assert.equal(libraryStyleSource.includes("display: block"), true);
  assert.equal(switchSource.includes("Boolean(props.selectedPlatform)"), true);
  assert.equal(navigationSource.includes('url.pathname = "/collection"'), true);
});
