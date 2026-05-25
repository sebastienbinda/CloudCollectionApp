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
 * Description : en-tete reutilisable pour les cartes de contenu.
 */

/**
 * Affiche l'en-tete d'une carte reutilisable.
 *
 * @param {Object} props - Proprietes React de l'en-tete.
 * @param {import("react").ReactNode} props.children - Contenu de l'en-tete.
 * @param {string} [props.className] - Classes CSS additionnelles.
 * @returns {import("react").JSX.Element} En-tete de carte.
 */
function CardHeaderComponent({ children, className = "" }) {
  const classes = ["platformCardHeader", className].filter(Boolean).join(" ");

  return <div className={classes}>{children}</div>;
}

export default CardHeaderComponent;
