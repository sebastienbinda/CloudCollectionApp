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
 * Description : menu principal React partage par les pages A propos et Ma collection.
 */
import { useEffect, useRef, useState } from "react";
import resolveMainMenuAccess from "../services/MainMenuAccessPolicy";

const MENU_ICON_PATHS = {
  about: (
    <>
      <path d="M12 17h.01" />
      <path d="M12 13a3 3 0 1 0-3-3" />
      <path d="M4 19.5a8 8 0 1 1 16 0" />
    </>
  ),
  library: (
    <>
      <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5V5.5Z" />
      <path d="M4 5.5v15" />
      <path d="M8 7h8" />
      <path d="M8 10h6" />
    </>
  ),
  configuration: (
    <>
      <path d="M12 8.5a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7Z" />
      <path d="M19.4 15a8 8 0 0 0 .1-2l2-1.2-2-3.4-2.3.9a7.6 7.6 0 0 0-1.7-1L15.2 6h-4l-.3 2.3a7.6 7.6 0 0 0-1.7 1l-2.3-.9-2 3.4 2 1.2a8 8 0 0 0 .1 2l-2 1.2 2 3.4 2.3-.9a7.6 7.6 0 0 0 1.7 1l.3 2.3h4l.3-2.3a7.6 7.6 0 0 0 1.7-1l2.3.9 2-3.4-2.2-1.2Z" />
    </>
  ),
  wishlist: (
    <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z" />
  ),
  statistics: (
    <>
      <path d="M4 19V5" />
      <path d="M4 19h16" />
      <path d="M8 16V9" />
      <path d="M12 16V6" />
      <path d="M16 16v-4" />
    </>
  ),
  collection: (
    <>
      <path d="M4 7h16v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z" />
      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M8 11h3" />
      <path d="M13 11h3" />
      <path d="M8 15h8" />
    </>
  ),
  login: (
    <>
      <path d="M10 17l5-5-5-5" />
      <path d="M15 12H3" />
      <path d="M21 4v16" />
    </>
  ),
  logout: (
    <>
      <path d="M14 17l5-5-5-5" />
      <path d="M19 12H7" />
      <path d="M5 4v16" />
    </>
  ),
  more: (
    <>
      <path d="M5 12h.01" />
      <path d="M12 12h.01" />
      <path d="M19 12h.01" />
    </>
  ),
};

const renderMenuIcon = (iconName) => (
  <svg className="mainNavigationIconGraphic" aria-hidden="true" viewBox="0 0 24 24">
    {MENU_ICON_PATHS[iconName] || MENU_ICON_PATHS.more}
  </svg>
);

/**
 * Affiche le menu principal de navigation applicative.
 *
 * @param {Object} props - Etat d'authentification, plateformes et callbacks de navigation.
 * @param {number} props.libraryValidationBadgeCount - Nombre de jeux en attente a signaler.
 * @returns {import("react").JSX.Element} Menu principal avec acces A propos, Ma collection et session.
 */
function MainMenu({
  isAuthenticated,
  canUseCollectionViews = true,
  canViewCollection = canUseCollectionViews,
  canViewWishlist = canUseCollectionViews,
  canViewStatistics = canViewCollection,
  canAccessConfiguration = true,
  username,
  profile,
  libraryValidationBadgeCount = 0,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenStatistics,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  activeNavigationKey = "",
}) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const closeMenuTimeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (closeMenuTimeoutRef.current) {
        window.clearTimeout(closeMenuTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const closeMenuOnOutsidePointer = (event) => {
      if (!menuRef.current || menuRef.current.contains(event.target)) {
        return;
      }
      setIsOpen(false);
    };

    const closeMenuOnEscape = (event) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("pointerdown", closeMenuOnOutsidePointer);
    document.addEventListener("keydown", closeMenuOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeMenuOnOutsidePointer);
      document.removeEventListener("keydown", closeMenuOnEscape);
    };
  }, [isOpen]);

  const closeMenu = () => {
    if (closeMenuTimeoutRef.current) {
      window.clearTimeout(closeMenuTimeoutRef.current);
      closeMenuTimeoutRef.current = null;
    }
    setIsOpen(false);
  };

  const toggleMenu = () => {
    setIsOpen((previous) => !previous);
  };

  const keepMenuOpen = () => {
    if (!closeMenuTimeoutRef.current) {
      return;
    }
    window.clearTimeout(closeMenuTimeoutRef.current);
    closeMenuTimeoutRef.current = null;
  };

  const closeMenuOnMouseLeave = (event) => {
    if (event.pointerType && event.pointerType !== "mouse") {
      return;
    }
    closeMenuTimeoutRef.current = window.setTimeout(closeMenu, 180);
  };

  const runMenuAction = (callback) => {
    closeMenu();
    if (typeof callback === "function") {
      callback();
    }
  };

  const normalizedProfile = String(profile || "").trim().toUpperCase();
  const normalizedLibraryValidationBadgeCount = Math.max(
    0,
    Number.parseInt(libraryValidationBadgeCount, 10) || 0
  );
  const { canOpenConfiguration, canOpenWishlist, canOpenHome, canOpenStatistics } = resolveMainMenuAccess({
    isAuthenticated,
    canAccessConfiguration,
    canViewWishlist,
    canViewCollection,
    canViewStatistics,
    onOpenConfiguration,
    onOpenWishlist,
    onOpenHome,
    onOpenStatistics,
  });
  const aboutItem = {
    key: "about",
    label: "A propos",
    shortLabel: "A propos",
    icon: "about",
    disabled: false,
    action: onOpenAbout,
  };
  const libraryItem = {
    key: "library",
    label: "Bibliotheque",
    shortLabel: "Biblio",
    icon: "library",
    badgeCount: normalizedLibraryValidationBadgeCount,
    disabled: typeof onOpenLibrary !== "function",
    action: onOpenLibrary,
  };
  const configurationItem = {
    key: "configuration",
    label: "Configuration",
    shortLabel: "Config",
    icon: "configuration",
    disabled: !canOpenConfiguration,
    action: onOpenConfiguration,
  };
  const wishlistItem = {
    key: "wishlist",
    label: "Liste de souhaits",
    shortLabel: "Souhaits",
    icon: "wishlist",
    disabled: !canOpenWishlist,
    action: onOpenWishlist,
  };
  const collectionItem = {
    key: "collection",
    label: "Ma collection",
    shortLabel: "Collection",
    icon: "collection",
    disabled: !canOpenHome,
    action: onOpenHome,
  };
  const statisticsItem = {
    key: "statistics",
    label: "Statistiques",
    shortLabel: "Stats",
    icon: "statistics",
    disabled: !canOpenStatistics,
    action: onOpenStatistics,
  };
  const anonymousNavigationItems = [
    aboutItem,
    libraryItem,
  ];
  const authenticatedNavigationItems = [
    canOpenHome ? collectionItem : null,
    canOpenWishlist ? wishlistItem : null,
    canOpenStatistics ? statisticsItem : null,
    libraryItem,
    canOpenConfiguration ? configurationItem : null,
    aboutItem,
  ].filter(Boolean);
  const navigationItems = isAuthenticated ? authenticatedNavigationItems : anonymousNavigationItems;
  const mobileAuthenticatedPrimaryItems = [
    canOpenHome ? collectionItem : null,
    canOpenWishlist ? wishlistItem : null,
    canOpenStatistics ? statisticsItem : null,
    libraryItem,
  ].filter(Boolean);
  const mobileAnonymousPrimaryItems = [
    libraryItem,
    null,
    aboutItem,
  ];
  const mobileAuthenticatedSecondaryItems = [
    canOpenConfiguration ? configurationItem : null,
    aboutItem,
    null,
  ];
  const mobileAnonymousSecondaryItems = [];
  const sessionItem = isAuthenticated
    ? {
        key: "logout",
        label: "Deconnexion",
        shortLabel: "Deconnexion",
        icon: "logout",
        disabled: typeof onLogout !== "function",
        action: onLogout,
      }
    : {
        key: "login",
        label: "Connexion",
        shortLabel: "Connexion",
        icon: "login",
        disabled: typeof onOpenAuth !== "function",
        action: onOpenAuth,
      };
  mobileAnonymousPrimaryItems[1] = sessionItem;
  mobileAuthenticatedSecondaryItems[2] = sessionItem;
  const mobilePrimaryItems = (
    isAuthenticated ? mobileAuthenticatedPrimaryItems : mobileAnonymousPrimaryItems
  ).filter(Boolean);
  const mobileSecondaryItems = (
    isAuthenticated ? mobileAuthenticatedSecondaryItems : mobileAnonymousSecondaryItems
  ).filter(Boolean);
  const isMobileSecondaryItemActive = mobileSecondaryItems.some(
    (item) => item.key === activeNavigationKey
  );

  const renderNavigationButton = (item, className = "mainNavigationItem") => {
    const isActive = item.key === activeNavigationKey;
    return (
      <button
        aria-current={isActive ? "page" : undefined}
        className={`${className}${isActive ? " isActiveNavigationItem" : ""}`}
        type="button"
        onClick={() => runMenuAction(item.action)}
        disabled={item.disabled}
        key={item.key}
      >
        <span className="mainNavigationIcon" aria-hidden="true">{renderMenuIcon(item.icon)}</span>
        <span className="mainNavigationLabel">{item.label}</span>
        <span className="mainNavigationShortLabel">{item.shortLabel}</span>
        {item.badgeCount > 0 ? (
          <span
            className="mainNavigationBadge"
            aria-label={`${item.badgeCount} jeux en attente de validation`}
            title={`${item.badgeCount} jeux en attente de validation`}
          >
            {item.badgeCount > 99 ? "99+" : item.badgeCount}
          </span>
        ) : null}
      </button>
    );
  };

  return (
    <div className="appNavigationBar">
      {isAuthenticated ? (
        <p className={`mobileSessionIdentity mobileSessionIdentity${normalizedProfile}`}>
          {normalizedProfile === "GUEST"
            ? username || "Invité"
            : `Utilisateur connecté : ${username || "utilisateur"}`}
        </p>
      ) : null}
      <nav className="desktopNavigation" aria-label="Navigation principale">
        {navigationItems.map((item) => renderNavigationButton(item))}
      </nav>
      <nav
        className={`mobileDockNavigation ${
          mobileSecondaryItems.length > 0 ? "" : "mobileDockNavigationCompact"
        }`}
        aria-label="Navigation mobile principale"
        style={{
          gridTemplateColumns: `repeat(${mobilePrimaryItems.length + (mobileSecondaryItems.length > 0 ? 1 : 0)}, minmax(0, 1fr))`,
        }}
      >
        {mobilePrimaryItems.map((item) => renderNavigationButton(item, "mobileDockItem"))}
        {mobileSecondaryItems.length > 0 ? (
          <div
            className={`pageHeaderOptionsMenu mobileDockMore ${isOpen ? "isOpen" : ""}`}
            ref={menuRef}
            onPointerEnter={keepMenuOpen}
            onPointerLeave={closeMenuOnMouseLeave}
          >
            <button
              aria-expanded={isOpen}
              aria-haspopup="true"
              aria-label="Ouvrir les autres actions"
              className={`mobileDockItem mobileDockMoreTrigger${
                isMobileSecondaryItemActive ? " isActiveNavigationItem" : ""
              }`}
              type="button"
              onClick={toggleMenu}
            >
              <span className="mainNavigationIcon" aria-hidden="true">{renderMenuIcon("more")}</span>
              <span className="mainNavigationLabel">Plus</span>
              <span className="mainNavigationShortLabel">Plus</span>
            </button>
            <div className="pageHeaderActions" hidden={!isOpen}>
              {mobileSecondaryItems.map((item) => renderNavigationButton(item, "mobileNavigationItem"))}
            </div>
          </div>
        ) : null}
      </nav>
      <div className="desktopSessionActions">
        {isAuthenticated ? (
          <p className={`pageHeaderConnectedUser pageHeaderConnectedUser${normalizedProfile}`}>
            {normalizedProfile === "GUEST"
              ? username || "Invité"
              : `Utilisateur connecté : ${username || "utilisateur"}`}
          </p>
        ) : null}
        {renderNavigationButton(sessionItem, "mainNavigationItem sessionNavigationItem")}
      </div>
    </div>
  );
}

export default MainMenu;
