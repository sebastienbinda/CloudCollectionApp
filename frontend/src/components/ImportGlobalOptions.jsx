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
 * Description : options globales affichees selon les colonnes importees.
 */

/**
 * Affiche les options globales liees aux colonnes prix et note configurees.
 *
 * @param {Object} props - Configuration courante et callback de modification.
 * @returns {import("react").JSX.Element|null} Options globales visibles si necessaire.
 * @throws {void} Ne leve pas d'exception.
 */
function ImportGlobalOptions({
  showPriceUnit,
  showRatingBase,
  priceUnit,
  ratingBase,
  disabled = false,
  onConfigurationChange,
}) {
  if (!showPriceUnit && !showRatingBase) {
    return null;
  }

  return (
    <section className="importGlobalOptions" aria-label="Options globales d'import">
      {showPriceUnit ? (
        <label>
          Unité des prix
          <select
            value={priceUnit}
            disabled={disabled}
            onChange={(event) => onConfigurationChange("priceUnit", event.target.value)}
          >
            {["EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "KRW"].map(
              (unit) => <option key={unit} value={unit}>{unit}</option>
            )}
          </select>
          <span className="fieldHelpText">
            Devise appliquée aux prix d'achat importés. Aucune conversion n'est effectuée.
          </span>
        </label>
      ) : null}

      {showRatingBase ? (
        <label>
          Base de notation
          <input
            type="number"
            min="1"
            value={ratingBase}
            disabled={disabled}
            onChange={(event) => onConfigurationChange("ratingBase", event.target.value)}
          />
          <span className="fieldHelpText">
            Base utilisée pour les notes simples, par exemple 10 pour une note sur 10.
          </span>
        </label>
      ) : null}
    </section>
  );
}

export { ImportGlobalOptions };
