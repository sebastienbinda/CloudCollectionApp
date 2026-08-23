/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de la page dediee aux retours utilisateur.
 */
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

test("la page A propos pointe vers la page dediee de retour utilisateur", () => {
  const aboutSource = readFileSync(
    new URL("../src/components/AboutView.jsx", import.meta.url),
    "utf8",
  );
  const feedbackViewSource = readFileSync(
    new URL("../src/components/FeedbackView.jsx", import.meta.url),
    "utf8",
  );
  const feedbackApiSource = readFileSync(
    new URL("../src/services/FeedbackApi.js", import.meta.url),
    "utf8",
  );

  assert.equal(aboutSource.includes("Envoyer une remarque"), true);
  assert.equal(aboutSource.includes("onOpenFeedback"), true);
  assert.equal(aboutSource.includes("FeedbackApi.submitFeedback"), false);
  assert.equal(feedbackViewSource.includes("FeedbackApi.submitFeedback"), true);
  assert.equal(feedbackViewSource.includes("sans creer de compte GitHub"), true);
  assert.equal(feedbackViewSource.includes("Suivre ma demande sur GitHub"), true);
  assert.equal(feedbackViewSource.includes("Le message creera une issue GitHub"), false);
  assert.equal(feedbackApiSource.includes("/api/feedback"), true);
  assert.equal(feedbackApiSource.includes("AuthApi.getAuthorizationHeaders()"), true);
});

test("la page de retour utilisateur est routee et accessible depuis le menu", () => {
  const routingSource = readFileSync(
    new URL("../src/appRouting.js", import.meta.url),
    "utf8",
  );
  const navigationSource = readFileSync(
    new URL("../src/hooks/navigation/useAppNavigation.js", import.meta.url),
    "utf8",
  );
  const viewSwitchSource = readFileSync(
    new URL("../src/components/AppViewSwitch.jsx", import.meta.url),
    "utf8",
  );
  const menuSource = readFileSync(
    new URL("../src/components/MainMenu.jsx", import.meta.url),
    "utf8",
  );

  assert.equal(routingSource.includes('"/feedback"'), true);
  assert.equal(navigationSource.includes('openFeedback: () => openView("feedback", "/feedback")'), true);
  assert.equal(viewSwitchSource.includes('props.currentView === "feedback"'), true);
  assert.equal(menuSource.includes('key: "feedback"'), true);
  assert.equal(menuSource.includes("Faire un retour"), true);
  assert.equal(menuSource.includes("mobileAuthenticatedSecondaryItems"), true);
});

test("les pages routees propagent l'entree de retour utilisateur au layout", () => {
  const componentsDirectory = new URL("../src/components/", import.meta.url);
  const files = readdirSync(componentsDirectory)
    .filter((file) => file.endsWith(".jsx") && file !== "PageLayout.jsx");

  files.forEach((file) => {
    const source = readFileSync(join(componentsDirectory.pathname, file), "utf8");
    if (!source.includes("<PageLayout") || !source.includes("onOpenLibrary")) {
      return;
    }

    assert.equal(
      source.includes("onOpenFeedback"),
      true,
      `${file} doit propager onOpenFeedback au PageLayout.`
    );
  });
});
