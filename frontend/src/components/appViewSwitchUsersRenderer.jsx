/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-07-05
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : rendu de la vue utilisateurs pour AppViewSwitch.
 */
import UsersView from "./UsersView";

/**
 * Rend la page de gestion des utilisateurs.
 *
 * @param {Object} props - Etat et callbacks d'administration utilisateur.
 * @param {Object} layoutProps - Proprietes communes du layout.
 * @returns {import("react").JSX.Element} Vue utilisateurs.
 */
function renderUsersView(props, layoutProps) {
  return (
    <UsersView
      {...layoutProps}
      canSearchUsers={props.actionPermissions.canSearchUsers}
      canDeleteUser={props.actionPermissions.canDeleteUser}
      canLockUser={props.actionPermissions.canLockUser}
      canUnlockUser={props.actionPermissions.canUnlockUser}
      canValidateUser={props.actionPermissions.canValidateUser}
    />
  );
}

export default renderUsersView;
