/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : aides de saisie des champs configurables pendant l'import.
 */
import { useState } from "react";

const booleanAcceptedValues = Object.freeze([
  "Oui", "O", "Yes", "Y", "True", "Vrai", "1", "X", "✓", "Present", "Avec",
  "Non", "N", "No", "False", "Faux", "0", "Absent", "Sans",
]);

const IMPORT_FIELD_HELPS = Object.freeze({
  name: textHelp("Titre du jeu tel qu'il apparaît dans votre fichier."),
  platform: textHelp("Nom de la console ou de la plateforme du jeu."),
  studio: textHelp("Studio, éditeur ou développeur principal si vous le connaissez."),
  release_date: textHelp("Date de sortie, par exemple 1994, 1994-11-24 ou 24/11/1994."),
  wishlist: {
    description: "Valeur indiquant si la ligne appartient à votre liste de souhaits.",
    examples: ["Oui", "Non", "Yes", "No"],
    note: "Une cellule vide signifie Non.",
  },
  purchase_price: textHelp("Prix payé, sans devise. La devise est choisie une seule fois plus haut."),
  buy_location: textHelp("Boutique, site ou personne auprès de laquelle le jeu a été acheté."),
  buy_date: textHelp("Date d'achat, par exemple 2024-03-15 ou 15/03/2024."),
  grade: textHelp("Votre note personnelle. Une valeur comme 8, 8/10 ou 82/100 est acceptée."),
  condition: {
    description: "État physique du jeu. Les libellés proches sont rapprochés automatiquement.",
    examples: ["Mauvais", "Correct", "Bon", "Très bon", "Neuf"],
    note: "Les descriptions de contenu comme complet, loose ou CIB ne sont pas des états.",
  },
  has_manual: booleanFieldHelp("la présence de la notice"),
  is_collector: booleanFieldHelp("si l'exemplaire est une édition collector"),
  has_steelbook: booleanFieldHelp("si l'exemplaire contient un steelbook"),
  is_digital: booleanFieldHelp("si l'exemplaire est dématérialisé"),
  region: {
    description: "Région ou version.",
    examples: ["JAP", "US", "EU-FR", "PAL - UK"],
    acceptedValues: [
      "JAP", "US", "EU-FR", "EU-UK", "EU-DE", "EU-ES", "EU-IT", "AU", "ASIA",
      "KOR", "TWN", "HK", "CHN", "FR", "UK", "DE", "ES", "IT", "NTSC - US",
      "US - NTSC", "PAL - FR", "PAL - EUR", "EUR - PAL", "PAL - UK", "PAL - DE",
      "PAL - ES", "PAL - IT",
    ],
  },
  description: textHelp("Note libre sur votre exemplaire ou sa variante."),
});

/**
 * Affiche l'aide associee a un champ d'import.
 *
 * @param {Object} props - Propriétés du composant.
 * @param {string} props.fieldName - Nom technique du champ d'import.
 * @returns {import("react").JSX.Element} Aide visible et liste detaillee optionnelle.
 * @throws {void} Ne lève pas d'exception.
 */
function ImportFieldHelp({ fieldName }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const help = getImportFieldHelp(fieldName);

  return (
    <div className="fieldHelpText">
      <span>{formatShortHelp(help)}</span>
      {help.acceptedValues?.length ? (
        <>
          <button
            type="button"
            className="fieldHelpToggle"
            aria-expanded={isExpanded}
            onClick={() => setIsExpanded((currentValue) => !currentValue)}
          >
            {isExpanded ? "Masquer l'aide" : "Voir les valeurs acceptées"}
          </button>
          {isExpanded ? <span className="fieldHelpValues">{help.acceptedValues.join(", ")}</span> : null}
        </>
      ) : null}
    </div>
  );
}

/**
 * Construit une aide simple sans liste detaillee.
 *
 * @param {string} description - Description courte du champ.
 * @returns {Object} Aide structurée.
 * @throws {void} Ne lève pas d'exception.
 */
function textHelp(description) {
  return { description };
}

/**
 * Construit l'aide des colonnes booleennes importables.
 *
 * @param {string} subject - Sujet du champ booléen.
 * @returns {Object} Description, exemples et valeurs acceptées.
 * @throws {void} Ne lève pas d'exception.
 */
function booleanFieldHelp(subject) {
  return {
    description: `Indique ${subject}.`,
    examples: ["Oui", "Non", "True", "False"],
    acceptedValues: booleanAcceptedValues,
  };
}

/**
 * Retourne l'aide structuree associee a un champ d'import.
 *
 * @param {string} fieldName - Nom technique du champ d'import.
 * @returns {Object} Aide lisible du contenu attendu.
 * @throws {void} Ne leve pas d'exception.
 */
function getImportFieldHelp(fieldName) {
  return IMPORT_FIELD_HELPS[fieldName] || textHelp("Valeur optionnelle lue depuis votre fichier.");
}

/**
 * Formate le texte court affiche sous un champ d'import.
 *
 * @param {Object} help - Aide structurée.
 * @returns {string} Texte court avec exemples limités.
 * @throws {void} Ne lève pas d'exception.
 */
function formatShortHelp(help) {
  const parts = [help.description];
  if (help.examples?.length) {
    parts.push(`Exemples : ${help.examples.join(", ")}.`);
  }
  if (help.note) {
    parts.push(help.note);
  }
  return parts.join(" ");
}

export { formatShortHelp, getImportFieldHelp };
export default ImportFieldHelp;
