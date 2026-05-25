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
import AuthStatusMenu from "./AuthStatusMenu";

/**
 * Affiche le menu principal de navigation applicative.
 *
 * @param {Object} props - Etat d'authentification, plateformes et callbacks de navigation.
 * @returns {import("react").JSX.Element} Menu principal avec acces A propos, Ma collection et session.
 */
function MainMenu({
  isAuthenticated,
  username,
  profile,
  onOpenAbout,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenAdminDashboard,
  onLogout,
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
    callback();
  };

  return (
    <div className="pageHeaderTopActions">
      <div
        className={`pageHeaderOptionsMenu ${isOpen ? "isOpen" : ""}`}
        ref={menuRef}
        onPointerEnter={keepMenuOpen}
        onPointerLeave={closeMenuOnMouseLeave}
      >
        <button
          aria-expanded={isOpen}
          aria-haspopup="true"
          aria-label="Ouvrir le menu des options"
          className="pageHeaderOptionsTrigger"
          type="button"
          onClick={toggleMenu}
        >
          <svg aria-hidden="true" className="pageHeaderOptionsIcon" viewBox="0 0 24 24">
            <path d="M4 7h16v2H4V7Zm0 4h16v2H4v-2Zm0 4h16v2H4v-2Z" />
          </svg>
          <span>Menu</span>
        </button>
        <div className="pageHeaderActions" hidden={!isOpen}>
          <button
            className="secondaryButton"
            type="button"
            onClick={() => runMenuAction(onOpenAbout)}
          >
            A propos
          </button>
          <button
            className="secondaryButton"
            type="button"
            onClick={() => runMenuAction(onOpenHome)}
            disabled={!isAuthenticated}
          >
            Ma collection
          </button>
          <button
            className="secondaryButton"
            type="button"
            onClick={() => runMenuAction(onOpenLibrary)}
          >
            Bibliotheque
          </button>
          <button
            className="secondaryButton"
            type="button"
            onClick={() => runMenuAction(onOpenWishlist)}
            disabled={!isAuthenticated}
          >
            Liste de souhaits
          </button>
        </div>
      </div>
      {AuthStatusMenu.render({
        isAuthenticated,
        username,
        profile,
        onOpenAdminDashboard,
        onLogout,
      })}
    </div>
  );
}

export default MainMenu;
