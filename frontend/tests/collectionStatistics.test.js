/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend des statistiques de collection.
 */
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";
import BackendRouteAccessService from "../src/services/BackendRouteAccessService.js";
import CollectionStatisticsApi from "../src/services/CollectionStatisticsApi.js";
import GuestNavigationPolicy from "../src/services/GuestNavigationPolicy.js";
import resolveMainMenuAccess from "../src/services/MainMenuAccessPolicy.js";
import VideoGamesApi from "../src/services/VideoGamesApi.js";

test("normalise le contrat backend des statistiques detaillees", () => {
  const statistics = CollectionStatisticsApi.normalizeStatistics({
    total_games: 4,
    platform_distribution: [
      { platform_id: 1, platform_name: "Switch", games_count: 3, ratio: 75 },
    ],
    release_year_distribution: [{ year: 1992, games_count: 1 }],
    purchase_year_distribution: [{ year: 2024, games_count: 2 }],
    top_rated_games: [
      {
        id: 3,
        name: "Mario Kart",
        platform_name: "Switch",
        release_date: "1992-08-27",
        buy_date: "2024-03-10",
        grade: "9.5",
        grade_normalized: 95,
      },
    ],
  });

  assert.equal(statistics.totalGames, 4);
  assert.equal(statistics.platformDistribution[0].label, "Switch");
  assert.equal(statistics.platformDistribution[0].ratio, 75);
  assert.equal(statistics.releaseYearDistribution[0].label, "1992");
  assert.equal(statistics.purchaseYearDistribution[0].gamesCount, 2);
  assert.equal(statistics.topRatedGames[0].platformName, "Switch");
  assert.equal(statistics.topRatedGames[0].gradeNormalized, 95);
});

test("envoie le filtre plateforme au endpoint des statistiques detaillees", async () => {
  const originalFetchJson = VideoGamesApi.fetchJson;
  let requestedUrl = "";
  VideoGamesApi.fetchJson = async (url) => {
    requestedUrl = url;
    return {};
  };

  try {
    await CollectionStatisticsApi.fetchStatistics({ platformId: 3 });
  } finally {
    VideoGamesApi.fetchJson = originalFetchJson;
  }

  assert.equal(requestedUrl, "/collections/statistics?platform_id=3");
});

test("expose l'entree statistiques seulement avec route et collection autorisees", () => {
  const service = new BackendRouteAccessService(
    [
      {
        path: "/collections/statistics",
        methods: ["GET"],
        requires_auth: true,
        required_profiles: ["GUEST", "USER"],
      },
    ],
    "token",
    "USER"
  );
  const menuAccess = resolveMainMenuAccess({
    isAuthenticated: true,
    canViewCollection: true,
    canViewStatistics: service.getActionPermissions().canViewCollectionStatistics,
    onOpenHome: () => {},
    onOpenStatistics: () => {},
  });

  assert.equal(menuAccess.canOpenStatistics, true);
  assert.equal(
    resolveMainMenuAccess({
      isAuthenticated: true,
      canViewCollection: true,
      canViewStatistics: true,
      onOpenStatistics: () => {},
    }).canOpenStatistics,
    true
  );
  assert.equal(
    resolveMainMenuAccess({
      isAuthenticated: true,
      canViewCollection: false,
      canViewStatistics: false,
      onOpenStatistics: () => {},
    }).canOpenStatistics,
    false
  );
});

test("autorise les statistiques GUEST uniquement avec la permission collection", () => {
  const collectionPolicy = new GuestNavigationPolicy({ canViewCollection: true });
  const wishlistPolicy = new GuestNavigationPolicy({ canViewWishlist: true });

  assert.equal(collectionPolicy.isViewBlocked("statistics"), false);
  assert.equal(wishlistPolicy.isViewBlocked("statistics"), true);
});

test("positionne statistiques apres la liste de souhaits dans le menu", () => {
  const source = readFileSync(
    new URL("../src/components/MainMenu.jsx", import.meta.url),
    "utf8"
  );
  const desktopMenu = source.slice(
    source.indexOf("const authenticatedNavigationItems"),
    source.indexOf("const navigationItems")
  );
  const mobileMenu = source.slice(
    source.indexOf("const mobileAuthenticatedPrimaryItems"),
    source.indexOf("const mobileAnonymousPrimaryItems")
  );

  assert.ok(desktopMenu.indexOf("wishlistItem") < desktopMenu.indexOf("statisticsItem"));
  assert.ok(mobileMenu.indexOf("wishlistItem") < mobileMenu.indexOf("statisticsItem"));
});

test("affiche les repartitions par dates dans un graphique Chart.js commun", () => {
  const source = readFileSync(
    new URL("../src/components/CollectionStatisticsView.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(source.includes("<DateDistributionBarChart"), true);
  assert.equal(source.includes('type: "bar"'), true);
  assert.equal(source.includes("releaseYearDistribution"), true);
  assert.equal(source.includes("purchaseYearDistribution"), true);
});

test("la legende du camembert pilote le filtre plateforme des dates", () => {
  const source = readFileSync(
    new URL("../src/components/CollectionStatisticsView.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(source.includes("onTogglePlatform"), true);
  assert.equal(source.includes("aria-pressed"), true);
  assert.equal(source.includes("selectedPlatformId"), true);
});

test("adapte le camembert aux ecrans mobiles avec legende compacte", () => {
  const componentSource = readFileSync(
    new URL("../src/components/CollectionStatisticsView.jsx", import.meta.url),
    "utf8"
  );
  const stylesSource = readFileSync(
    new URL("../src/styles/collection-statistics.css", import.meta.url),
    "utf8"
  );

  assert.equal(componentSource.includes("createMobilePieLabelPlugin"), false);
  assert.equal(componentSource.includes("mobilePlatformPieLabels"), false);
  assert.equal(stylesSource.includes("grid-template-columns: repeat(2, minmax(0, 1fr));"), true);
  assert.equal(stylesSource.includes("font-size: 0.76rem;"), true);
  assert.equal(stylesSource.includes("padding: 0.28rem 0.34rem;"), true);
  assert.equal(stylesSource.includes("width: min(68vw, 13.5rem);"), true);
});

test("conserve le contenu statistiques pendant le rechargement du filtre plateforme", () => {
  const source = readFileSync(
    new URL("../src/components/CollectionStatisticsView.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(source.includes("!statisticsPage?.isLoadingStatistics && statistics && !hasNoData"), false);
  assert.equal(source.includes("statistics && !hasNoData"), true);
});

test("masque le message vide des jeux les mieux notes", () => {
  const source = readFileSync(
    new URL("../src/components/CollectionStatisticsView.jsx", import.meta.url),
    "utf8"
  );

  assert.equal(source.includes("Aucun jeu avec une note superieure a 9"), false);
  assert.equal(source.includes("{formatNumber(statistics.topRatedGames.length)} jeux"), true);
});

test("les pages applicatives propagent l'entree statistiques au layout", () => {
  const componentsDirectory = new URL("../src/components/", import.meta.url);
  const ignoredFiles = new Set(["AuthView.jsx", "EmailVerificationResultView.jsx"]);
  const files = readdirSync(componentsDirectory)
    .filter((file) => file.endsWith(".jsx") && !ignoredFiles.has(file));

  files.forEach((file) => {
    const source = readFileSync(join(componentsDirectory.pathname, file), "utf8");
    if (!source.includes("<PageLayout") || !source.includes("canViewCollection")) {
      return;
    }

    assert.equal(
      source.includes("canViewStatistics"),
      true,
      `${file} doit propager canViewStatistics au PageLayout.`
    );
    assert.equal(
      source.includes("onOpenStatistics"),
      true,
      `${file} doit propager onOpenStatistics au PageLayout.`
    );
  });
});
