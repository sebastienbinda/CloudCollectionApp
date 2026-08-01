/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-22
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : service de formatage centralise des colonnes de tableaux frontend.
 */
import { formatCellValue, formatMonthYearValue, isDateColumn } from "../collectionUtils";

const profileLabels = {
  ADMIN: "Administrateur",
  USER: "Utilisateur",
};

const statusLabels = {
  ACCEPTED: "Accepte",
  ACTIVE: "Actif",
  WAITING_VALIDATION: "En attente de validation",
  LOCKED: "Bloque",
};

const regionFlags = {
  JAP: "🇯🇵",
  US: "🇺🇸",
  "EU-FR": "🇫🇷",
  "EU-UK": "🇬🇧",
  "EU-DE": "🇩🇪",
  "EU-ES": "🇪🇸",
  "EU-IT": "🇮🇹",
  AU: "🇦🇺",
  ASIA: "🌏",
  KOR: "🇰🇷",
  TWN: "🇹🇼",
  HK: "🇭🇰",
  CHN: "🇨🇳",
};

/**
 * Centralise le formatage des valeurs affichees dans les tableaux.
 */
class TableColumnFormatService {
  /**
   * Formate une valeur de tableau de jeux.
   *
   * @param {string} column - Nom de colonne a formater.
   * @param {unknown} value - Valeur brute de cellule.
   * @param {Object|null} row - Ligne complete contenant les informations associees.
   * @returns {string|import("react").JSX.Element} Valeur prete a afficher.
   */
  static formatGameValue(column, value, row = null) {
    if (column === "Version") {
      return this.formatVersionValue(value);
    }

    if (column === "status") {
      return statusLabels[String(value || "").toUpperCase()] || formatCellValue(column, value);
    }

    if (column === "Prix d'achat") {
      if (this.isEmpty(value)) {
        return "-";
      }
      const priceUnit = String(row?.priceUnit || "").trim();
      const numericValue = Number.parseFloat(String(value).replace(",", "."));
      if (!priceUnit || Number.isNaN(numericValue)) {
        return String(value);
      }
      return new Intl.NumberFormat("fr-FR", {
        style: "currency",
        currency: priceUnit,
        maximumFractionDigits: 2,
      }).format(numericValue);
    }

    if (isDateColumn(column)) {
      return (
        <>
          <span className="dateValueFull">{formatCellValue(column, value)}</span>
          <span className="dateValueCompact">{formatMonthYearValue(value)}</span>
        </>
      );
    }

    return formatCellValue(column, value);
  }

  /**
   * Formate une valeur du tableau d'administration des utilisateurs.
   *
   * @param {string} column - Nom de colonne utilisateur.
   * @param {unknown} value - Valeur brute de cellule.
   * @returns {string|import("react").JSX.Element} Valeur prete a afficher.
   */
  static formatUserValue(column, value) {
    if (this.isEmpty(value)) {
      return "-";
    }
    if (column === "profile") {
      return profileLabels[String(value).toUpperCase()] || String(value);
    }
    if (column === "status") {
      return statusLabels[String(value).toUpperCase()] || String(value);
    }
    if (column === "is_email_verified") {
      return this.renderBooleanIcon(Boolean(value), "Email verifie", "Email non verifie");
    }
    if (["creation_date", "last_connexion_date"].includes(column)) {
      return this.formatBrowserDateTime(value);
    }
    if (typeof value === "boolean") {
      return value ? "Oui" : "Non";
    }
    return String(value);
  }

  /**
   * Formate une date avec la locale et le fuseau horaire du navigateur.
   *
   * @param {unknown} value - Date ISO retournee par l'API.
   * @returns {string} Date locale ou valeur brute si la date est invalide.
   */
  static formatBrowserDateTime(value) {
    if (this.isEmpty(value)) {
      return "-";
    }
    const date = new Date(String(value));
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    return new Intl.DateTimeFormat(window.navigator.language, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  /**
   * Rend des pictogrammes de region/version pour une cellule `Version`.
   *
   * @param {unknown} value - Valeur brute de version.
   * @returns {string|import("react").JSX.Element} Tiret si vide, sinon icones de version.
   */
  static formatVersionValue(value) {
    if (this.isEmpty(value)) {
      return "-";
    }

    const versionText = String(value).trim();
    const regionFlag = regionFlags[versionText.toUpperCase()];
    if (regionFlag) {
      return (
        <span
          className="versionIcons"
          aria-label={`Region ${versionText}`}
          title={`Region ${versionText}`}
          role="img"
        >
          {regionFlag}
        </span>
      );
    }

    const normalized = versionText.toLowerCase();
    const icons = [];

    if (normalized.includes("pal")) {
      icons.push("🌍");
    }
    if (normalized.includes("ntsc")) {
      icons.push("📺");
    }
    if (normalized.includes("jap")) {
      icons.push("🇯🇵");
    }
    if (normalized.includes("us")) {
      icons.push("🇺🇸");
    }
    if (normalized.includes("fr")) {
      icons.push("🇫🇷");
    }

    if (icons.length === 0) {
      return "-";
    }

    return (
      <span
        className="versionIcons"
        aria-label={`Region ${versionText}`}
        title={`Region ${versionText}`}
        role="img"
      >
        {icons.join(" ")}
      </span>
    );
  }

  /**
   * Rend un booleen sous forme d'icone accessible.
   *
   * @param {boolean} value - Valeur booleenne.
   * @param {string} trueLabel - Libelle accessible pour `true`.
   * @param {string} falseLabel - Libelle accessible pour `false`.
   * @returns {import("react").JSX.Element} Icone d'etat.
   */
  static renderBooleanIcon(value, trueLabel, falseLabel) {
    const label = value ? trueLabel : falseLabel;
    return (
      <span
        className={`tableBooleanIcon ${value ? "isTrue" : "isFalse"}`}
        aria-label={label}
        title={label}
        role="img"
      >
        <svg aria-hidden="true" viewBox="0 0 24 24">
          {value ? (
            <path d="M9.55 17.3 4.9 12.65l1.4-1.4 3.25 3.25 8.15-8.15 1.4 1.4-9.55 9.55Z" />
          ) : (
            <path d="m12 13.4-4.3 4.3-1.4-1.4 4.3-4.3-4.3-4.3 1.4-1.4 4.3 4.3 4.3-4.3 1.4 1.4-4.3 4.3 4.3 4.3-1.4 1.4-4.3-4.3Z" />
          )}
        </svg>
      </span>
    );
  }

  /**
   * Indique si une valeur doit etre affichee comme absente.
   *
   * @param {unknown} value - Valeur brute.
   * @returns {boolean} `true` si la valeur est vide.
   */
  static isEmpty(value) {
    return value === null || value === undefined || value === "";
  }
}

export default TableColumnFormatService;
