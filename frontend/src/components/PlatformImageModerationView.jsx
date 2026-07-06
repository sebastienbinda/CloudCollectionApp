/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-20
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page admin dediee a la moderation des images de plateformes.
 */
import PageLayout from "./PageLayout";
import PlatformImageModerationSection from "./PlatformImageModerationSection";

/**
 * Affiche la page dediee a la moderation des images de plateformes.
 *
 * @param {Object} props - Etat de session, permissions et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue de moderation des images.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function PlatformImageModerationView({
  platformImageModeration,
  canModeratePlatformImages,
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
}) {
  return (
    <PageLayout
      shellClassName="appShell configuration"
      eyebrow="Administration"
      title="Images de plateformes"
      subtitle="Moderez les images proposees pour les plateformes de la Bibliotheque."
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
      <button className="backButton" type="button" onClick={onOpenConfiguration}>
        Retour
      </button>
      {canModeratePlatformImages ? (
        <PlatformImageModerationSection moderation={platformImageModeration} />
      ) : (
        <p className="error">La moderation des images de plateformes est indisponible.</p>
      )}
    </PageLayout>
  );
}

export default PlatformImageModerationView;
