/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : presentation pure des statuts de partage de collection.
 */

/**
 * Normalise le statut backend d'un partage pour la vue.
 *
 * @param {string} status - Statut brut retourne par le backend.
 * @returns {{key: string, label: string}} Cle CSS et libelle francais.
 * @throws {void} Ne leve pas d'exception.
 */
function getCollectionShareStatusPresentation(status) {
  const normalizedStatus = String(status || "ACTIVE").trim().toUpperCase();
  if (normalizedStatus === "EXPIRED") {
    return { key: "EXPIRED", label: "Expire" };
  }
  if (normalizedStatus === "REVOKED") {
    return { key: "REVOKED", label: "Revoque" };
  }
  return { key: "ACTIVE", label: "Actif" };
}

export default getCollectionShareStatusPresentation;
