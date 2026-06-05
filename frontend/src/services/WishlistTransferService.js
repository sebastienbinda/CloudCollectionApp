/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-04
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : service objet pour la promotion des jeux wishlist vers leur plateforme.
 */

/**
 * Centralise les regles de transfert d'un jeu wishlist vers un onglet plateforme.
 */
class WishlistTransferService {
  /**
   * Indique si une valeur de jeu est renseignee.
   *
   * @param {unknown} value - Valeur brute a tester.
   * @returns {boolean} `true` si la valeur contient du texte.
   */
  hasTextValue(value) {
    return String(value || "").trim() !== "";
  }

  /**
   * Indique si un jeu de la wishlist a deja une date d'achat.
   *
   * @param {Record<string, unknown>} game - Jeu de la liste de souhaits.
   * @returns {boolean} `true` si une date d'achat est renseignee.
   */
  hasPurchaseDate(game) {
    return this.hasTextValue(game["Date d'achat"]);
  }

  /**
   * Trouve la plateforme existante correspondant a la console wishlist.
   *
   * @param {Record<string, unknown>} game - Jeu de la wishlist.
   * @param {string[]} platforms - Plateformes existantes chargees depuis l'API.
   * @returns {string} Nom exact de plateforme existante, ou chaine vide.
   */
  findTargetPlatform(game, platforms) {
    const consoleName = String(game.Console || game.Plateforme || "").trim();
    const normalizedConsole = consoleName.toLowerCase();

    return (
      (platforms || []).find(
        (platform) => String(platform).trim().toLowerCase() === normalizedConsole
      ) || ""
    );
  }

  /**
   * Formate une date pour un champ `input[type=date]`.
   *
   * @param {unknown} value - Date brute issue du fichier ODS.
   * @returns {string} Date au format `YYYY-MM-DD`, ou chaine vide.
   */
  formatDateInputValue(value) {
    if (!this.hasTextValue(value)) {
      return "";
    }

    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return String(value);
    }

    return parsed.toISOString().slice(0, 10);
  }

  /**
   * Retourne le debut de la journee courante.
   *
   * @param {void} Aucun - Utilise la date locale du navigateur.
   * @returns {Date} Date du jour a minuit.
   */
  getTodayStart() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }

  /**
   * Parse une date de sortie exploitable pour la comparaison.
   *
   * @param {unknown} value - Valeur brute de la colonne `Date de sortie`.
   * @returns {Date|null} Date parsee, ou `null` si la valeur est invalide.
   */
  parseReleaseDate(value) {
    if (!this.hasTextValue(value)) {
      return null;
    }

    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  /**
   * Trouve le prochain jeu a sortir dans la wishlist.
   *
   * @param {Record<string, unknown>[]} games - Jeux de la liste de souhaits.
   * @returns {{game: Record<string, unknown>, releaseDate: Date}|null} Prochaine sortie future.
   */
  getNextWishlistRelease(games) {
    const todayStart = this.getTodayStart();

    return games.reduce((nextRelease, game) => {
      const releaseDate = this.parseReleaseDate(game["Date de sortie"]);
      if (!releaseDate || releaseDate <= todayStart) {
        return nextRelease;
      }

      if (!nextRelease || releaseDate < nextRelease.releaseDate) {
        return { game, releaseDate };
      }

      return nextRelease;
    }, null);
  }

  /**
   * Calcule le nombre de jours avant une date de sortie.
   *
   * @param {Date} releaseDate - Date de sortie future.
   * @returns {number} Nombre de jours restants avant la sortie.
   */
  getDaysUntilRelease(releaseDate) {
    const millisecondsPerDay = 24 * 60 * 60 * 1000;
    return Math.ceil((releaseDate.getTime() - this.getTodayStart().getTime()) / millisecondsPerDay);
  }

  /**
   * Construit le payload d'ajout depuis un jeu wishlist.
   *
   * @param {Record<string, unknown>} game - Jeu wishlist source.
   * @param {string} platform - Plateforme cible existante.
   * @param {Record<string, string>} transferForm - Champs saisis dans la confirmation.
   * @returns {Record<string, unknown>} Donnees compatibles avec l'endpoint d'ajout.
   */
  buildTransferPayload(game, platform, transferForm) {
    return {
      platform,
      "Nom du jeu": game["Nom du jeu"] || "",
      Studio: game.Studio || "",
      "Date de sortie": game["Date de sortie"] || "",
      "Date d'achat": transferForm["Date d'achat"],
      "Lieu d'achat": transferForm["Lieu d'achat"],
      Note: game.Note || "",
      "Prix d'achat": game["Prix d'achat"] || "",
      Version: game.Version || "",
    };
  }
}

export default WishlistTransferService;
