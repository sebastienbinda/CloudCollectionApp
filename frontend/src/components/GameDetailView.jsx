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
  selectedGameSource,
  isAuthenticated,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
  onBack,
}) {
  const game = gameDetailPage?.gameDetail;
  const isCollectionSource = selectedGameSource === "collection";
  const title = getGameName(game) || "Jeu";
  const platformName = getGamePlatform(game);
  const fields = buildGameFields(game, isCollectionSource);

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
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <button className="backButton" type="button" onClick={onBack}>
        Retour
      </button>

      {gameDetailPage?.isLoadingGameDetail ? <ProgressBar label="Chargement du jeu" /> : null}
      {gameDetailPage?.gameDetailError ? <p className="error">{gameDetailPage.gameDetailError}</p> : null}

      {!gameDetailPage?.isLoadingGameDetail && game ? (
        <section className="gameDetailContent" aria-label="Informations du jeu">
          <div className="gameDetailSummary">
            <span>{platformName || EMPTY_VALUE}</span>
            <strong>{title}</strong>
          </div>
          <dl className="gameDetailGrid">
            {fields.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value || EMPTY_VALUE}</dd>
              </div>
            ))}
          </dl>
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
