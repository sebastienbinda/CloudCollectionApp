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
 * Description : grille reutilisable pour les cartes de contenu.
 */

/**
 * Affiche une grille reutilisable de cartes.
 *
 * @param {Object} props - Proprietes React de la grille.
 * @param {import("react").ReactNode} props.children - Cartes affichees dans la grille.
 * @param {string} [props.className] - Classes CSS additionnelles.
 * @param {string} [props.ariaLabel] - Libelle accessible de la grille.
 * @returns {import("react").JSX.Element} Grille de cartes.
 */
function GridComponent({ children, className = "", ariaLabel }) {
  const classes = ["platformGrid", className].filter(Boolean).join(" ");

  return (
    <div className={classes} aria-label={ariaLabel}>
      {children}
    </div>
  );
}

export default GridComponent;
