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
 * Description : compteur reutilisable pour les cartes de contenu.
 */

/**
 * Affiche un compteur dans une carte reutilisable.
 *
 * @param {Object} props - Proprietes React du compteur.
 * @param {import("react").ReactNode} props.children - Valeur et libelle du compteur.
 * @param {string} [props.className] - Classes CSS additionnelles.
 * @returns {import("react").JSX.Element} Compteur de carte.
 */
function CardCountComponent({ children, className = "" }) {
  const classes = ["platformGameCount", className].filter(Boolean).join(" ");

  return <p className={classes}>{children}</p>;
}

export default CardCountComponent;
