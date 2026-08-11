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
  const displayedCounters = counters || [
    ["Plateformes liees", result.linked_platforms],
    ["Studios crees", result.created_studios],
    ["Jeux crees", result.created_games],
    ["Jeux associes", result.associated_games],
    ["Souhaits importes", result.wishlisted_games],
    ["Duree totale", totalImportDuration],
  ];
  const invalidWishlist = result.warnings?.invalid_wishlist || 0;
  const invalidGames = Array.isArray(result.warnings?.invalid_games)
    ? result.warnings.invalid_games
    : [];
  const platformMatches = Array.isArray(result.warnings?.platform_matches)
    ? result.warnings.platform_matches
    : [];
  const skippedGames = Array.isArray(result.warnings?.skipped_games)
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
      </dl>
      {isRefused ? (
        <p className="error">{formatImportRefusalMessage(refusal)}</p>
      ) : null}
      {contributionNotice ? (
        <div className="importContributionNotice">{contributionNotice}</div>
      ) : null}
      {invalidWishlist ? (
        <p className="warningText">
          {invalidWishlist} ligne(s) wishlist ignoree(s).
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
 * Affiche les plateformes rattachees avec verification manuelle.
 *
 * @param {Object} props - Warnings de plateformes incertaines.
 * @returns {import("react").JSX.Element} Liste des rattachements incertains.
 * @throws {void} Ne leve pas d'exception.
 */
function PlatformMatchWarningsList({ platformMatches }) {
  return (
    <section className="invalidImportedGames" aria-label="Plateformes a verifier">
      <h3>Plateformes a verifier</h3>
      <ul>
        {platformMatches.map((warning) => (
          <li key={`${warning.game_name}-${warning.imported_platform}-${warning.matched_platform}`}>
            <strong>{warning.game_name}</strong>
            <span>{formatPlatformMatchWarning(warning)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Affiche les jeux ignores faute de plateforme fiable.
 *
 * @param {Object} props - Warnings de jeux ignores.
 * @returns {import("react").JSX.Element} Liste des jeux ignores.
 * @throws {void} Ne leve pas d'exception.
 */
function SkippedGamesWarningsList({ skippedGames }) {
  return (
    <section className="invalidImportedGames" aria-label="Jeux ignores">
      <h3>Jeux ignores</h3>
      <ul>
        {skippedGames.map((warning) => (
          <li key={`${warning.game_name}-${warning.imported_platform}-${warning.reason}`}>
            <strong>{warning.game_name}</strong>
            <span>{formatSkippedGameWarning(warning)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Affiche les jeux importes avec des informations invalides ignorees.
 *
 * @param {Object} props - Warnings de jeux invalides.
 * @returns {import("react").JSX.Element} Liste des informations invalides.
 * @throws {void} Ne leve pas d'exception.
 */
function InvalidImportedGamesList({ invalidGames }) {
  return (
    <section className="invalidImportedGames" aria-label="Informations invalides importees">
      <h3>Informations ignorees</h3>
      <ul>
        {invalidGames.map((gameWarning) => (
          <li key={`${gameWarning.name}-${JSON.stringify(gameWarning.invalid_fields || [])}`}>
            <strong>{gameWarning.name}</strong>
            <span>{formatInvalidFields(gameWarning.invalid_fields || [])}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Formate les champs invalides d'un jeu pour affichage.
 *
 * @param {Array<Object>} invalidFields - Champs invalides retournes par l'API.
 * @returns {string} Description courte des champs invalides.
 * @throws {void} Ne leve pas d'exception.
 */
function formatInvalidFields(invalidFields) {
  return invalidFields
    .map((field) => {
      const label = field.field === "release_date" ? "Date de sortie" : field.field;
      return field.value ? `${label}: ${field.value}` : label;
    })
    .join(", ");
}

/**
 * Formate un warning de rattachement de plateforme incertain.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise du rattachement.
 * @throws {void} Ne leve pas d'exception.
 */
function formatPlatformMatchWarning(warning) {
  return `${warning.imported_platform || "-"} -> ${warning.matched_platform || "-"} (${Number(warning.score || 0)}%)`;
}

/**
 * Formate un warning de jeu ignore.
 *
 * @param {Object} warning - Warning retourne par l'API d'import.
 * @returns {string} Description concise du refus.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSkippedGameWarning(warning) {
  return `${warning.imported_platform || "-"} - ${formatSkippedGameReason(warning.reason)} (${Number(warning.score || 0)}%)`;
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
  return labels[reason] || "plateforme non fiable";
}

export { formatImportDuration };
export default ImportSummary;
