/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-09
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests des liens de recherche marchande depuis le detail d'un jeu.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildGameMarketplaceSearchLinks,
  buildMarketplaceSearchQuery,
  wasPlatformActiveTenYearsBefore,
} from "../src/gameMarketplaceSearchLinks.js";

const REFERENCE_DATE = new Date("2026-07-09T12:00:00Z");

test("construit une requete de recherche avec le nom du jeu et la plateforme", () => {
  assert.equal(
    buildMarketplaceSearchQuery("The Legend of Zelda", "Nintendo Switch"),
    "The Legend of Zelda Nintendo Switch"
  );
});

test("ignore les valeurs vides dans la requete de recherche", () => {
  assert.equal(buildMarketplaceSearchQuery("  Chrono Trigger  ", " "), "Chrono Trigger");
});

test("utilise l'alias courant de plateforme fourni pour la recherche", () => {
  const links = buildGameMarketplaceSearchLinks("Zelda", "NES", "1995-08-14", REFERENCE_DATE);

  assert.equal(links[0].url, "https://www.leboncoin.fr/recherche?text=Zelda+NES");
  assert.equal(links[1].url, "https://www.ebay.fr/sch/i.html?_nkw=Zelda+NES");
});

test("ajoute la region non francaise a la requete de recherche", () => {
  const links = buildGameMarketplaceSearchLinks("Chrono Trigger", "SNES", "1999-09-30", REFERENCE_DATE, "US");

  assert.equal(links[0].url, "https://www.leboncoin.fr/recherche?text=Chrono+Trigger+SNES+US");
  assert.equal(links[1].url, "https://www.ebay.fr/sch/i.html?_nkw=Chrono+Trigger+SNES+US");
});

test("ignore les regions francaises dans la requete de recherche", () => {
  assert.equal(buildMarketplaceSearchQuery("Zelda", "NES", "EU-FR"), "Zelda NES");
  assert.equal(buildMarketplaceSearchQuery("Zelda", "NES", "EUR-FR"), "Zelda NES");
  assert.equal(buildMarketplaceSearchQuery("Zelda", "NES", "FR"), "Zelda NES");
});

test("construit les quatre liens d'achat pour une plateforme active dix ans avant", () => {
  const links = buildGameMarketplaceSearchLinks(
    "Mario & Luigi",
    "3DS",
    "2017-01-01",
    REFERENCE_DATE
  );

  assert.deepEqual(
    links.map((link) => link.label),
    [
      "leboncoin",
      "eBay",
      "Amazon",
      "fnac.com",
    ]
  );
  assert.equal(links[0].url, "https://www.leboncoin.fr/recherche?text=Mario+%26+Luigi+3DS");
  assert.equal(links[1].url, "https://www.ebay.fr/sch/i.html?_nkw=Mario+%26+Luigi+3DS");
  assert.equal(links[2].url, "https://www.amazon.fr/s?k=Mario+%26+Luigi+3DS");
  assert.equal(links[3].url, "https://www.fnac.com/SearchResult/ResultList.aspx?Search=Mario+%26+Luigi+3DS");
  assert.equal(links.every((link) => link.iconUrl.endsWith("/favicon.ico")), true);
});

test("limite les liens a l'occasion pour une plateforme arretee depuis plus de dix ans", () => {
  const links = buildGameMarketplaceSearchLinks("Final Fantasy", "NES", "1995-08-14", REFERENCE_DATE);

  assert.deepEqual(
    links.map((link) => link.label),
    ["leboncoin", "eBay"]
  );
});

test("n'affiche pas Amazon et Fnac pour une PlayStation arretee depuis plus de dix ans", () => {
  const links = buildGameMarketplaceSearchLinks("Ridge Racer", "PS1", "2006-03-23", REFERENCE_DATE);

  assert.deepEqual(
    links.map((link) => link.key),
    ["leboncoin", "ebay"]
  );
});

test("affiche les quatre liens d'achat quand la plateforme n'a pas de date de fin", () => {
  const links = buildGameMarketplaceSearchLinks("Zelda", "Switch", "", REFERENCE_DATE);

  assert.deepEqual(
    links.map((link) => link.key),
    ["leboncoin", "ebay", "amazon", "fnac"]
  );
});

test("considere une plateforme sans date de fin comme active dix ans avant", () => {
  assert.equal(wasPlatformActiveTenYearsBefore("", REFERENCE_DATE), true);
});

test("accepte une date de fin egale au seuil des dix ans", () => {
  assert.equal(wasPlatformActiveTenYearsBefore("2016-07-09", REFERENCE_DATE), true);
});

test("refuse une date de fin anterieure au seuil des dix ans", () => {
  assert.equal(wasPlatformActiveTenYearsBefore("2016-07-08", REFERENCE_DATE), false);
});

test("ne construit pas de lien sans nom ni plateforme", () => {
  assert.deepEqual(buildGameMarketplaceSearchLinks("", ""), []);
});
