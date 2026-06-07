/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | |__| (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-03
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : messages frontend du workflow d'import de collection.
 */

/**
 * Convertit une erreur d'import en message utilisateur comprehensible.
 *
 * @param {Error} error - Erreur retournee par le client API.
 * @returns {string} Message affichable par la vue d'onboarding.
 * @throws {void} Ne leve pas d'exception.
 */
function getUserCollectionErrorMessage(error) {
  const messagesByCode = {
    invalid_file: formatInvalidFileMessage(error),
    file_too_large: "Le fichier selectionne depasse la taille maximale autorisee.",
    invalid_configuration: formatInvalidConfigurationMessage(error),
    temporary_file_missing: "Envoyez votre fichier de collection avant de lancer l'import.",
    collection_already_imported: "Une collection est deja associee a ce compte.",
    collection_not_found: "Aucune collection n'est disponible pour votre compte.",
    unauthorized: "Votre session ne permet pas d'importer cette collection.",
    unexpected_error: "L'import de la collection a echoue.",
  };
  return messagesByCode[error?.code] || error?.message || messagesByCode.unexpected_error;
}

/**
 * Formate les erreurs 400 de fichier invalide retournees par le backend.
 *
 * @param {Error} error - Erreur API normalisee.
 * @returns {string} Message affichable dans l'onboarding.
 */
function formatInvalidFileMessage(error) {
  const details = Array.isArray(error?.details?.details) ? error.details.details : [];
  if (!details.length) {
    return "Le fichier selectionne doit etre un fichier de collection valide.";
  }
  return `Le fichier selectionne est invalide : ${details.join(" ")}`;
}

/**
 * Formate les erreurs 422 de configuration retournees par le backend.
 *
 * @param {Error} error - Erreur API normalisee.
 * @returns {string} Message affichable dans l'onboarding.
 */
function formatInvalidConfigurationMessage(error) {
  const details = Array.isArray(error?.details?.details) ? error.details.details : [];
  if (!details.length) {
    return "La configuration d'import est invalide.";
  }
  return `La configuration d'import est invalide : ${details.join(" ")}`;
}

export default getUserCollectionErrorMessage;
