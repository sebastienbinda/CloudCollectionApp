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
 * Description : carte reutilisable pour les listes de contenus.
 */

/**
 * Affiche une carte interactive reutilisable.
 *
 * @param {Object} props - Proprietes React de la carte.
 * @param {import("react").ReactNode} props.children - Contenu affiche dans la carte.
 * @param {string} [props.className] - Classes CSS additionnelles.
 * @param {Function} [props.onClick] - Callback appele au clic.
 * @param {Object} [props.style] - Styles inline optionnels.
 * @param {string} [props.type] - Type du bouton lorsque la carte est interactive.
 * @returns {import("react").JSX.Element} Carte interactive.
 */
function CardComponent({ children, className = "", onClick, style, type = "button" }) {
  const classes = ["platformCard", className].filter(Boolean).join(" ");

  return (
    <button type={type} className={classes} onClick={onClick} style={style}>
      {children}
    </button>
  );
}

export default CardComponent;
