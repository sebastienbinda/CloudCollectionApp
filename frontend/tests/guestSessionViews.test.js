/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests des vues, libelles et redirections des sessions GUEST.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import GuestNavigationPolicy from "../src/services/GuestNavigationPolicy.js";
import GuestSessionViewPolicy from "../src/services/GuestSessionViewPolicy.js";
import resolveMainMenuAccess from "../src/services/MainMenuAccessPolicy.js";
import VideoGamesApi from "../src/services/VideoGamesApi.js";

test("derive l'identite et les sous-titres GUEST avec le pseudonyme proprietaire", () => {
  const policy = new GuestSessionViewPolicy({
    profile: "GUEST",
    owner_pseudonym: "Sébastien",
    permissions: { collection: true, wishlist: true, prices: false },
    wishlist_buy_status_default_filter: "yes",
  }).toViewModel("ignored");

  assert.equal(policy.identityLabel, "Invité de Sébastien");
  assert.equal(policy.collectionLabel, "Collection de Sébastien");
  assert.equal(policy.wishlistLabel, "Liste de souhaits de Sébastien");
  assert.equal(policy.canViewPrices, false);
  assert.equal(policy.canAccessConfiguration, false);
  assert.equal(policy.canMutate, false);
  assert.equal(policy.wishlistBuyStatusDefaultFilter, "yes");
});

test("reproduit exactement les combinaisons de menus collection et wishlist", () => {
  const combinations = [
    [{ collection: true, wishlist: true }, [true, true]],
    [{ collection: true, wishlist: false }, [true, false]],
    [{ collection: false, wishlist: true }, [false, true]],
    [{ collection: false, wishlist: false }, [false, false]],
  ];

  combinations.forEach(([permissions, expected]) => {
    const policy = new GuestSessionViewPolicy({ profile: "GUEST", permissions }).toViewModel();
    assert.deepEqual([policy.canViewCollection, policy.canViewWishlist], expected);
  });
});

test("masque l'entree wishlist du menu quand le partage GUEST ne l'autorise pas", () => {
  const menuAccess = resolveMainMenuAccess({
    isAuthenticated: true,
    canViewCollection: true,
    canViewWishlist: false,
    canAccessConfiguration: false,
    onOpenHome: () => {},
    onOpenWishlist: () => {},
    onOpenConfiguration: () => {},
  });

  assert.equal(menuAccess.canOpenHome, true);
  assert.equal(menuAccess.canOpenWishlist, false);
  assert.equal(menuAccess.canOpenConfiguration, false);
});

test("redirige les routes interdites vers la premiere categorie partagee", () => {
  const collectionPolicy = new GuestNavigationPolicy({ canViewCollection: true });
  const wishlistPolicy = new GuestNavigationPolicy({ canViewWishlist: true });

  ["configuration", "collectionShares", "platformImageModeration", "addGame", "collectionOnboarding"]
    .forEach((view) => assert.equal(collectionPolicy.isViewBlocked(view), true));
  assert.deepEqual(collectionPolicy.getFallbackDestination(), {
    view: "home",
    path: "/collection",
  });
  assert.equal(wishlistPolicy.isViewBlocked("home"), true);
  assert.equal(wishlistPolicy.isViewBlocked("wishlist"), false);
  assert.deepEqual(wishlistPolicy.getFallbackDestination(), {
    view: "wishlist",
    path: "/wishlist",
  });
});

test("conserve les acces visuels des profils USER et ADMIN", () => {
  ["USER", "ADMIN"].forEach((profile) => {
    const policy = new GuestSessionViewPolicy({ profile }).toViewModel(profile.toLowerCase());
    assert.equal(policy.identityLabel, profile.toLowerCase());
    assert.equal(policy.canViewCollection, true);
    assert.equal(policy.canViewWishlist, true);
    assert.equal(policy.canViewPrices, true);
    assert.equal(policy.canAccessConfiguration, true);
    assert.equal(policy.canMutate, true);
  });
});

test("ne recree pas les champs de prix absents du payload GUEST", () => {
  const [game] = VideoGamesApi.normalizeCollectionGames([{ id: 7, name: "Sans prix" }]);

  assert.equal(Object.hasOwn(game, "Prix d'achat"), false);
  assert.equal(Object.hasOwn(game, "priceUnit"), false);
});

test("normalise le filtre en cours d'achat de la wishlist", () => {
  assert.equal(
    new GuestSessionViewPolicy({
      profile: "GUEST",
      wishlist_buy_status_default_filter: "yes",
    }).wishlistBuyStatusDefaultFilter,
    "yes"
  );
  assert.equal(
    new GuestSessionViewPolicy({
      profile: "GUEST",
      wishlist_buy_status_default_filter: "no",
    }).wishlistBuyStatusDefaultFilter,
    "no"
  );
  assert.equal(
    new GuestSessionViewPolicy({
      profile: "GUEST",
      wishlist_buy_status_default_filter: "unexpected",
    }).wishlistBuyStatusDefaultFilter,
    "all"
  );
});
