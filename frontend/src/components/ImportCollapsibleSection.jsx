/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-18
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : section repliable reutilisable du formulaire d'import.
 */

/**
 * Affiche une section repliable de formulaire d'import.
 *
 * @param {Object} props - Propriétés de la section.
 * @param {string} props.title - Titre visible de la section.
 * @param {string} props.description - Résumé court de la section.
 * @param {boolean} props.defaultOpen - Indique si la section est ouverte par défaut.
 * @param {import("react").ReactNode} props.children - Contenu de la section.
 * @returns {import("react").JSX.Element} Section repliable.
 * @throws {void} Ne lève pas d'exception.
 */
function ImportCollapsibleSection({ title, description, defaultOpen = true, children }) {
  return (
    <details className="importCollapsibleSection" open={defaultOpen}>
      <summary>
        <span>{title}</span>
        <small>{description}</small>
      </summary>
      <div className="importCollapsibleContent">{children}</div>
    </details>
  );
}

export default ImportCollapsibleSection;
