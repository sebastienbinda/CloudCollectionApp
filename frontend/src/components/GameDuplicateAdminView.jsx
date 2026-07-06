/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-27
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React admin de correction des doublons de jeux.
 */
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche l'ecran admin de correction d'un doublon de jeu.
 *
 * @param {Object} props - Etat de page, session et callbacks.
 * @returns {import("react").JSX.Element} Vue de correction.
 */
function GameDuplicateAdminView({
  duplicatePage,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onOpenGameDetail,
  onBack,
}) {
  const duplicateGame = duplicatePage.duplicateGame;
  const selectedCandidate = duplicatePage.selectedCandidate;
  const resolutionResult = duplicatePage.resolutionResult;
  const isResultScreen = Boolean(resolutionResult);

  return (
    <PageLayout
      shellClassName="appShell gameDuplicateShell"
      eyebrow="Administration"
      title={isResultScreen ? "Resultat de resolution" : "Correction de doublon"}
      subtitle={buildSubtitle(duplicateGame, resolutionResult)}
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <button className="backButton" type="button" onClick={onBack}>
        Retour
      </button>

      {isResultScreen ? (
        <GameDuplicateResultScreen
          result={resolutionResult}
          onBackToForm={duplicatePage.clearResolutionResult}
          onOpenGameDetail={onOpenGameDetail}
        />
      ) : null}

      {duplicatePage.isLoading ? <ProgressBar label="Chargement du doublon" /> : null}
      {!isResultScreen && duplicatePage.error ? <p className="error">{duplicatePage.error}</p> : null}

      {!isResultScreen && duplicateGame ? (
        <section className="gameDuplicateWorkspace" aria-label="Correction de doublon">
          <div className="gameDuplicateHeader">
            <div>
              <span>Jeu signale</span>
              <strong>{duplicateGame.name}</strong>
              <small>{duplicateGame.platform}</small>
            </div>
            <button
              className="secondaryButton"
              type="button"
              disabled={duplicatePage.isSaving}
              onClick={duplicatePage.rejectDuplicate}
            >
              Refuser le doublon
            </button>
          </div>

          <form className="gameDuplicateSearch" onSubmit={duplicatePage.searchCandidates}>
            <label>
              Jeu a conserver
              <input
                type="search"
                value={duplicatePage.candidateSearch}
                onChange={(event) => duplicatePage.setCandidateSearch(event.target.value)}
                placeholder="Rechercher sur la meme plateforme"
              />
            </label>
            <button type="submit" disabled={duplicatePage.isLoading}>
              Rechercher
            </button>
          </form>

          <select
            className="gameDuplicateCandidateSelect"
            value={duplicatePage.selectedCandidateId}
            onChange={(event) => duplicatePage.setSelectedCandidateId(event.target.value)}
          >
            {duplicatePage.candidates.map((candidate) => (
              <option key={candidate.id} value={candidate.id}>
                {candidate.name}
              </option>
            ))}
          </select>

          {selectedCandidate ? (
            <>
              <label className="gameDuplicateAliasChoice">
                <input
                  type="checkbox"
                  checked={duplicatePage.keepAlias}
                  onChange={(event) => duplicatePage.setKeepAlias(event.target.checked)}
                />
                Conserver le nom du doublon comme alias
              </label>

              <div className="gameDuplicateComparison">
                {duplicatePage.fields.map((field) => (
                  <fieldset key={field.key}>
                    <legend>{field.label}</legend>
                    <label>
                      <input
                        type="radio"
                        name={`duplicate-field-${field.key}`}
                        checked={duplicatePage.fieldSources[field.key] !== "duplicate"}
                        onChange={() => duplicatePage.updateFieldSource(field.key, "target")}
                      />
                      <span>{formatFieldValue(selectedCandidate, field.key)}</span>
                    </label>
                    <label>
                      <input
                        type="radio"
                        name={`duplicate-field-${field.key}`}
                        checked={duplicatePage.fieldSources[field.key] === "duplicate"}
                        onChange={() => duplicatePage.updateFieldSource(field.key, "duplicate")}
                      />
                      <span>{formatFieldValue(duplicateGame, field.key)}</span>
                    </label>
                  </fieldset>
                ))}
              </div>

              <button
                className="primaryAction"
                type="button"
                disabled={duplicatePage.isSaving}
                onClick={duplicatePage.mergeDuplicate}
              >
                Fusionner le doublon
              </button>
            </>
          ) : null}

        </section>
      ) : null}
    </PageLayout>
  );
}

function GameDuplicateResultScreen({ result, onBackToForm, onOpenGameDetail }) {
  const actionLabel = result.action === "merge" ? "Fusion" : "Refus";
  const targetGame = result.targetGame;
  const canOpenTarget = result.isSuccess && targetGame?.id;

  return (
    <section
      className={`gameDuplicateResultScreen ${result.isSuccess ? "isSuccess" : "isFailure"}`}
      aria-label="Resultat de correction du doublon"
    >
      <div className="gameDuplicateResultBanner">
        <span>{result.isSuccess ? "Succes" : "Echec"}</span>
        <strong>{result.message}</strong>
      </div>

      <dl className="gameDuplicateResultFacts">
        <div>
          <dt>Action</dt>
          <dd>{actionLabel}</dd>
        </div>
        <div>
          <dt>Jeu signale</dt>
          <dd>{result.duplicateGame?.name || "-"}</dd>
        </div>
        <div>
          <dt>Jeu conserve</dt>
          <dd>{targetGame?.name || targetGame?.id || "-"}</dd>
        </div>
        <div>
          <dt>Statut</dt>
          <dd>{result.isSuccess ? "Termine" : buildFailureStatus(result)}</dd>
        </div>
      </dl>

      {result.isSuccess && result.action === "merge" ? (
        <div className="gameDuplicateResultMetrics" aria-label="Compteurs de fusion">
          <Metric label="Utilisateurs rattaches" value={result.result?.remapped_user_count} />
          <Metric label="Lignes remappees" value={result.result?.updated_collection_rows} />
          <Metric label="Lignes fusionnees" value={result.result?.merged_collection_rows} />
          <Metric label="Alias cree" value={result.result?.alias_created ? "Oui" : "Non"} />
        </div>
      ) : null}

      <div className="gameDuplicateResultActions">
        {canOpenTarget ? (
          <button
            className="primaryAction"
            type="button"
            onClick={() => onOpenGameDetail(targetGame, "library")}
          >
            {result.action === "merge" ? "Voir le jeu fusionne" : "Voir le jeu"}
          </button>
        ) : null}
        {!result.isSuccess ? (
          <button className="secondaryButton" type="button" onClick={onBackToForm}>
            Retour au formulaire
          </button>
        ) : null}
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
    </div>
  );
}

function buildSubtitle(duplicateGame, resolutionResult) {
  if (resolutionResult?.isSuccess) {
    return "Operation terminee";
  }
  if (resolutionResult && !resolutionResult.isSuccess) {
    return "Operation echouee";
  }
  return duplicateGame ? duplicateGame.name : "Jeu signale";
}

function buildFailureStatus(result) {
  if (result.errorStatus) {
    return `Erreur ${result.errorStatus}`;
  }
  return "Erreur";
}

function formatFieldValue(game, fieldKey) {
  const value = game?.[fieldKey === "developer_id" ? "developer" : fieldKey === "editor_id" ? "editor" : fieldKey];
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export default GameDuplicateAdminView;
