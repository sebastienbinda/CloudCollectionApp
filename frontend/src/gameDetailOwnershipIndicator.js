/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : presentation de l'indicateur d'association utilisateur d'un jeu.
 */

/**
 * Construit le modele d'affichage de l'indicateur collection ou wishlist.
 *
 * @param {boolean} isInCurrentUserCollection - Indique si le jeu est associe a l'utilisateur.
 * @param {boolean} isInCurrentUserWishlist - Indique si l'association est une wishlist.
 * @returns {Object|null} Modele d'indicateur ou `null` si rien ne doit etre affiche.
 * @throws {Error} Aucune exception n'est levee.
 */
export function buildGameDetailOwnershipIndicator(
  isInCurrentUserCollection,
  isInCurrentUserWishlist
) {
  if (!isInCurrentUserCollection) {
    return null;
  }
  if (isInCurrentUserWishlist) {
    return {
      ariaLabel: "Jeu dans votre liste de souhaits",
      className: "gameCollectionOwnershipIndicator gameCollectionOwnershipIndicatorWishlist",
      icon: "heart",
      label: "Dans votre liste de souhaits",
    };
  }
  return {
    ariaLabel: "Jeu possede",
    className: "gameCollectionOwnershipIndicator",
    icon: "star",
    label: "Vous possedez ce jeu",
  };
}
