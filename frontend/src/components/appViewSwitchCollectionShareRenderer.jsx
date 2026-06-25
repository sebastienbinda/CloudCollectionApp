/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : rendu de la page proprietaire des partages depuis AppViewSwitch.
 */
import CollectionShareManagementView from "./CollectionShareManagementView";

/**
 * Rend la page de gestion des partages de collection.
 *
 * @param {Object} props - Etat applicatif et hook de gestion des partages.
 * @param {Object} pageLayoutProps - Proprietes communes du layout applicatif.
 * @returns {import("react").JSX.Element} Vue de gestion des partages.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function renderCollectionShareManagementView(props, pageLayoutProps) {
  return (
    <CollectionShareManagementView
      {...pageLayoutProps}
      isManagementAllowed={props.canManageCollectionShares}
      collectionShareManagement={props.collectionShareManagement}
    />
  );
}

export default renderCollectionShareManagementView;
