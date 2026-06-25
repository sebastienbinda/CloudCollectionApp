/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : hook metier de gestion proprietaire des partages de collection.
 */
import { useEffect, useState } from "react";
import CollectionSharesApi from "../../services/CollectionSharesApi.js";
import { validateCollectionShareForm } from "./collectionShareForm.js";

const INITIAL_SHARE_FORM = Object.freeze({
  durationHours: 24,
  allowCollection: true,
  allowWishlist: false,
  allowPrices: false,
});

/**
 * Copie un lien de partage avec le presse-papiers fourni.
 *
 * @param {Object} share - Partage contenant le lien absolu.
 * @param {Clipboard|null} clipboard - API presse-papiers injectable.
 * @returns {Promise<void>} Promesse resolue apres copie.
 * @throws {Error} Si le presse-papiers est indisponible.
 */
async function copyCollectionShareLink(share, clipboard = navigator.clipboard) {
  if (!clipboard?.writeText) {
    throw new Error("Presse-papiers indisponible dans ce navigateur.");
  }
  await clipboard.writeText(share.link);
}

/**
 * Demande la confirmation de revocation d'un partage.
 *
 * @param {Function} confirmAction - Fonction de confirmation injectable.
 * @returns {boolean} `true` lorsque le proprietaire confirme.
 * @throws {void} Ne leve pas d'exception.
 */
function confirmCollectionShareRevocation(confirmAction = window.confirm) {
  return confirmAction("Confirmer la revocation de ce partage ?");
}

/**
 * Orchestre la creation, la liste, la copie et la revocation des partages.
 *
 * @param {Object} options - Etat d'activation de la page proprietaire.
 * @returns {Object} Etat et actions directement consommables par la vue.
 * @throws {void} Les erreurs asynchrones sont converties en messages.
 */
function useCollectionShareManagement(options) {
  const [shares, setShares] = useState([]);
  const [form, setForm] = useState(INITIAL_SHARE_FORM);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [revokingShareId, setRevokingShareId] = useState(null);

  useEffect(() => {
    if (!options.enabled) {
      return;
    }
    const loadShares = async () => {
      setIsLoading(true);
      setError("");
      try {
        setShares(await CollectionSharesApi.listShares());
      } catch (loadError) {
        setError(loadError.message || "Impossible de charger les partages.");
      } finally {
        setIsLoading(false);
      }
    };
    loadShares();
  }, [options.enabled]);

  const updateForm = (fieldName, value) => {
    setForm((currentForm) => ({ ...currentForm, [fieldName]: value }));
    setError("");
    setMessage("");
  };

  const createShare = async (event) => {
    event.preventDefault();
    const validation = validateCollectionShareForm(form);
    if (validation.error) {
      setError(validation.error);
      return;
    }
    setIsCreating(true);
    setError("");
    setMessage("");
    try {
      const createdShare = await CollectionSharesApi.createShare(validation.payload);
      setShares((currentShares) => [createdShare, ...currentShares]);
      setMessage("Le lien de partage a ete cree.");
    } catch (creationError) {
      setError(creationError.message || "Impossible de creer le partage.");
    } finally {
      setIsCreating(false);
    }
  };

  const copyShareLink = async (share) => {
    setError("");
    setMessage("");
    try {
      await copyCollectionShareLink(share);
      setMessage("Le lien de partage a ete copie.");
    } catch (copyError) {
      setError(copyError.message || "Impossible de copier le lien.");
    }
  };

  const revokeShare = async (share) => {
    if (!confirmCollectionShareRevocation()) {
      return;
    }
    setRevokingShareId(share.id);
    setError("");
    setMessage("");
    try {
      const revokedShare = await CollectionSharesApi.revokeShare(share.id);
      setShares((currentShares) => currentShares.map(
        (currentShare) => currentShare.id === revokedShare.id ? revokedShare : currentShare
      ));
      setMessage("Le partage a ete revoque.");
    } catch (revocationError) {
      setError(revocationError.message || "Impossible de revoquer le partage.");
    } finally {
      setRevokingShareId(null);
    }
  };

  return {
    shares,
    form,
    error,
    message,
    isLoading,
    isCreating,
    revokingShareId,
    updateForm,
    createShare,
    copyShareLink,
    revokeShare,
  };
}

export {
  INITIAL_SHARE_FORM,
  confirmCollectionShareRevocation,
  copyCollectionShareLink,
};
export default useCollectionShareManagement;
