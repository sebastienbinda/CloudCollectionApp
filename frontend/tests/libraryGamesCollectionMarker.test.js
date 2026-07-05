/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : tests frontend de l'enrichissement collection des jeux Bibliotheque.
 */
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import AuthApi from "../src/services/AuthApi.js";
import BackendAvailabilityGuard from "../src/services/BackendAvailabilityGuard.js";
import LibraryApi from "../src/services/LibraryApi.js";

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

function createToken(payload) {
  return `${Buffer.from(JSON.stringify(payload)).toString("base64url")}.signature`;
}

beforeEach(() => {
  global.window = {
    atob: (value) => Buffer.from(value, "base64").toString("binary"),
    dispatchEvent: () => {},
    fetch: async () => new Response("{}", { status: 500 }),
    localStorage: new MemoryStorage(),
  };
  AuthApi.hasNotifiedExpiredSession = false;
  BackendAvailabilityGuard.consecutiveFailures = 0;
  BackendAvailabilityGuard.blockedUntil = 0;
});

test("envoie un Bearer frais pour enrichir la liste publique des jeux", async () => {
  let receivedRequest = null;
  window.fetch = async (url, options) => {
    receivedRequest = { url, options };
    return new Response(JSON.stringify({ page: {}, games: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  AuthApi.storeAccessToken(createToken({ profile: "USER" }), 3600);

  await LibraryApi.fetchGames();

  assert.equal(receivedRequest.url, "/api/library/games");
  assert.equal(receivedRequest.options.headers.Authorization.startsWith("Bearer "), true);
});

test("n'envoie pas de Bearer expire pour conserver la lecture publique", async () => {
  let receivedRequest = null;
  window.fetch = async (url, options) => {
    receivedRequest = { url, options };
    return new Response(JSON.stringify({ page: {}, games: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  AuthApi.storeAccessToken(createToken({ profile: "USER" }), -1);

  await LibraryApi.fetchGames();

  assert.equal(receivedRequest.url, "/api/library/games");
  assert.equal(receivedRequest.options.headers, undefined);
});
