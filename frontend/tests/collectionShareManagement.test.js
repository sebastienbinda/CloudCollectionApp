/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de gestion proprietaire des partages.
 */
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import getCollectionShareStatusPresentation from "../src/collectionSharePresentation.js";
import {
  validateCollectionShareForm,
} from "../src/hooks/collection/collectionShareForm.js";
import {
  confirmCollectionShareRevocation,
  copyCollectionShareLink,
} from "../src/hooks/collection/useCollectionShareManagement.js";
import AuthApi from "../src/services/AuthApi.js";
import BackendAvailabilityGuard from "../src/services/BackendAvailabilityGuard.js";
import CollectionSharesApi from "../src/services/CollectionSharesApi.js";

class MemoryStorage {
  constructor() {
    this.values = new Map();
  }

  getItem(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  }

  setItem(key, value) {
    this.values.set(key, String(value));
  }

  removeItem(key) {
    this.values.delete(key);
  }
}

beforeEach(() => {
  global.window = {
    atob: (value) => Buffer.from(value, "base64").toString("binary"),
    dispatchEvent: () => {},
    localStorage: new MemoryStorage(),
    fetch: async () => new Response("{}", { status: 500 }),
  };
  AuthApi.storeAccessToken("user-token", 3600);
  BackendAvailabilityGuard.consecutiveFailures = 0;
  BackendAvailabilityGuard.blockedUntil = 0;
});

test("valide les bornes de duree et les permissions obligatoires", () => {
  const baseForm = {
    recipient: " Alice ",
    durationHours: 24,
    allowCollection: true,
    allowWishlist: false,
    allowPrices: true,
  };
  assert.ok(validateCollectionShareForm({ ...baseForm, durationHours: 0 }).error);
  assert.ok(validateCollectionShareForm({ ...baseForm, durationHours: 241 }).error);
  assert.ok(validateCollectionShareForm({ ...baseForm, durationHours: 1.5 }).error);
  assert.ok(validateCollectionShareForm({
    ...baseForm,
    allowCollection: false,
    allowWishlist: false,
  }).error);
  assert.deepEqual(validateCollectionShareForm(baseForm).payload, {
    recipient: "Alice",
    duration_hours: 24,
    allow_collection: true,
    allow_wishlist: false,
    allow_prices: true,
  });
  assert.equal(validateCollectionShareForm({ ...baseForm, recipient: "x".repeat(257) }).error,
    "Le destinataire doit contenir 256 caracteres maximum.");
  assert.equal(validateCollectionShareForm({ ...baseForm, recipient: "   " }).payload.recipient, null);
});

test("liste cree et revoque avec les contrats HTTP proprietaire", async () => {
  const requests = [];
  window.fetch = async (url, options) => {
    requests.push({ url, options });
    if (options.method === "POST") {
      return Response.json({ share: { id: 9, status: "ACTIVE" } }, { status: 201 });
    }
    if (options.method === "DELETE") {
      return Response.json({ share: { id: 9, status: "REVOKED" } });
    }
    return Response.json({ shares: [{ id: 8, status: "EXPIRED" }] });
  };

  const shares = await CollectionSharesApi.listShares();
  const created = await CollectionSharesApi.createShare({ duration_hours: 24, recipient: "Alice" });
  const revoked = await CollectionSharesApi.revokeShare(9);

  assert.equal(shares[0].status, "EXPIRED");
  assert.equal(created.status, "ACTIVE");
  assert.equal(revoked.status, "REVOKED");
  assert.equal(requests[0].options.headers.Authorization, "Bearer user-token");
  assert.deepEqual(requests.map((request) => request.options.method || "GET"), [
    "GET", "POST", "DELETE",
  ]);
  assert.deepEqual(JSON.parse(requests[1].options.body), {
    duration_hours: 24,
    recipient: "Alice",
  });
});

test("presente distinctement les partages actifs expires et revoques", () => {
  assert.deepEqual(getCollectionShareStatusPresentation("ACTIVE"), {
    key: "ACTIVE", label: "Actif",
  });
  assert.deepEqual(getCollectionShareStatusPresentation("EXPIRED"), {
    key: "EXPIRED", label: "Expire",
  });
  assert.deepEqual(getCollectionShareStatusPresentation("REVOKED"), {
    key: "REVOKED", label: "Revoque",
  });
});

test("copie le lien avec le presse-papiers injecte", async () => {
  let copiedValue = "";
  await copyCollectionShareLink(
    { link: "https://example.test/collection/share/token" },
    { writeText: async (value) => { copiedValue = value; } }
  );
  assert.equal(copiedValue, "https://example.test/collection/share/token");
  await assert.rejects(() => copyCollectionShareLink({ link: "x" }, null));
});

test("demande confirmation avant la revocation", () => {
  let confirmationMessage = "";
  const confirmed = confirmCollectionShareRevocation((message) => {
    confirmationMessage = message;
    return true;
  });
  assert.equal(confirmed, true);
  assert.match(confirmationMessage, /revocation/i);
});
