/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : tests frontend de l'activation et de l'invalidation des sessions GUEST.
 */
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import AppRouting from "../src/appRouting.js";
import AuthApi from "../src/services/AuthApi.js";
import CollectionShareSessionApi from "../src/services/CollectionShareSessionApi.js";
import BackendAvailabilityGuard from "../src/services/BackendAvailabilityGuard.js";

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
  const dispatchedEvents = [];
  global.window = {
    atob: (value) => Buffer.from(value, "base64").toString("binary"),
    dispatchEvent: (event) => dispatchedEvents.push(event.type),
    fetch: async () => new Response("{}", { status: 500 }),
    localStorage: new MemoryStorage(),
    location: {
      pathname: "/about",
      search: "",
    },
  };
  window.dispatchedEvents = dispatchedEvents;
  AuthApi.hasNotifiedExpiredSession = false;
  BackendAvailabilityGuard.consecutiveFailures = 0;
  BackendAvailabilityGuard.blockedUntil = 0;
});

test("echange publiquement le token de lien sans Authorization", async () => {
  let receivedRequest = null;
  window.fetch = async (url, options) => {
    receivedRequest = { url, options };
    return new Response(JSON.stringify({ access_token: "guest-token", expires_in: 3600 }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  const result = await CollectionShareSessionApi.exchangeShareToken("share-link-token");

  assert.equal(result.access_token, "guest-token");
  assert.equal(receivedRequest.url, "/api/auth/collection-share/session");
  assert.deepEqual(JSON.parse(receivedRequest.options.body), { token: "share-link-token" });
  assert.equal(receivedRequest.options.headers.Authorization, undefined);
});

test("reconnait la route de partage comme route publique transitoire", () => {
  window.location.pathname = "/collection/share/token%2Evalue";
  window.localStorage.setItem(AuthApi.authTokenStorageKey, "previous-user-token");

  assert.equal(AppRouting.getCollectionShareTokenFromUrl(), "token.value");
  assert.equal(AppRouting.isPublicPath(window.location.pathname), true);
  assert.equal(AppRouting.getViewFromUrl(), "about");
});

test("redirige en priorite vers la collection puis vers la wishlist autorisee", () => {
  assert.deepEqual(
    CollectionShareSessionApi.resolveGuestDestination({
      permissions: { collection: true, wishlist: true },
    }),
    { path: "/collection", view: "home" }
  );
  assert.deepEqual(
    CollectionShareSessionApi.resolveGuestDestination({
      permissions: { collection: false, wishlist: true },
    }),
    { path: "/wishlist", view: "wishlist" }
  );
  assert.equal(
    CollectionShareSessionApi.resolveGuestDestination({ permissions: {} }),
    null
  );
});

test("un GUEST est deconnecte sur 411 mais pas sur 403", () => {
  const guestToken = createToken({ profile: "GUEST", permissions: { collection: true } });
  AuthApi.storeAccessToken(guestToken, 3600);
  const options = { headers: AuthApi.getAuthorizationHeaders() };

  assert.equal(AuthApi.isExpiredAuthenticatedResponse({ status: 403 }, options), false);
  assert.equal(AuthApi.isExpiredAuthenticatedResponse({ status: 411 }, options), true);

  AuthApi.handleExpiredSession({ status: 411 });

  assert.equal(AuthApi.getAccessToken(), "");
  assert.equal(window.dispatchedEvents.includes(AuthApi.guestShareUnavailableEventName), true);
  assert.equal(window.dispatchedEvents.includes(AuthApi.sessionExpiredEventName), false);
});

test("les profils USER conservent le traitement existant des statuts 401 et 403", () => {
  AuthApi.storeAccessToken(createToken({ profile: "USER" }), 3600);
  const options = { headers: AuthApi.getAuthorizationHeaders() };

  assert.equal(AuthApi.isExpiredAuthenticatedResponse({ status: 401 }, options), true);
  assert.equal(AuthApi.isExpiredAuthenticatedResponse({ status: 403 }, options), true);
  assert.equal(AuthApi.isExpiredAuthenticatedResponse({ status: 411 }, options), false);
});
