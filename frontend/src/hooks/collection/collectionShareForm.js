/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : validation pure du formulaire de partage de collection.
 */

const MINIMUM_DURATION_HOURS = 1;
const MAXIMUM_DURATION_HOURS = 240;

/**
 * Valide et transforme le formulaire frontend en payload backend.
 *
 * @param {Object} form - Valeurs de duree et permissions saisies.
 * @returns {{payload: Object|null, error: string}} Resultat de validation.
 * @throws {void} Ne leve pas d'exception.
 */
function validateCollectionShareForm(form) {
  const durationHours = Number(form.durationHours);
  if (
    !Number.isInteger(durationHours) ||
    durationHours < MINIMUM_DURATION_HOURS ||
    durationHours > MAXIMUM_DURATION_HOURS
  ) {
    return {
      payload: null,
      error: "La duree doit etre un nombre entier compris entre 1 et 240 heures.",
    };
  }
  if (!form.allowCollection && !form.allowWishlist) {
    return {
      payload: null,
      error: "Autorisez au moins la collection ou la liste de souhaits.",
    };
  }
  return {
    error: "",
    payload: {
      duration_hours: durationHours,
      allow_collection: form.allowCollection === true,
      allow_wishlist: form.allowWishlist === true,
      allow_prices: form.allowPrices === true,
    },
  };
}

export {
  MAXIMUM_DURATION_HOURS,
  MINIMUM_DURATION_HOURS,
  validateCollectionShareForm,
};
