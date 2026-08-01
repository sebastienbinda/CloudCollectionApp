/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-01
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend du workflow admin de validation des jeux.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { beforeEach, test } from "node:test";
import AuthApi from "../src/services/AuthApi.js";
import BackendAvailabilityGuard from "../src/services/BackendAvailabilityGuard.js";
import BackendRouteAccessService from "../src/services/BackendRouteAccessService.js";
import LibraryAdminApi from "../src/services/LibraryAdminApi.js";
import LibraryApi from "../src/services/LibraryApi.js";
import { getLibraryGameColumns } from "../src/hooks/library/libraryGameColumns.js";
import { buildLibraryResetConfirmationMessage } from "../src/hooks/library/useLibraryResetAction.js";

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

test("encode le filtre de statut de validation dans la liste des jeux", async () => {
  let receivedUrl = "";
  window.fetch = async (url) => {
    receivedUrl = url;
    return new Response(JSON.stringify({ page: {}, games: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  AuthApi.storeAccessToken(createToken({ profile: "ADMIN" }), 3600);

  await LibraryApi.fetchGames({ status: "WAITING_VALIDATION", duplicate_flag: "true" });

  assert.equal(receivedUrl.includes("status=WAITING_VALIDATION"), true);
  assert.equal(receivedUrl.includes("duplicate_flag=true"), true);
});

test("appelle les endpoints admin de validation et refus avec les identifiants selectionnes", async () => {
  const calls = [];
  window.fetch = async (url, options) => {
    calls.push({ url, options });
    return new Response(JSON.stringify({ result: { validated_count: 2, refused_count: 2 } }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  AuthApi.storeAccessToken(createToken({ profile: "ADMIN" }), 3600);

  await LibraryAdminApi.validateGames([3, 7]);
  await LibraryAdminApi.refuseGames([11]);
  await LibraryAdminApi.fetchGameValidationSummary();

  assert.equal(calls[0].url, "/api/library/games/validation");
  assert.deepEqual(JSON.parse(calls[0].options.body), { game_ids: [3, 7] });
  assert.equal(calls[1].url, "/api/library/games/refusal");
  assert.deepEqual(JSON.parse(calls[1].options.body), { game_ids: [11] });
  assert.equal(calls[2].url, "/api/library/games/validation/summary");
});

test("derive la permission de gestion validation jeux depuis les routes admin", () => {
  const routes = [
    { path: "/api/library/games/validation/summary", methods: ["GET"], requires_auth: true, required_profiles: ["ADMIN"] },
    { path: "/api/library/games/validation", methods: ["POST"], requires_auth: true, required_profiles: ["ADMIN"] },
    { path: "/api/library/games/refusal", methods: ["POST"], requires_auth: true, required_profiles: ["ADMIN"] },
  ];

  const adminPermissions = new BackendRouteAccessService(routes, "token", "ADMIN").getActionPermissions();
  const userPermissions = new BackendRouteAccessService(routes, "token", "USER").getActionPermissions();

  assert.equal(adminPermissions.canManageGameValidation, true);
  assert.equal(userPermissions.canManageGameValidation, false);
});

test("ajoute l'avertissement de validation automatique dans la confirmation reset", () => {
  const message = buildLibraryResetConfirmationMessage(4);

  assert.equal(message.includes("4 jeu(x) en attente"), true);
  assert.equal(message.includes("valides automatiquement"), true);
});

test("declare les controles admin de filtre, selection et badge Bibliotheque", () => {
  const hookSource = readFileSync(
    new URL("../src/hooks/library/useLibraryGames.js", import.meta.url),
    "utf8"
  );
  const summaryHookSource = readFileSync(
    new URL("../src/hooks/library/useGameValidationSummary.js", import.meta.url),
    "utf8"
  );
  const viewModelSource = readFileSync(
    new URL("../src/hooks/app/useCloudCollectionViewModel.js", import.meta.url),
    "utf8"
  );
  const appSource = readFileSync(
    new URL("../src/App.jsx", import.meta.url),
    "utf8"
  );
  const pageLayoutSource = readFileSync(
    new URL("../src/components/PageLayout.jsx", import.meta.url),
    "utf8"
  );
  const listSource = readFileSync(
    new URL("../src/components/LibraryEntityListView.jsx", import.meta.url),
    "utf8"
  );
  const menuSource = readFileSync(
    new URL("../src/components/MainMenu.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(hookSource.includes("validationStatusFilter"), true);
  assert.equal(hookSource.includes("canManageGameValidation"), true);
  assert.equal(summaryHookSource.includes("loadGameValidationSummaryFromGameList"), true);
  assert.equal(summaryHookSource.includes('status: "WAITING_VALIDATION"'), true);
  assert.equal(listSource.includes("library-validation-status-filter"), true);
  assert.equal(listSource.includes("Tout selectionner"), true);
  assert.equal(listSource.includes("<span>Selectionner</span>"), false);
  assert.equal(listSource.includes("actionColumnLabel"), true);
  assert.equal(listSource.includes('actionColumnPosition={listState.validationWorkflow ? "left" : "right"}'), true);
  assert.equal(viewModelSource.includes('session.authenticatedProfile === "ADMIN"'), true);
  assert.equal(viewModelSource.includes("libraryValidationBadgeCount"), true);
  assert.equal(appSource.includes("LibraryValidationBadgeContext.Provider"), true);
  assert.equal(pageLayoutSource.includes("contextLibraryValidationBadgeCount"), true);
  assert.equal(menuSource.includes("mainNavigationBadge"), true);
  assert.equal(menuSource.includes("data-badge-count"), true);
});

test("affiche la colonne statut Bibliotheque uniquement pour ADMIN", () => {
  assert.equal(getLibraryGameColumns("ADMIN").includes("status"), true);
  assert.equal(getLibraryGameColumns("USER").includes("status"), false);
  assert.equal(getLibraryGameColumns("GUEST").includes("status"), false);
  assert.equal(getLibraryGameColumns("").includes("status"), false);
});
