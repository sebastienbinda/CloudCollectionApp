/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : utilitaire objet de conversion des dates vers les champs HTML date.
 */

/**
 * Convertit les dates API vers le format attendu par `input[type=date]`.
 */
class DateInputFormatter {
  /**
   * Formate une date brute pour un champ HTML date.
   *
   * @param {unknown} value - Valeur date issue de l'API.
   * @returns {string} Date au format `YYYY-MM-DD`, ou chaine vide.
   */
  static format(value) {
    if (value === null || value === undefined || value === "") {
      return "";
    }

    const textValue = String(value).trim();
    const isoMatch = textValue.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (isoMatch) {
      return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}`;
    }

    const frenchMatch = textValue.match(/^(\d{1,2})[/. -](\d{1,2})[/. -](\d{2,4})$/);
    if (frenchMatch) {
      return this.formatFrenchDateMatch(frenchMatch);
    }

    return this.formatParsedDate(textValue);
  }

  /**
   * Convertit une date francaise capturee en date ISO.
   *
   * @param {RegExpMatchArray} match - Capture jour, mois et annee.
   * @returns {string} Date ISO compatible input date.
   */
  static formatFrenchDateMatch(match) {
    const year = match[3].length === 2 ? `20${match[3]}` : match[3];
    const month = match[2].padStart(2, "0");
    const day = match[1].padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  /**
   * Convertit une date reconnue par le navigateur en date ISO.
   *
   * @param {string} value - Texte date a parser.
   * @returns {string} Date ISO compatible input date, ou chaine vide.
   */
  static formatParsedDate(value) {
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return "";
    }
    return parsed.toISOString().slice(0, 10);
  }
}

export default DateInputFormatter;
