/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : regles frontend de session pour les vues collection.
 */

import AuthApi from "../../services/AuthApi";

/**
 * Indique si le token courant peut ouvrir les vues de collection.
 *
 * @returns {boolean} `true` pour les profils collection utilisateur.
 * @throws {void} Ne leve pas d'exception.
 */
function canCurrentTokenUseCollectionViews() {
  const profile = String(AuthApi.getAccessTokenPayload().profile || "USER").trim().toUpperCase();
  return profile !== "ADMIN";
}

export default canCurrentTokenUseCollectionViews;
