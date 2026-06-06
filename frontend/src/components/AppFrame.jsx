/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
import { Children } from "react";
import AppFooter from "./AppFooter";
import PageLayout from "./PageLayout";

/**
 * Encapsule une vue en conservant le footer pour les pages non migrees.
 *
 * @param {{children: import("react").ReactNode}} props - Contenu de la vue courante.
 * @returns {import("react").JSX.Element} Vue complete avec footer transitoire si necessaire.
 */
function AppFrame({ children }) {
  const childElements = Children.toArray(children);
  const hasPageLayout = childElements.some((child) => child?.type === PageLayout);

  return (
    <>
      {children}
      {hasPageLayout ? null : <AppFooter />}
    </>
  );
}

export default AppFrame;
