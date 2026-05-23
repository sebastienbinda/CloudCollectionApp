/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-20
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page publique de presentation fonctionnelle de l'application.
 */
import MainMenu from "./MainMenu";
import ProjectIcon from "./ProjectIcon";

/**
 * Presente les fonctionnalites de l'application aux visiteurs non connectes.
 *
 * @param {Object} props - Etat de session et callbacks de navigation du menu.
 * @returns {import("react").JSX.Element} Page About publique.
 */
function AboutView({
  isAuthenticated,
  authenticatedUsername,
  authenticatedProfile,
  platforms,
  selectedPlatform,
  onOpenAbout,
  onOpenHome,
  onOpenWishlist,
  onOpenPlatform,
  onOpenAdminDashboard,
  onLogout,
}) {
  return (
    <main className="appShell aboutShell">
      <header className="pageHeader aboutHeader">
        <img
          className="aboutHeaderImage"
          src="/about-home-image.jpg?v=ods-home-20260520"
          alt="Apercu visuel de la collection de jeux video"
        />
        <MainMenu
          isAuthenticated={isAuthenticated}
          username={authenticatedUsername}
          profile={authenticatedProfile}
          platforms={platforms}
          selectedPlatform={selectedPlatform}
          onOpenAbout={onOpenAbout}
          onOpenHome={onOpenHome}
          onOpenWishlist={onOpenWishlist}
          onOpenPlatform={onOpenPlatform}
          onOpenAdminDashboard={onOpenAdminDashboard}
          onLogout={onLogout}
        />
        <div className="aboutHeaderContent">
          <p className="eyebrow">CloudCollectionApp</p>
          <h1>
            <span className="pageTitleWithIcon">
              <ProjectIcon />
              <span className="aboutTitleFull">Qu'est-ce que CloudApplicationApp ?</span>
              <span className="aboutTitleMobile">CloudApplicationApp</span>
            </span>
          </h1>
          <p className="subtitle">
            Un espace simple pour organiser une collection de jeux video, garder une vue claire
            sur les plateformes et retrouver rapidement les informations importantes.
          </p>
        </div>
      </header>

      <section className="aboutContent" aria-label="Fonctionnalites de l'application">
        <div className="aboutIntro">
          <h2>Ce que permet l'application</h2>
          <p>
            CloudCollectionApp aide a suivre une collection personnelle sans tableur ouvert en
            permanence. Les jeux sont regroupes par plateforme, la liste de souhaits reste separee,
            et les vues principales mettent en avant les informations utiles pour parcourir,
            rechercher et maintenir la collection.
          </p>
        </div>

        <div className="aboutFeatureGrid">
          <article>
            <h3>Explorer la collection</h3>
            <p>
              Parcourez les jeux par plateforme, consultez les informations de chaque titre et
              retrouvez rapidement un jeu grace a la recherche.
            </p>
          </article>
          <article>
            <h3>Suivre les envies</h3>
            <p>
              Gardez une liste de souhaits dediee pour preparer les prochains ajouts et transferer
              les jeux vers la collection quand ils sont acquis.
            </p>
          </article>
          <article>
            <h3>Piloter les donnees</h3>
            <p>
              Une fois connecte, l'accueil affiche les indicateurs de collection et donne acces aux
              actions de mise a jour reservees a l'administrateur.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}

export default AboutView;
