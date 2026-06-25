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
import { useEffect, useState } from "react";
import AppFooter from "./AppFooter";
import MainMenu from "./MainMenu";
import ProjectIcon from "./ProjectIcon";

const SCROLL_TOP_VISIBILITY_THRESHOLD = 520;

/**
 * Deduit l'entree de menu active depuis l'URL courante.
 *
 * @returns {string} Cle de navigation active.
 */
function resolveActiveNavigationKeyFromLocation() {
  if (typeof window === "undefined") {
    return "";
  }
  const pathname = window.location.pathname;
  if (pathname === "/auth" || pathname === "/auth/verify-email") {
    return "login";
  }
  if (pathname === "/about") {
    return "about";
  }
  if (
    pathname === "/configuration" ||
    pathname === "/configuration/images-plateformes" ||
    pathname === "/users"
  ) {
    return "configuration";
  }
  if (pathname === "/wishlist") {
    return "wishlist";
  }
  if (pathname.startsWith("/bibliotheque")) {
    return "library";
  }
  return "collection";
}

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
 * @param {import("react").ReactNode} props.headerLeadingContent - Contenu affiche au debut du header.
 * @param {import("react").ReactNode} props.titleContent - Contenu personnalise du titre.
 * @param {import("react").ReactNode} props.headerExtraContent - Contenu additionnel du header.
 * @param {import("react").ReactNode} props.headerAsideContent - Contenu lateral du header.
 * @param {boolean} props.isAuthenticated - Indique si une session locale est active.
 * @param {boolean} props.canUseCollectionViews - Indique si les vues collection sont accessibles.
 * @param {string} props.authenticatedUsername - Identifiant affiche pour l'utilisateur connecte.
 * @param {string} props.authenticatedProfile - Profil de l'utilisateur connecte.
 * @param {Function} props.onOpenAbout - Callback ouvrant la page A propos.
 * @param {Function} props.onOpenAuth - Callback ouvrant la page Connexion.
 * @param {Function} props.onOpenHome - Callback ouvrant Ma collection.
 * @param {Function} props.onOpenLibrary - Callback ouvrant la Bibliotheque.
 * @param {Function} props.onOpenWishlist - Callback ouvrant la liste de souhaits.
 * @param {Function} props.onOpenConfiguration - Callback ouvrant la page Configuration.
 * @param {Function} props.onLogout - Callback de deconnexion.
 * @param {string} props.activeNavigationKey - Cle de l'entree de menu active.
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
  headerAsideContent = null,
  isAuthenticated,
  canUseCollectionViews = true,
  canViewCollection = canUseCollectionViews,
  canViewWishlist = canUseCollectionViews,
  canAccessConfiguration = true,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  activeNavigationKey = "",
}) {
  const [isScrollTopVisible, setIsScrollTopVisible] = useState(false);
  const resolvedActiveNavigationKey = (
    activeNavigationKey || resolveActiveNavigationKeyFromLocation()
  );
  const renderedTitleContent = titleContent || (
    <span className="pageTitleWithIcon">
      <ProjectIcon />
      <span>{title}</span>
    </span>
  );

  useEffect(() => {
    /**
     * Met a jour la visibilite du bouton de retour en haut.
     *
     * @returns {void} Met a jour l'etat local selon la position de defilement.
     */
    const updateScrollTopVisibility = () => {
      setIsScrollTopVisible(window.scrollY > SCROLL_TOP_VISIBILITY_THRESHOLD);
    };

    updateScrollTopVisibility();
    window.addEventListener("scroll", updateScrollTopVisibility, { passive: true });
    window.addEventListener("resize", updateScrollTopVisibility);

    return () => {
      window.removeEventListener("scroll", updateScrollTopVisibility);
      window.removeEventListener("resize", updateScrollTopVisibility);
    };
  }, []);

  /**
   * Ramene l'utilisateur en haut de la page.
   *
   * @returns {void} Lance un defilement fluide vers le debut du document.
   */
  const scrollToPageTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <>
      <main className={shellClassName}>
        <header className={headerClassName}>
          {headerLeadingContent}
          <div className={headerContentClassName || undefined}>
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            {title || titleContent ? <h1>{renderedTitleContent}</h1> : null}
            {headerExtraContent}
            {subtitle ? <p className="subtitle">{subtitle}</p> : null}
          </div>
          {headerAsideContent}
        </header>
        <MainMenu
          isAuthenticated={isAuthenticated}
          canUseCollectionViews={canUseCollectionViews}
          canViewCollection={canViewCollection}
          canViewWishlist={canViewWishlist}
          canAccessConfiguration={canAccessConfiguration}
          username={authenticatedUsername}
          profile={authenticatedProfile}
          onOpenAbout={onOpenAbout}
          onOpenAuth={onOpenAuth}
          onOpenHome={onOpenHome}
          onOpenLibrary={onOpenLibrary}
          onOpenWishlist={onOpenWishlist}
          onOpenConfiguration={onOpenConfiguration}
          onLogout={onLogout}
          activeNavigationKey={resolvedActiveNavigationKey}
        />
        {children}
      </main>
      {isScrollTopVisible ? (
        <button
          className="scrollTopButton"
          type="button"
          aria-label="Revenir en haut de la page"
          title="Revenir en haut"
          onClick={scrollToPageTop}
        >
          ↑
        </button>
      ) : null}
      <AppFooter />
    </>
  );
}

export default PageLayout;
