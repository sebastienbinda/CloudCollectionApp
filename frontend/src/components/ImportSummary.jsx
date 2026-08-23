/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-26
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : resume reutilisable des imports utilisateur et admin.
 */
import { useState } from "react";

import { getImportFieldLabel } from "../hooks/collection/importFieldLabels";
import UserCollectionApi from "../services/UserCollectionApi";

/**
 * Affiche le resume d'un import termine.
 *
 * @param {Object} props - Resultat d'import, compteurs et callback de navigation.
 * @returns {import("react").JSX.Element} Resume d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function ImportSummary({
  actionLabel = "Ouvrir Ma collection",
  contributionNotice,
  counters,
  onAction,
  result,
}) {
  const refusal = result.refusal || {};
  const isRefused = Boolean(refusal.refused);
  const totalImportDuration = formatImportDuration(
    result.warnings?.total_import_duration_seconds
  );
  const invalidGamesCount = Number(refusal.invalid_games_count || 0);
  const displayedCounters = counters || [
    ["Plateformes liees", result.linked_platforms],
    ["Studios crees", result.created_studios],
    ["Jeux crees", result.created_games],
    ["Jeux associes", result.associated_games],
    ["Jeux en liste de souhaits", result.wishlisted_games],
    ["Duree totale", totalImportDuration],
  ];
  const invalidWishlist = result.warnings?.invalid_wishlist || 0;
  const invalidGames = Array.isArray(result.warnings?.invalid_games)
    ? result.warnings.invalid_games
    : [];
  const platformMatches = Array.isArray(result.warnings?.user_platform_matches)
    ? result.warnings.user_platform_matches
    : Array.isArray(result.warnings?.platform_matches)
    ? result.warnings.platform_matches
    : [];
  const platformMatchesCount = platformMatches.length;
  const skippedGames = Array.isArray(result.warnings?.user_skipped_games)
    ? result.warnings.user_skipped_games
    : Array.isArray(result.warnings?.skipped_games)
    ? result.warnings.skipped_games
    : [];
  return (
    <section className="importSummary" aria-label="Resume de l'import">
      <h2>{isRefused ? "Import refuse" : "Import termine"}</h2>
      <dl>
        {displayedCounters.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
        {invalidGamesCount > 0 ? (
          <div className={isRefused ? "importErrorCounterRefused" : "importErrorCounterAccepted"}>
            <dt>Jeux avec erreur</dt>
            <dd>{formatInvalidGamesRatio(refusal)}</dd>
          </div>
        ) : null}
        {platformMatchesCount > 0 ? (
          <div className="importErrorCounterAccepted">
            <dt>Jeux à vérifier</dt>
            <dd>{platformMatchesCount}</dd>
          </div>
        ) : null}
      </dl>
      {isRefused ? (
        <p className="error">{formatImportRefusalMessage(refusal)}</p>
      ) : null}
      {contributionNotice ? (
        <div className="importContributionNotice">{contributionNotice}</div>
      ) : null}
      {invalidWishlist ? (
        <p className="warningText">
          {invalidWishlist} ligne(s) de liste de souhaits ignorée(s).
        </p>
      ) : null}
      {invalidGames.length > 0 ? (
        <InvalidImportedGamesList invalidGames={invalidGames} />
      ) : null}
      {platformMatches.length > 0 ? (
        <PlatformMatchWarningsList platformMatches={platformMatches} />
      ) : null}
      {skippedGames.length > 0 ? (
        <SkippedGamesWarningsList skippedGames={skippedGames} />
      ) : null}
      <button type="button" onClick={onAction}>
        {actionLabel}
      </button>
    </section>
  );
}

/**
 * Formate le message de refus global d'un fichier d'import.
 *
 * @param {Object} refusal - Decision de refus retournee par le backend.
 * @returns {string} Message clair pour corriger puis reimporter le fichier.
 * @throws {void} Ne leve pas d'exception.
 */
function formatImportRefusalMessage(refusal) {
  const invalidGamesCount = Number(refusal.invalid_games_count || 0);
  const totalGamesCount = Number(refusal.total_games_count || 0);
  const ratio = totalGamesCount > 0
    ? `${invalidGamesCount}/${totalGamesCount}`
    : `${invalidGamesCount}/0`;
  return (
    `Le fichier a ete refuse a cause du nombre d'erreurs: ${ratio} jeux `
    + "contiennent au moins une erreur. Corrigez votre fichier avant de le reimporter a nouveau."
  );
}

/**
 * Formate la duree totale d'import retournee par le backend.
 *
 * @param {number|string|undefined} durationSeconds - Duree brute en secondes.
 * @returns {string} Duree lisible pour le resume d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function formatImportDuration(durationSeconds) {
  const duration = Number(durationSeconds || 0);
  if (!Number.isFinite(duration) || duration <= 0) {
    return "0 s";
  }
  if (duration < 1) {
    return `${Math.round(duration * 1000)} ms`;
  }
  if (duration < 60) {
    return `${duration.toFixed(2)} s`;
  }
  const minutes = Math.floor(duration / 60);
  const seconds = Math.round(duration % 60);
  return `${minutes} min ${seconds.toString().padStart(2, "0")} s`;
}

/**
 * Formate le nombre de jeux contenant une erreur sur le total lu.
 *
 * @param {Object} refusal - Decision de refus ou compteurs d'erreurs d'import.
 * @returns {string} Ratio lisible pour le resume d'import.
 * @throws {void} Ne leve pas d'exception.
 */
function formatInvalidGamesRatio(refusal) {
  const invalidGamesCount = Number(refusal.invalid_games_count || 0);
  const totalGamesCount = Number(refusal.total_games_count || 0);
  return `${invalidGamesCount}/${totalGamesCount}`;
}

/**
 * Affiche les plateformes rattachees avec verification manuelle.
 *
 * @param {Object} props - Warnings de plateformes incertaines.
 * @returns {import("react").JSX.Element} Liste des rattachements incertains.
 * @throws {void} Ne leve pas d'exception.
 */
function PlatformMatchWarningsList({ platformMatches }) {
  const groupedPlatformMatches = groupPlatformWarningsByPlatformAndCause(platformMatches);
  return (
    <section className="invalidImportedGames" aria-label="Plateformes a verifier">
      <h3>Plateformes à vérifier par un admin</h3>
      <ul>
        {groupedPlatformMatches.map((group) => (
          <li key={group.key}>
            <strong>Plateforme dans votre fichier : {group.importedPlatform}</strong>
            <span>
              Statut : ces jeux sont importés, mais la plateforme doit être validée
              par un admin.
            </span>
            <span>Raison : {formatPlatformRefusal(group.warning)}</span>
            <span>Jeux en attente de validation admin pour cette plateforme :</span>
            <ul className="invalidAssociatedGames">
              {group.games.map((gameName) => (
                <li key={gameName}>{gameName}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Regroupe les avertissements de plateforme par plateforme importee et cause.
 *
 * @param {Array<Object>} platformWarnings - Plateformes a verifier retournees par l'API.
 * @returns {Array<Object>} Groupes affichables par l'IHM.
 * @throws {void} Ne leve pas d'exception.
 */
function groupPlatformWarningsByPlatformAndCause(platformWarnings) {
  const groupsByKey = new Map();
  platformWarnings.forEach((warning) => {
    const importedPlatform = warning.imported_platform || "-";
    const cause = warning.message || `${warning.matched_platform || "-"}-${warning.score || 0}`;
    const key = `${importedPlatform}-${cause}`;
    const group = groupsByKey.get(key) || {
      key,
      importedPlatform,
      warning,
      games: [],
    };
    group.games.push(warning.game_name || "-");
    groupsByKey.set(key, group);
  });
  return Array.from(groupsByKey.values());
}

/**
 * Affiche les jeux ignores faute de plateforme fiable.
 *
 * @param {Object} props - Warnings de jeux ignores.
 * @returns {import("react").JSX.Element} Liste des jeux ignores.
 * @throws {void} Ne leve pas d'exception.
 */
function SkippedGamesWarningsList({ skippedGames }) {
  const groupedSkippedGames = groupSkippedGamesByPlatformAndCause(skippedGames);
  return (
    <section className="invalidImportedGames" aria-label="Jeux non importés">
      <h3>Jeux non importés</h3>
      <span>Vous pouvez corriger votre fichier puis le réimporter pour corriger ces erreurs.</span>
      <ul>
        {groupedSkippedGames.map((group) => (
          <li key={group.key}>
            <strong>{group.importedPlatform}</strong>
            <span>{formatSkippedPlatformRefusal(group.warning)}</span>
            <ul className="invalidAssociatedGames">
              {group.games.map((gameName) => (
                <li key={gameName}>{gameName}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Regroupe les jeux ignores par plateforme importee et cause de refus.
 *
 * @param {Array<Object>} skippedGames - Jeux ignores retournes par l'API.
 * @returns {Array<Object>} Groupes affichables par l'IHM.
 * @throws {void} Ne leve pas d'exception.
 */
function groupSkippedGamesByPlatformAndCause(skippedGames) {
  const groupsByKey = new Map();
  skippedGames.forEach((warning) => {
    const importedPlatform = warning.imported_platform || "-";
    const cause = warning.message || warning.reason || "";
    const key = `${importedPlatform}-${cause}`;
    const group = groupsByKey.get(key) || {
      key,
      importedPlatform,
      warning,
      games: [],
    };
    group.games.push(warning.game_name || "-");
    groupsByKey.set(key, group);
  });
  return Array.from(groupsByKey.values());
}

/**
 * Affiche les jeux importes avec des informations invalides ignorees.
 *
 * @param {Object} props - Warnings de jeux invalides.
 * @returns {import("react").JSX.Element} Liste des informations invalides.
 * @throws {void} Ne leve pas d'exception.
 */
function InvalidImportedGamesList({ invalidGames }) {
  const [detailsByFieldKey, setDetailsByFieldKey] = useState({});
  const groupedInvalidFields = groupInvalidFieldsByField(invalidGames);

  async function toggleInvalidFieldDetails(fieldGroup) {
    const fieldKey = invalidFieldGroupKey(fieldGroup.field);
    const currentDetails = detailsByFieldKey[fieldKey];
    if (currentDetails?.isLoading) {
      return;
    }
    if (currentDetails?.data || currentDetails?.error) {
      setDetailsByFieldKey((currentValues) => ({
        ...currentValues,
        [fieldKey]: {
          ...currentDetails,
          isOpen: !currentDetails.isOpen,
        },
      }));
      return;
    }
    setDetailsByFieldKey((currentValues) => ({
      ...currentValues,
      [fieldKey]: { isLoading: true, isOpen: true, data: null, error: "" },
    }));
    try {
      const data = await UserCollectionApi.fetchImportInvalidValueHelp(
        fieldGroup.field,
        fieldGroup.sampleValue || "",
      );
      setDetailsByFieldKey((currentValues) => ({
        ...currentValues,
        [fieldKey]: { isLoading: false, isOpen: true, data, error: "" },
      }));
    } catch (error) {
      setDetailsByFieldKey((currentValues) => ({
        ...currentValues,
        [fieldKey]: {
          isLoading: false,
          isOpen: true,
          data: null,
          error: error?.message || "Impossible de charger le détail.",
        },
      }));
    }
  }

  return (
    <section className="invalidImportedGames" aria-label="Informations invalides importées">
      <h3>Informations ignorées</h3>
      <ul>
        {groupedInvalidFields.map((fieldGroup) => (
          <li key={fieldGroup.key}>
            <InvalidFieldGroupWarning
              details={detailsByFieldKey[invalidFieldGroupKey(fieldGroup.field)]}
              fieldGroup={fieldGroup}
              onToggleDetails={toggleInvalidFieldDetails}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Regroupe les informations ignorees par champ refuse.
 *
 * @param {Array<Object>} invalidGames - Jeux avec champs invalides retournes par l'API.
 * @returns {Array<Object>} Groupes affichables par champ refuse.
 * @throws {void} Ne leve pas d'exception.
 */
function groupInvalidFieldsByField(invalidGames) {
  const groupsByKey = new Map();
  invalidGames.forEach((gameWarning) => {
    (gameWarning.invalid_fields || []).forEach((fieldWarning) => {
      const field = fieldWarning.field || "";
      const key = invalidFieldGroupKey(field);
      const group = groupsByKey.get(key) || {
        key,
        field,
        sampleValue: fieldWarning.value || "",
        games: [],
      };
      group.games.push({
        gameName: gameWarning.name || "-",
        value: fieldWarning.value || "",
      });
      groupsByKey.set(key, group);
    });
  });
  return Array.from(groupsByKey.values());
}

/**
 * Affiche un groupe de valeurs refusees et son aide chargee a la demande.
 *
 * @param {Object} props - Groupe invalide et etat d'aide.
 * @returns {import("react").JSX.Element} Groupe invalide avec bouton de detail.
 * @throws {void} Ne leve pas d'exception.
 */
function InvalidFieldGroupWarning({ details, fieldGroup, onToggleDetails }) {
  const isOpen = Boolean(details?.isOpen);
  return (
    <div className="invalidFieldWarning">
      <strong>Champ ignoré : {formatInvalidFieldLabel(fieldGroup.field)}</strong>
      <span>Valeurs refusées dans votre fichier :</span>
      <ul className="invalidAssociatedGames invalidRejectedValues">
        {fieldGroup.games.map((game) => (
          <li key={`${game.gameName}-${game.value}`}>
            {game.gameName}: "{game.value}" Valeur refusée
          </li>
        ))}
      </ul>
      <button
        type="button"
        className="fieldHelpToggle invalidFieldDetailsButton"
        disabled={details?.isLoading}
        onClick={() => onToggleDetails(fieldGroup)}
      >
        {details?.isLoading ? "Chargement" : isOpen ? "Masquer" : "Plus d'info"}
      </button>
      {isOpen && details?.data ? <InvalidFieldDetails details={details.data} /> : null}
      {isOpen && details?.error ? (
        <span className="invalidFieldDetailsError">{details.error}</span>
      ) : null}
    </div>
  );
}

/**
 * Affiche la raison d'un refus et les valeurs possibles lorsqu'elles existent.
 *
 * @param {Object} props - Aide retournee par le backend.
 * @returns {import("react").JSX.Element} Detail du refus.
 * @throws {void} Ne leve pas d'exception.
 */
function InvalidFieldDetails({ details }) {
  const possibleValues = Array.isArray(details.possible_values)
    ? details.possible_values
    : [];
  return (
    <span className="invalidFieldDetails">
      <span>{details.reason}</span>
      {possibleValues.length > 0 ? (
        <span>Valeurs possibles : {possibleValues.join(", ")}</span>
      ) : null}
    </span>
  );
}

/**
 * Formate le libelle d'un champ invalide.
 *
 * @param {string} field - Champ invalide retourne par l'API.
 * @returns {string} Libelle lisible du champ.
 * @throws {void} Ne leve pas d'exception.
 */
function formatInvalidFieldLabel(field) {
  return getImportFieldLabel(field);
}

function invalidFieldGroupKey(field) {
  return field || "";
}

/**
 * Formate la cause d'un groupe de plateformes a verifier.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise de la cause.
 * @throws {void} Ne leve pas d'exception.
 */
function formatPlatformRefusal(warning) {
  if (warning.message) {
    return warning.message;
  }
  return `${warning.matched_platform || "-"} (${Number(warning.score || 0)}%)`;
}

/**
 * Formate la cause d'un groupe de jeux ignores.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise de la cause.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSkippedPlatformRefusal(warning) {
  if (warning.message) {
    return warning.message;
  }
  return `${formatSkippedGameReason(warning.reason)} (${Number(warning.score || 0)}%)`;
}

/**
 * Traduit la raison technique d'un jeu ignore.
 *
 * @param {string} reason - Raison backend.
 * @returns {string} Raison lisible.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSkippedGameReason(reason) {
  const labels = {
    ambiguous: "correspondance ambigue",
    low_score: "score trop faible",
    no_match: "aucune correspondance",
  };
  return labels[reason] || reason || "plateforme non fiable";
}

export { formatImportDuration, formatInvalidGamesRatio };
export default ImportSummary;
