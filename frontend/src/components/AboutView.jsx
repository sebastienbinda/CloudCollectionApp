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
            moment, avec un simple import. Votre collection reste privee, la base de jeux
            s'enrichit avec la communaute.
          </p>
        </div>
      </header>

      <section className="aboutContent" aria-label="Fonctionnalites de l'application">
        <div className="aboutIntro">
          <h2>Ce que permet l'application</h2>
          <p>
            CloudCollectionApp transforme un tableur local en espace web personnel. Apres
            inscription, importez votre fichier de collection et retrouvez votre collection depuis
            n'importe quel appareil. Vos jeux restent rattaches a votre compte, pendant que le
            catalogue commun des plateformes, studios et jeux progresse grace aux imports de tous
            les utilisateurs.
          </p>
        </div>

        <div className="aboutFeatureGrid">
          <article>
            <h3>Du fichier au site</h3>
            <p>
              Importez votre fichier de collection une seule fois et accedez ensuite a vos
              plateformes, jeux et indicateurs depuis une interface en ligne claire. Vous pouvez
              ensuite telecharger un fichier mis a jour avec les modifications faites sur le site.
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

        <div className="aboutIntro">
          <h2>Les points cles au quotidien</h2>
          <p>
            Une fois la collection importee, l'application devient un tableau de bord personnel
            pour consulter, suivre et faire evoluer votre collection sans revenir au fichier source
            pour chaque action.
          </p>
        </div>

        <div className="aboutFeatureGrid">
          <article>
            <h3>Explorer la collection</h3>
            <p>
              Parcourez vos jeux par plateforme et retrouvez rapidement une entree grace aux vues de
              detail, aux filtres et a la recherche.
            </p>
          </article>
          <article>
            <h3>Suivre la liste des envies</h3>
            <p>
              Gardez une liste de souhaits separee pour preparer vos prochains ajouts et suivre les
              jeux qui vous interessent.
            </p>
          </article>
          <article>
            <h3>Piloter les mises a jour</h3>
            <p>
              Ajoutez, modifiez ou transferez des jeux avec les actions autorisees par votre profil
              et recuperez ensuite un fichier de collection coherent avec vos changements.
            </p>
          </article>
          <article>
            <h3>Afficher les statistiques</h3>
            <p>
              Consultez les indicateurs de collection pour garder une vision claire des plateformes,
              volumes et informations importantes.
            </p>
          </article>
          <article>
            <h3>Libre et open source</h3>
            <p>
              Profitez d'une application gratuite, libre et open source, pensee pour rester
              transparente et evoluer avec sa communaute.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}

export default AboutView;
