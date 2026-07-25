/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-13
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React de detail d'un jeu.
 */
import { formatCellValue } from "../collectionUtils";
import { buildGameDetailOwnershipIndicator } from "../gameDetailOwnershipIndicator";
import { buildGameMarketplaceSearchLinks } from "../gameMarketplaceSearchLinks";
import TableColumnFormatService from "../services/TableColumnFormatService.jsx";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

const EMPTY_VALUE = "-";

/**
 * Affiche la page dediee au detail d'un jeu selectionne.
 *
 * @param {Object} props - Donnees de jeu, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue detail jeu.
 */
function GameDetailView({
  gameDetailPage,
  gameResultNavigation,
  selectedGameSource,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onOpenGameDuplicateAdmin,
  onLogout,
  onBack,
}) {
  const game = gameDetailPage?.gameDetail;
  const isCollectionSource = selectedGameSource === "collection";
  const title = getGameName(game) || "Jeu";
  const platformName = getGamePlatform(game);
  const fields = buildGameFields(game, isCollectionSource);
  const marketplaceSearchLinks = buildGameMarketplaceSearchLinks(
    getGameName(game),
    getGameMarketplacePlatformName(game),
    getGamePlatformEndDate(game),
    new Date(),
    getGameMarketplaceRegion(game, isCollectionSource)
  );
  const ownershipIndicator = buildGameDetailOwnershipIndicator(
    Boolean(gameDetailPage?.isInCurrentUserCollection),
    Boolean(gameDetailPage?.isInCurrentUserWishlist)
  );

  return (
    <PageLayout
      shellClassName="appShell gameDetailShell"
      eyebrow={isCollectionSource ? "Collection" : "Bibliotheque"}
      title={title}
      subtitle={platformName ? `Plateforme : ${platformName}` : "Detail du jeu"}
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <div className="gameDetailTopActions">
        <button className="backButton" type="button" onClick={onBack}>
          Retour
        </button>
        <div className="gameResultNavigationActions" aria-label="Navigation entre les jeux">
          <button
            className="secondaryButton"
            type="button"
            disabled={
              !gameResultNavigation?.canOpenPreviousGame ||
              gameResultNavigation?.isLoadingAdjacentGame
            }
            onClick={gameResultNavigation?.openPreviousGame}
          >
            Precedent
          </button>
          {gameResultNavigation?.positionLabel ? (
            <span>{gameResultNavigation.positionLabel}</span>
          ) : null}
          <button
            className="secondaryButton"
            type="button"
            disabled={
              !gameResultNavigation?.canOpenNextGame ||
              gameResultNavigation?.isLoadingAdjacentGame
            }
            onClick={gameResultNavigation?.openNextGame}
          >
            Suivant
          </button>
        </div>
        {gameDetailPage?.canReportDuplicate ? (
          <button
            className="secondaryButton gameDuplicateReportTopButton"
            type="button"
            disabled={gameDetailPage.isReportingDuplicate}
            onClick={gameDetailPage.reportDuplicate}
          >
            Indiquer un doublon
          </button>
        ) : null}
      </div>

      {gameDetailPage?.isLoadingGameDetail ? <ProgressBar label="Chargement du jeu" /> : null}
      {gameDetailPage?.gameDetailError ? <p className="error">{gameDetailPage.gameDetailError}</p> : null}
      {gameDetailPage?.duplicateReportMessage ? (
        <p className="success">{gameDetailPage.duplicateReportMessage}</p>
      ) : null}
      {gameDetailPage?.duplicateReportError ? (
        <p className="error">{gameDetailPage.duplicateReportError}</p>
      ) : null}

      {!gameDetailPage?.isLoadingGameDetail && game ? (
        <section className="gameDetailContent" aria-label="Informations du jeu">
          <div className="gameDetailSummary">
            <div className="gameDetailTitleBlock">
              <span>{platformName || EMPTY_VALUE}</span>
              <strong>{title}</strong>
            </div>
            {ownershipIndicator ? (
              <div className={ownershipIndicator.className} aria-label={ownershipIndicator.ariaLabel}>
                <svg aria-hidden="true" viewBox="0 0 24 24">
                  <path d={ownershipIndicator.icon === "star"
                    ? "m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1L12 16.9 6.6 19.8l1-6.1-4.4-4.3 6.1-.9L12 3Z"
                    : "M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z"}
                  />
                </svg>
                <span>{ownershipIndicator.label}</span>
              </div>
            ) : null}
          </div>
          <dl className="gameDetailGrid">
            {fields.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value || EMPTY_VALUE}</dd>
              </div>
            ))}
          </dl>
          {marketplaceSearchLinks.length ? (
            <section className="gamePurchaseSection" aria-labelledby="game-purchase-title">
              <h2 id="game-purchase-title">Acheter ce jeu</h2>
              <div className="gameMarketplaceActions">
                {marketplaceSearchLinks.map((link) => (
                  <a
                    key={link.key}
                    className="secondaryButton gameMarketplaceSearchButton"
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img src={link.iconUrl} alt="" aria-hidden="true" loading="lazy" />
                    {link.label}
                  </a>
                ))}
              </div>
            </section>
          ) : null}
          <div className="gameDetailActions">
            {gameDetailPage.canCorrectDuplicate ? (
              <button
                className="primaryAction"
                type="button"
                onClick={() => onOpenGameDuplicateAdmin(game)}
              >
                Corriger un doublon
              </button>
            ) : null}
          </div>
        </section>
      ) : null}
    </PageLayout>
  );
}

function getGameName(game) {
  return game?.["Nom du jeu"] || game?.name || "";
}

function getGamePlatform(game) {
  return game?.Plateforme || game?.platform || game?.platform_name || "";
}

function getGamePlatformEndDate(game) {
  return game?.platform_end_date || game?.["Date de fin plateforme"] || "";
}

function getGameMarketplacePlatformName(game) {
  return game?.platform_common_alias || game?.["Alias courant plateforme"] || getGamePlatform(game);
}

function getGameMarketplaceRegion(game, isCollectionSource) {
  return isCollectionSource ? game?.Region || game?.region || "" : "";
}

function buildGameFields(game, isCollectionSource) {
  if (!game) {
    return [];
  }
  if (isCollectionSource) {
    return [
      ["Plateforme", formatCellValue("Plateforme", game.Plateforme)],
      ["Studio", formatCellValue("Studio", game.Studio)],
      ["Date de sortie", formatCellValue("Date", game["Date de sortie"])],
      ["Prix d'achat", formatPurchasePrice(game["Prix d'achat"], game.priceUnit)],
      ["Date d'achat", formatCellValue("Date", game["Date d'achat"])],
      ["Lieu d'achat", formatCellValue("Texte", game["Lieu d'achat"])],
      ["Note", formatCellValue("Note", game.Note)],
      ["Etat", formatCondition(game.Etat)],
      ["Notice", formatBoolean(game.Notice)],
      ["Collector", formatBoolean(game.Collector)],
      ["Steelbook", formatBoolean(game.Steelbook)],
      ["Version digitale", formatBoolean(game["Version digitale"])],
      ["Region", TableColumnFormatService.formatVersionValue(game.Region)],
      ["Description", game.Description],
    ].filter(([, value]) => value !== null && value !== undefined && value !== "");
  }
  return [
    ["Plateforme", formatCellValue("Plateforme", game.platform)],
    ["Developpeur", formatCellValue("Studio", game.developer)],
    ["Editeur", formatCellValue("Studio", game.editor)],
    ["Date de sortie", formatCellValue("Date", game.release_date)],
    ["Statut", formatCellValue("Statut", game.status)],
  ];
}

function formatPurchasePrice(value, priceUnit) {
  if (value === null || value === undefined || value === "" || !priceUnit) {
    return null;
  }
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: priceUnit,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function formatCondition(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  return ["Mauvais", "Correct", "Bon", "Très bon", "Neuf"][Number(value)] || null;
}

function formatBoolean(value) {
  if (value === null || value === undefined) {
    return null;
  }
  return value ? "Oui" : "Non";
}

export default GameDetailView;
