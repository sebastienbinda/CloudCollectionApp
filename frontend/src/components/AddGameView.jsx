/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Page contenant le formulaire d'ajout futur d'un jeu.
 *
 * @param {Object} props - Etat du formulaire, listes de suggestions et callbacks.
 * @returns {import("react").JSX.Element} Vue d'ajout de jeu.
 */
function AddGameView({
  platforms,
  gameForm,
  addGameColumnValues,
  addGameError,
  addGameMessage,
  isAddingGame,
  canAddGame,
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
  onOpenFeedback,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
  onBack,
  onSubmit,
  onFieldChange,
}) {
  const platformChoices = (addGameColumnValues.Plateforme || []).length > 0
    ? addGameColumnValues.Plateforme
    : platforms.map((platform) => platform.name || "");

  return (
    <PageLayout
      shellClassName="container"
      eyebrow="Nouveau jeu"
      title="Ajouter un jeu"
      subtitle="Le jeu sera ajoute dans la collection en conservant la presentation de votre fichier."
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
      onOpenFeedback={onOpenFeedback}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {addGameError ? <p className="error">{addGameError}</p> : null}
      {addGameMessage ? <p className="success">{addGameMessage}</p> : null}

      <form className="addGameForm" onSubmit={onSubmit}>
        <label>
          Plateforme
          <select
            value={gameForm.platform}
            onChange={(event) => onFieldChange("platform", event.target.value)}
            required
          >
            <option value="">Choisir une plateforme</option>
            {platformChoices.map((platform) => (
              <option key={platform} value={platform}>
                {platform}
              </option>
            ))}
          </select>
        </label>

        <label>
          Nom du jeu
          <input
            type="text"
            value={gameForm["Nom du jeu"]}
            onChange={(event) => onFieldChange("Nom du jeu", event.target.value)}
            required
          />
        </label>

        <label>
          Studio
          <input
            list="studio-options"
            type="text"
            value={gameForm.Studio}
            onChange={(event) => onFieldChange("Studio", event.target.value)}
          />
          <datalist id="studio-options">
            {(addGameColumnValues.Studio || []).map((studio) => (
              <option key={studio} value={studio} />
            ))}
          </datalist>
        </label>

        <label>
          Date de sortie
          <input
            type="date"
            value={gameForm["Date de sortie"]}
            onChange={(event) => onFieldChange("Date de sortie", event.target.value)}
          />
        </label>

        <label>
          Date d'achat
          <input
            type="date"
            value={gameForm["Date d'achat"]}
            onChange={(event) => onFieldChange("Date d'achat", event.target.value)}
            required
          />
        </label>

        <label>
          Lieu d'achat
          <input
            type="text"
            value={gameForm["Lieu d'achat"]}
            onChange={(event) => onFieldChange("Lieu d'achat", event.target.value)}
            required
          />
        </label>

        <label>
          Note
          <input
            type="text"
            value={gameForm.Note}
            onChange={(event) => onFieldChange("Note", event.target.value)}
            placeholder="8/10"
          />
        </label>

        <label>
          Prix d'achat
          <input
            type="number"
            min="0"
            step="0.01"
            value={gameForm["Prix d'achat"]}
            onChange={(event) => onFieldChange("Prix d'achat", event.target.value)}
            required
          />
        </label>

        <label>
          Version
          <input
            list="version-options"
            type="text"
            value={gameForm.Version}
            onChange={(event) => onFieldChange("Version", event.target.value)}
            placeholder="FR, PAL, NTSC..."
          />
          <datalist id="version-options">
            {(addGameColumnValues.Version || []).map((version) => (
              <option key={version} value={version} />
            ))}
          </datalist>
        </label>

        <div className="formActions">
          <button type="button" className="secondaryButton" onClick={onBack}>
            Annuler
          </button>
          {canAddGame ? (
            <button type="submit" disabled={isAddingGame}>
              Ajouter le jeu
            </button>
          ) : null}
        </div>
        {isAddingGame ? <ProgressBar label="Ajout du jeu en cours" /> : null}
      </form>
    </PageLayout>
  );
}

export default AddGameView;
