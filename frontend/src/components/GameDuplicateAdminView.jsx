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
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  onBack,
}) {
  const duplicateGame = duplicatePage.duplicateGame;
  const selectedCandidate = duplicatePage.selectedCandidate;

  return (
    <PageLayout
      shellClassName="appShell gameDuplicateShell"
      eyebrow="Administration"
      title="Correction de doublon"
      subtitle={duplicateGame ? duplicateGame.name : "Jeu signale"}
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <button className="backButton" type="button" onClick={onBack}>
        Retour
      </button>

      {duplicatePage.isLoading ? <ProgressBar label="Chargement du doublon" /> : null}
      {duplicatePage.error ? <p className="error">{duplicatePage.error}</p> : null}

      {duplicateGame ? (
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

          {duplicatePage.result ? (
            <pre className="gameDuplicateResult">
              {JSON.stringify(duplicatePage.result.result || duplicatePage.result, null, 2)}
            </pre>
          ) : null}
        </section>
      ) : null}
    </PageLayout>
  );
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
