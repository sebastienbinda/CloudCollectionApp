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
import {
  ArrowRight,
  Code2,
  HeartHandshake,
  LockKeyhole,
  Search,
  Share2,
  Smartphone,
  UploadCloud,
} from "lucide-react";
import PageLayout from "./PageLayout";

/**
 * Presente les fonctionnalites de l'application aux visiteurs non connectes.
 *
 * @param {Object} props - Etat de session et callbacks de navigation du menu.
 * @returns {import("react").JSX.Element} Page About publique.
 */
function AboutView({
  error,
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
}) {
  return (
    <PageLayout
      shellClassName="appShell aboutShell"
      headerClassName="pageHeader aboutHeader"
      headerContentClassName="aboutHeaderContent"
      headerLeadingContent={(
        <img
          className="aboutHeaderImage"
          src="/about-home-image.jpg?v=ods-home-20260520"
          alt="Apercu visuel de la collection de jeux video"
        />
      )}
      eyebrow="CloudCollectionApp"
      title="Votre collection de jeux, toujours sous la main"
      subtitle={
        "Importez votre fichier, consultez vos jeux partout, gardez vos donnees privees et partagez seulement ce que vous choisissez."
      }
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
      {error ? <p className="error" role="alert">{error}</p> : null}
      <section className="aboutContent" aria-label="Fonctionnalites de l'application">
        <div className="aboutIntro aboutLead">
          <h2>Un espace simple pour ne plus perdre le fil</h2>
          <p>
            CloudCollectionApp transforme votre fichier de collection en espace personnel en ligne.
            Vous retrouvez rapidement ce que vous possedez, ce que vous cherchez encore et les
            informations utiles quand vous etes chez vous, en boutique ou en salon.
          </p>
        </div>

        <div className="aboutFeatureGrid">
          <article className="aboutFeatureCard aboutFeatureCardBlue">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <Smartphone size={24} strokeWidth={2.2} />
            </span>
            <h3>Disponible partout</h3>
            <p>
              Votre collection vous suit sur ordinateur, tablette ou mobile. Plus besoin d'avoir
              le bon fichier sous la main pour verifier un jeu ou une plateforme.
            </p>
          </article>
          <article className="aboutFeatureCard aboutFeatureCardGreen">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <UploadCloud size={24} strokeWidth={2.2} />
            </span>
            <h3>Import rapide</h3>
            <p>
              Repartez de votre tableur existant, importez-le, puis ajoutez de nouveaux fichiers
              quand votre collection evolue.
            </p>
          </article>
          <article className="aboutFeatureCard aboutFeatureCardAmber">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <Search size={24} strokeWidth={2.2} />
            </span>
            <h3>Recherche claire</h3>
            <p>
              Retrouvez vos jeux par plateforme, consultez les details importants et gardez une
              liste d'envies separee de votre collection.
            </p>
          </article>
          <article className="aboutFeatureCard aboutFeatureCardRose">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <LockKeyhole size={24} strokeWidth={2.2} />
            </span>
            <h3>Collection privee</h3>
            <p>
              Vos jeux restent rattaches a votre compte. Vous pouvez garder votre collection pour
              vous ou partager un acces controle quand vous le decidez.
            </p>
          </article>
          <article className="aboutFeatureCard aboutFeatureCardTeal">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <HeartHandshake size={24} strokeWidth={2.2} />
            </span>
            <h3>Esprit communautaire</h3>
            <p>
              Le catalogue commun des jeux, plateformes et studios s'ameliore avec les imports et
              les validations, au benefice de tous les collectionneurs.
            </p>
          </article>
          <article className="aboutFeatureCard aboutFeatureCardViolet">
            <span className="aboutFeatureIcon" aria-hidden="true">
              <Code2 size={24} strokeWidth={2.2} />
            </span>
            <h3>Open source</h3>
            <p>
              Le projet est libre et transparent. Il peut evoluer avec les besoins reels des
              utilisateurs, sans enfermer votre collection dans une boite noire.
            </p>
          </article>
        </div>

        <div className="aboutBetaNotice">
          <h2>Application en evolution</h2>
          <p>
            L'application est encore en cours de travail. Des fonctionnalites peuvent evoluer, et
            les retours des utilisateurs aident a prioriser les prochaines ameliorations.
          </p>
          <button type="button" className="aboutSecondaryAction" onClick={onOpenFeedback}>
            Envoyer une remarque
            <ArrowRight size={18} strokeWidth={2.3} aria-hidden="true" />
          </button>
        </div>

        <div className="aboutCallout">
          <span className="aboutCalloutIcon" aria-hidden="true">
            <Share2 size={26} strokeWidth={2.1} />
          </span>
          <h2>Pour commencer</h2>
          <p>
            Creez un compte, importez votre fichier, puis consultez votre collection en ligne. Vos
            donnees restent privees par defaut, votre espace connecte garde vos parametres a jour
            et les fonctions de partage restent sous votre controle.
          </p>
          {!isAuthenticated ? (
            <button type="button" className="aboutPrimaryAction" onClick={onOpenAuth}>
              Se connecter ou creer un compte
              <ArrowRight size={18} strokeWidth={2.3} aria-hidden="true" />
            </button>
          ) : null}
        </div>
      </section>
    </PageLayout>
  );
}

export default AboutView;
