/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page publique d'accueil de la Bibliotheque.
 */
import { formatNumber } from "../collectionUtils";
import CardComponent from "./CardComponent";
import CardCountComponent from "./CardCountComponent";
import CardHeaderComponent from "./CardHeaderComponent";
import GridComponent from "./GridComponent";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

/**
 * Affiche les compteurs publics et les acces aux entites Bibliotheque.
 *
 * @param {Object} props - Etat de page, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Page Bibliotheque publique.
 */
function LibraryHomeView({
  entities,
  entitiesError,
  isLoadingEntities,
  isAuthenticated,
  canUseCollectionViews,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenLibraryPlatforms,
  onOpenLibraryStudios,
  onOpenLibraryGames,
  onOpenConfiguration,
  onLogout,
}) {
  const cards = [
    ["Plateformes", entities.platforms, onOpenLibraryPlatforms],
    ["Studios", entities.studios, onOpenLibraryStudios],
    ["Jeux", entities.games, onOpenLibraryGames],
  ];

  return (
    <PageLayout
      shellClassName="appShell libraryShell"
      eyebrow="Bibliotheque publique"
      title="Bibliotheque"
      subtitle="Consultez les plateformes, studios et jeux du referentiel commun."
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      {isLoadingEntities ? <ProgressBar label="Chargement de la Bibliotheque" /> : null}
      {entitiesError ? <p className="error">{entitiesError}</p> : null}

      <section className="platformSection libraryEntitySection">
        <div className="sectionHeader">
          <div>
            <h2>Entites</h2>
            <span>Referentiel global</span>
          </div>
        </div>
        <GridComponent className="libraryEntityGrid">
          {cards.map(([label, count, onClick]) => (
            <CardComponent key={label} className="libraryEntityCard" onClick={onClick}>
              <CardHeaderComponent>
                <h3>{label}</h3>
                <CardCountComponent>{formatNumber(count)} elements</CardCountComponent>
              </CardHeaderComponent>
            </CardComponent>
          ))}
        </GridComponent>
      </section>
    </PageLayout>
  );
}

export default LibraryHomeView;
