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
            Transformez votre fichier de collection personnel en site en ligne, disponible a tout
            moment, avec un simple import ODS. Votre collection reste privee, la base de jeux
            s'enrichit avec la communaute.
          </p>
        </div>
      </header>

      <section className="aboutContent" aria-label="Fonctionnalites de l'application">
        <div className="aboutIntro">
          <h2>Ce que permet l'application</h2>
          <p>
            CloudCollectionApp transforme un tableur local en espace web personnel. Apres
            inscription, importez votre fichier ODS et retrouvez votre collection depuis n'importe
            quel appareil. Vos jeux restent rattaches a votre compte, pendant que le catalogue commun
            des plateformes, studios et jeux progresse grace aux imports de tous les utilisateurs.
          </p>
        </div>

        <div className="aboutFeatureGrid">
          <article>
            <h3>Du fichier au site</h3>
            <p>
              Importez votre collection ODS une seule fois et accedez ensuite a vos plateformes,
              jeux et indicateurs depuis une interface en ligne claire.
            </p>
          </article>
          <article>
            <h3>Collection privee</h3>
            <p>
              Votre collection personnelle reste associee a votre compte. Elle n'est pas exposee aux
              autres utilisateurs et les acces passent par votre session connectee.
            </p>
          </article>
          <article>
            <h3>Base commune</h3>
            <p>
              Chaque import aide a enrichir le referentiel commun des jeux, plateformes et studios,
              pour rendre la recherche et les futures collections plus utiles.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}

export default AboutView;
