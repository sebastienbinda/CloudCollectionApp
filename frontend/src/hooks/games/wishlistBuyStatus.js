/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-11-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : detection du statut d'achat affiche dans la liste de souhaits.
 */

/**
 * Indique si un jeu de la liste de souhaits contient une information d'achat.
 *
 * @param {Object|null|undefined} game - Jeu normalise retourne par le backend.
 * @returns {boolean} `true` lorsque le jeu est en cours d'achat.
 * @throws {Error} Aucune exception n'est levee.
 */
function isWishlistPurchaseInProgress(game) {
  if (!game) {
    return false;
  }

  return [game["Date d'achat"], game["Lieu d'achat"], game["Prix d'achat"]]
    .some((value) => value !== null && value !== undefined && String(value).trim() !== "");
}

export default isWishlistPurchaseInProgress;
