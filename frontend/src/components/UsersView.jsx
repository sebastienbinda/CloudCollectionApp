/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-22
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React de consultation administrative des utilisateurs.
 */
import { useEffect, useState } from "react";
import TableColumnFormatService from "../services/TableColumnFormatService.jsx";
import UsersApi from "../services/UsersApi";
import ProgressBar from "./ProgressBar";
import ProjectIcon from "./ProjectIcon";

const userColumns = [
  { key: "email", label: "Email" },
  { key: "profile", label: "Profil" },
  { key: "status", label: "Statut" },
  { key: "is_email_verified", label: "Email verifie" },
  { key: "creation_date", label: "Creation" },
  { key: "last_connexion_date", label: "Derniere connexion" },
];

const initialUserFilters = {
  email: "",
  emailMode: "contains",
  creationPeriod: "",
  lastConnexionPeriod: "",
  status: "",
};

const statusFilterOptions = [
  { value: "WAITING_VALIDATION", label: "En attente de validation" },
  { value: "ACTIVE", label: "Actif" },
  { value: "LOCKED", label: "Bloque" },
];

/**
 * Affiche la liste des utilisateurs dans un tableau administrateur.
 *
 * @param {Object} props - Etat d'autorisation et callback de navigation.
 * @returns {import("react").JSX.Element} Page de gestion des utilisateurs.
 */
function UsersView({
  canSearchUsers,
  canDeleteUser,
  canLockUser,
  canUnlockUser,
  canValidateUser,
  authenticatedProfile,
  onBack,
}) {
  const [users, setUsers] = useState([]);
  const [filters, setFilters] = useState(createInitialUserFilters);
  const [activeFilters, setActiveFilters] = useState(createInitialUserFilters);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [activeUserActionId, setActiveUserActionId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const isAdmin = authenticatedProfile === "ADMIN";
  const displayedUsers = filterUsersLocally(users, activeFilters);

  useEffect(() => {
    let isCancelled = false;

    const fetchUsers = async () => {
      if (!isAdmin || !canSearchUsers) {
        setUsers([]);
        setIsLoadingUsers(false);
        return;
      }

      try {
        setIsLoadingUsers(true);
        setError("");
        setMessage("");
        const data = await UsersApi.searchUsers(buildBackendCriteria(activeFilters));
        if (!isCancelled) {
          setUsers(Array.isArray(data.users) ? data.users : []);
        }
      } catch (e) {
        if (!isCancelled) {
          setUsers([]);
          setError(e.message || "Impossible de charger les utilisateurs.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoadingUsers(false);
        }
      }
    };

    fetchUsers();
    return () => {
      isCancelled = true;
    };
  }, [activeFilters, canSearchUsers, isAdmin]);

  /**
   * Met a jour un filtre de recherche utilisateur.
   *
   * @param {string} key - Cle du filtre.
   * @param {string} value - Nouvelle valeur.
   * @returns {void} Met a jour l'etat local des filtres.
   */
  const updateFilter = (key, value) => {
    setFilters((previous) => ({
      ...previous,
      [key]: value,
    }));
  };

  /**
   * Applique les filtres saisis.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Soumission du formulaire.
   * @returns {void} Declenche une nouvelle recherche.
   */
  const applyFilters = (event) => {
    event.preventDefault();
    setActiveFilters(filters);
  };

  /**
   * Reinitialise tous les filtres utilisateur.
   *
   * @param {void} Aucun.
   * @returns {void} Recharge la liste sans filtre.
   */
  const resetFilters = () => {
    setFilters(initialUserFilters);
    setActiveFilters(initialUserFilters);
  };

  /**
   * Recharge les utilisateurs avec les filtres actifs.
   *
   * @param {void} Aucun.
   * @returns {Promise<void>} Met a jour la liste utilisateur.
   */
  const reloadUsers = async () => {
    const data = await UsersApi.searchUsers(buildBackendCriteria(activeFilters));
    setUsers(Array.isArray(data.users) ? data.users : []);
  };

  /**
   * Supprime un utilisateur apres confirmation.
   *
   * @param {Object} user - Utilisateur cible.
   * @returns {Promise<void>} Recharge la liste apres suppression.
   */
  const deleteUser = async (user) => {
    if (!window.confirm(`Supprimer l'utilisateur ${user.email} ?`)) {
      return;
    }
    await runUserAction(user.id, async () => {
      await UsersApi.deleteUser(user.id);
      await reloadUsers();
      setMessage("Utilisateur supprime.");
    });
  };

  /**
   * Bloque ou debloque un utilisateur.
   *
   * @param {Object} user - Utilisateur cible.
   * @returns {Promise<void>} Met a jour la ligne utilisateur.
   */
  const toggleUserLock = async (user) => {
    const isLocked = user.status === "LOCKED";
    await runUserAction(user.id, async () => {
      const data = isLocked ? await UsersApi.unlockUser(user.id) : await UsersApi.lockUser(user.id);
      setUsers((previous) => replaceUser(previous, data.user));
      setMessage(isLocked ? "Utilisateur debloque." : "Utilisateur bloque.");
    });
  };

  /**
   * Valide un utilisateur en attente de confirmation administrateur.
   *
   * @param {Object} user - Utilisateur cible.
   * @returns {Promise<void>} Met a jour la ligne utilisateur.
   */
  const validateUser = async (user) => {
    await runUserAction(user.id, async () => {
      const data = await UsersApi.validateUser(user.id);
      setUsers((previous) => replaceUser(previous, data.user));
      setMessage("Utilisateur valide.");
    });
  };

  /**
   * Execute une action utilisateur avec etat de chargement local.
   *
   * @param {number|string} userId - Identifiant utilisateur cible.
   * @param {Function} action - Action asynchrone a executer.
   * @returns {Promise<void>} Termine quand l'action est traitee.
   */
  const runUserAction = async (userId, action) => {
    try {
      setActiveUserActionId(userId);
      setError("");
      setMessage("");
      await action();
    } catch (e) {
      setError(e.message || "Action utilisateur impossible.");
    } finally {
      setActiveUserActionId(null);
    }
  };

  return (
    <main className="container usersPage">
      <button className="backButton" type="button" onClick={onBack}>
        Dashboard admin
      </button>

      <section className="addGameHeader">
        <p className="eyebrow">Administration</p>
        <h1>
          <span className="pageTitleWithIcon">
            <ProjectIcon />
            <span>Utilisateurs</span>
          </span>
        </h1>
      </section>

      {!isAdmin ? <p className="error">Acces reserve aux administrateurs.</p> : null}
      {isAdmin && !canSearchUsers ? (
        <p className="error">La route de gestion des utilisateurs n'est pas disponible.</p>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
      {message ? <p className="success">{message}</p> : null}
      {isLoadingUsers ? <ProgressBar label="Chargement des utilisateurs" /> : null}

      {isAdmin && canSearchUsers ? (
        <>
          <form className="usersFilterForm" onSubmit={applyFilters}>
            <label>
              Email
              <input
                type="search"
                value={filters.email}
                onChange={(event) => updateFilter("email", event.target.value)}
                placeholder="Rechercher un email"
              />
            </label>
            <label>
              Mode email
              <select
                value={filters.emailMode}
                onChange={(event) => updateFilter("emailMode", event.target.value)}
              >
                <option value="contains">Contient</option>
                <option value="exact">Exact</option>
              </select>
            </label>
            <label>
              Date de connexion
              <select
                value={filters.lastConnexionPeriod}
                onChange={(event) => updateFilter("lastConnexionPeriod", event.target.value)}
              >
                <option value="">Toutes</option>
                <option value="year">Cette annee</option>
                <option value="month">Ce mois</option>
                <option value="week">Cette semaine</option>
              </select>
            </label>
            <label>
              Date de creation
              <select
                value={filters.creationPeriod}
                onChange={(event) => updateFilter("creationPeriod", event.target.value)}
              >
                <option value="">Toutes</option>
                <option value="year">Cette annee</option>
                <option value="month">Ce mois</option>
                <option value="week">Cette semaine</option>
              </select>
            </label>
            <label>
              Statut
              <select
                value={filters.status}
                onChange={(event) => updateFilter("status", event.target.value)}
              >
                <option value="">Tous</option>
                {statusFilterOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="usersFilterActions">
              <button type="submit" disabled={isLoadingUsers}>
                Rechercher
              </button>
              <button className="secondaryButton" type="button" onClick={resetFilters}>
                Reinitialiser
              </button>
            </div>
          </form>

          {!isLoadingUsers ? (
            <section className="usersTableSection" aria-label="Liste des utilisateurs">
              <div className="usersResultSummary">
                {displayedUsers.length} utilisateur{displayedUsers.length > 1 ? "s" : ""} trouve
                {displayedUsers.length > 1 ? "s" : ""}
              </div>
              <div className="usersTableScroller">
                <table className="usersTable">
                  <thead>
                    <tr>
                      {userColumns.map((column) => (
                        <th key={column.key} scope="col">
                          {column.label}
                        </th>
                      ))}
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {displayedUsers.length > 0 ? (
                      displayedUsers.map((user) => (
                        <tr key={user.id}>
                          {userColumns.map((column) => (
                            <td key={column.key}>
                              {TableColumnFormatService.formatUserValue(
                                column.key,
                                user[column.key]
                              )}
                            </td>
                          ))}
                          <td>
                            <div className="usersRowActions">
                              {user.status === "WAITING_VALIDATION" ? (
                                <button
                                  className="iconActionButton"
                                  type="button"
                                  onClick={() => validateUser(user)}
                                  aria-label={`Valider ${user.email}`}
                                  title="Valider l'utilisateur"
                                  disabled={activeUserActionId === user.id || !canValidateUser}
                                >
                                  <svg aria-hidden="true" viewBox="0 0 24 24">
                                    <path d="M9.55 17.3 4.9 12.65l1.4-1.4 3.25 3.25 8.15-8.15 1.4 1.4-9.55 9.55Z" />
                                  </svg>
                                </button>
                              ) : null}
                              <button
                                className="iconActionButton"
                                type="button"
                                onClick={() => toggleUserLock(user)}
                                aria-label={
                                  user.status === "LOCKED"
                                    ? `Debloquer ${user.email}`
                                    : `Bloquer ${user.email}`
                                }
                                title={
                                  user.status === "LOCKED"
                                    ? "Debloquer l'utilisateur"
                                    : "Bloquer l'utilisateur"
                                }
                                disabled={
                                  activeUserActionId === user.id
                                  || (user.status === "LOCKED" ? !canUnlockUser : !canLockUser)
                                }
                              >
                                <svg aria-hidden="true" viewBox="0 0 24 24">
                                  {user.status === "LOCKED" ? (
                                    <path d="M17 9h-1V7a4 4 0 0 0-7.45-2.03l1.72 1.03A2 2 0 0 1 14 7v2H7a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2Zm0 10H7v-8h10v8Zm-5-6a2 2 0 0 0-1 3.73V18h2v-1.27A2 2 0 0 0 12 13Z" />
                                  ) : (
                                    <path d="M17 9h-1V7A4 4 0 0 0 8 7v2H7a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2Zm-7 0V7a2 2 0 0 1 4 0v2h-4Zm7 10H7v-8h10v8Zm-5-6a2 2 0 0 0-1 3.73V18h2v-1.27A2 2 0 0 0 12 13Z" />
                                  )}
                                </svg>
                              </button>
                              <button
                                className="iconActionButton dangerIconButton"
                                type="button"
                                onClick={() => deleteUser(user)}
                                aria-label={`Supprimer ${user.email}`}
                                title="Supprimer l'utilisateur"
                                disabled={activeUserActionId === user.id || !canDeleteUser}
                              >
                                <svg aria-hidden="true" viewBox="0 0 24 24">
                                  <path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-.7 12H7.7L7 9Zm3 2v8h2v-8h-2Zm4 0v8h2v-8h-2Z" />
                                </svg>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={userColumns.length + 1}>Aucun utilisateur trouve.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </main>
  );
}

/**
 * Remplace un utilisateur dans une liste par sa nouvelle version.
 *
 * @param {Array<Object>} users - Liste utilisateur courante.
 * @param {Object} updatedUser - Utilisateur modifie.
 * @returns {Array<Object>} Liste mise a jour.
 */
function replaceUser(users, updatedUser) {
  return users.map((user) => (user.id === updatedUser.id ? updatedUser : user));
}

/**
 * Construit les criteres envoyes au backend.
 *
 * @param {Object} currentFilters - Filtres actifs de la page utilisateurs.
 * @returns {Object} Criteres compatibles avec `GET /api/users`.
 */
function buildBackendCriteria(currentFilters) {
  const criteria = {};
  const email = currentFilters.email.trim();
  if (email) {
    criteria.name = email;
  }
  if (currentFilters.status) {
    criteria.status = currentFilters.status;
  }
  Object.assign(
    criteria,
    buildPeriodCriteria("creation_date", currentFilters.creationPeriod),
    buildPeriodCriteria("last_connexion_date", currentFilters.lastConnexionPeriod)
  );
  return criteria;
}

/**
 * Construit les bornes ISO d'un filtre de periode.
 *
 * @param {string} prefix - Prefixe attendu par l'API backend.
 * @param {string} period - Periode selectionnee.
 * @returns {Object} Bornes `from` et `to`, ou objet vide.
 */
function buildPeriodCriteria(prefix, period) {
  const range = getLocalPeriodRange(period);
  if (!range) {
    return {};
  }
  return {
    [`${prefix}_from`]: formatLocalIsoDateTime(range.from),
    [`${prefix}_to`]: formatLocalIsoDateTime(range.to),
  };
}

/**
 * Retourne les bornes locales d'une periode relative.
 *
 * @param {string} period - `year`, `month`, `week` ou chaine vide.
 * @returns {{from: Date, to: Date}|null} Bornes locales a appliquer.
 */
function getLocalPeriodRange(period) {
  const now = new Date();
  if (period === "year") {
    return { from: new Date(now.getFullYear(), 0, 1, 0, 0, 0), to: now };
  }
  if (period === "month") {
    return { from: new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0), to: now };
  }
  if (period === "week") {
    const dayOfWeek = now.getDay() || 7;
    const startOfWeek = new Date(now);
    startOfWeek.setDate(now.getDate() - dayOfWeek + 1);
    startOfWeek.setHours(0, 0, 0, 0);
    return { from: startOfWeek, to: now };
  }
  return null;
}

/**
 * Formate une date locale en ISO sans fuseau pour les filtres backend.
 *
 * @param {Date} date - Date locale a encoder.
 * @returns {string} Date au format `YYYY-MM-DDTHH:mm:ss`.
 */
function formatLocalIsoDateTime(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return [
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`,
    `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`,
  ].join("T");
}

/**
 * Applique les filtres traites cote frontend.
 *
 * @param {Array<Object>} users - Utilisateurs retournes par l'API.
 * @param {Object} currentFilters - Filtres actifs.
 * @returns {Array<Object>} Utilisateurs filtres.
 */
function filterUsersLocally(users, currentFilters) {
  const email = currentFilters.email.trim().toLowerCase();
  return users.filter((user) => {
    const userEmail = String(user.email || "").trim().toLowerCase();
    if (email && currentFilters.emailMode === "exact" && userEmail !== email) {
      return false;
    }
    if (email && currentFilters.emailMode !== "exact" && !userEmail.includes(email)) {
      return false;
    }
    return true;
  });
}

/**
 * Cree les filtres initiaux depuis les parametres d'URL supportes.
 *
 * @param {void} Aucun.
 * @returns {Object} Filtres utilisateur initiaux.
 */
function createInitialUserFilters() {
  const filters = { ...initialUserFilters };
  if (typeof window === "undefined") {
    return filters;
  }
  const status = String(new URLSearchParams(window.location.search).get("status") || "")
    .trim()
    .toUpperCase();
  if (["ACTIVE", "WAITING_VALIDATION", "LOCKED"].includes(status)) {
    filters.status = status;
  }
  return filters;
}

export default UsersView;
