/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-06
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : layout React commun pour les pages applicatives.
 */
import AppFooter from "./AppFooter";
import MainMenu from "./MainMenu";
import ProjectIcon from "./ProjectIcon";

/**
 * Structure une page avec header, menu principal, contenu et footer.
 *
 * @param {Object} props - Informations de page, session et callbacks de navigation.
 * @param {import("react").ReactNode} props.children - Contenu principal de la page.
 * @param {string} props.eyebrow - Libelle court affiche au-dessus du titre.
 * @param {string|import("react").ReactNode} props.title - Titre principal de la page.
 * @param {string|import("react").ReactNode} props.subtitle - Sous-titre affiche sous le titre.
 * @param {string} props.shellClassName - Classes CSS appliquees au conteneur principal.
 * @param {string} props.headerClassName - Classes CSS appliquees au header.
 * @param {string} props.headerContentClassName - Classes CSS appliquees au bloc de titre.
 * @param {import("react").ReactNode} props.headerLeadingContent - Contenu affiche avant le menu.
 * @param {import("react").ReactNode} props.titleContent - Contenu personnalise du titre.
 * @param {import("react").ReactNode} props.headerExtraContent - Contenu additionnel du header.
 * @param {boolean} props.isAuthenticated - Indique si une session locale est active.
 * @param {boolean} props.canUseCollectionViews - Indique si les vues collection sont accessibles.
 * @param {string} props.authenticatedUsername - Identifiant affiche pour l'utilisateur connecte.
 * @param {string} props.authenticatedProfile - Profil de l'utilisateur connecte.
 * @param {Function} props.onOpenAbout - Callback ouvrant la page A propos.
 * @param {Function} props.onOpenAuth - Callback ouvrant la page Connexion.
 * @param {Function} props.onOpenHome - Callback ouvrant Ma collection.
 * @param {Function} props.onOpenLibrary - Callback ouvrant la Bibliotheque.
 * @param {Function} props.onOpenAdminDashboard - Callback ouvrant le dashboard admin.
 * @param {Function} props.onLogout - Callback de deconnexion.
 * @returns {import("react").JSX.Element} Page complete avec layout commun.
 */
function PageLayout({
  children,
  eyebrow,
  title,
  subtitle,
  shellClassName = "appShell",
  headerClassName = "pageHeader",
  headerContentClassName = "",
  headerLeadingContent = null,
  titleContent = null,
  headerExtraContent = null,
  isAuthenticated,
  canUseCollectionViews = true,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenAdminDashboard,
  onLogout,
}) {
  const renderedTitleContent = titleContent || (
    <span className="pageTitleWithIcon">
      <ProjectIcon />
      <span>{title}</span>
    </span>
  );

  return (
    <>
      <main className={shellClassName}>
        <header className={headerClassName}>
          {headerLeadingContent}
          <MainMenu
            isAuthenticated={isAuthenticated}
            canUseCollectionViews={canUseCollectionViews}
            username={authenticatedUsername}
            profile={authenticatedProfile}
            onOpenAbout={onOpenAbout}
            onOpenAuth={onOpenAuth}
            onOpenHome={onOpenHome}
            onOpenLibrary={onOpenLibrary}
            onOpenAdminDashboard={onOpenAdminDashboard}
            onLogout={onLogout}
          />
          <div className={headerContentClassName || undefined}>
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            {title || titleContent ? <h1>{renderedTitleContent}</h1> : null}
            {headerExtraContent}
            {subtitle ? <p className="subtitle">{subtitle}</p> : null}
          </div>
        </header>
        {children}
      </main>
      <AppFooter />
    </>
  );
}

export default PageLayout;
