/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-15
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page React de detail d'une plateforme publique.
 */
import { useRef } from "react";

import { formatCellValue } from "../collectionUtils";
import LibraryApi from "../services/LibraryApi";
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";

const EMPTY_VALUE = "-";

/**
 * Affiche la page dediee au detail d'une plateforme Bibliotheque.
 *
 * @param {Object} props - Donnees de plateforme, session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Vue detail plateforme.
 */
function LibraryPlatformDetailView({
  platformDetailPage,
  isAuthenticated,
  canUseCollectionViews,
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
  const platform = platformDetailPage?.platformDetail;
  const title = platform?.name || "Plateforme";
  const aliases = platform?.aliases || [];
  const fields = buildPlatformFields(platform);
  const imageDisplay = buildImageDisplay(platform, platformDetailPage?.imageCacheVersion);
  const canUploadImage = isAuthenticated && authenticatedProfile !== "ADMIN";
  const imageInputRef = useRef(null);

  return (
    <PageLayout
      shellClassName="appShell gameDetailShell"
      eyebrow="Bibliotheque"
      title={title}
      subtitle="Detail de la plateforme"
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
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

      {platformDetailPage?.isLoadingPlatformDetail ? <ProgressBar label="Chargement de la plateforme" /> : null}
      {platformDetailPage?.platformDetailError ? <p className="error">{platformDetailPage.platformDetailError}</p> : null}

      {!platformDetailPage?.isLoadingPlatformDetail && platform ? (
        <section className="gameDetailContent" aria-label="Informations de la plateforme">
          {imageDisplay.featuredImage ? (
            <section className="platformImagesSection" aria-label="Images de la plateforme">
              <figure className="platformFeaturedImage">
                <img
                  src={imageDisplay.featuredImage.url}
                  alt={`${title} - image principale`}
                  loading="eager"
                />
              </figure>
              {imageDisplay.carouselImages.length ? (
                <div className="platformImageCarousel" aria-label="Images complementaires">
                  {imageDisplay.carouselImages.map((image, index) => (
                    <img
                      key={image.id}
                      src={image.url}
                      alt={`${title} - image ${index + 2}`}
                      loading="lazy"
                    />
                  ))}
                </div>
              ) : null}
            </section>
          ) : null}

          <div className="gameDetailSummary">
            <span>{platform.manufacturer || EMPTY_VALUE}</span>
            <strong>{title}</strong>
          </div>

          {canUploadImage ? (
            <form
              className="platformImageUploadForm"
              onSubmit={(event) => event.preventDefault()}
            >
              <button
                type="button"
                disabled={platformDetailPage?.isUploadingPlatformImage}
                onClick={() => imageInputRef.current?.click()}
              >
                Ajouter une image
              </button>
              <input
                ref={imageInputRef}
                id="platform-image-upload"
                className="platformImageFileInput"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                disabled={platformDetailPage?.isUploadingPlatformImage}
                onChange={(event) => {
                  const imageFile = event.target.files?.[0] || null;
                  if (imageFile) {
                    platformDetailPage?.uploadPlatformImage(imageFile);
                    event.target.value = "";
                  }
                }}
              />
              {platformDetailPage?.isUploadingPlatformImage ? <ProgressBar label="Envoi de l'image" /> : null}
              {platformDetailPage?.platformImageUploadError ? (
                <p className="error">{platformDetailPage.platformImageUploadError}</p>
              ) : null}
              {platformDetailPage?.platformImageUploadMessage ? (
                <p className="success">{platformDetailPage.platformImageUploadMessage}</p>
              ) : null}
            </form>
          ) : null}

          <dl className="gameDetailGrid">
            {fields.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value || EMPTY_VALUE}</dd>
              </div>
            ))}
          </dl>
          <section className="platformAliasesSection" aria-label="Alias de la plateforme">
            <h2>Alias</h2>
            {aliases.length ? (
              <ul className="platformAliasList">
                {aliases.map((alias) => (
                  <li key={`${alias.name}-${alias.usage_region}`} className="platformAliasItem">
                    <strong>{alias.name || EMPTY_VALUE}</strong>
                    <span className={getAliasRegionClassName(alias.usage_region)}>
                      {alias.usage_region || "Region non precisee"}
                    </span>
                    {alias.category ? <small>{alias.category}</small> : null}
                    {alias.comment ? <p>{alias.comment}</p> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="platformAliasEmpty">Aucun alias reference.</p>
            )}
          </section>
        </section>
      ) : null}
    </PageLayout>
  );
}

function buildImageDisplay(platform, cacheVersion) {
  const images = Array.isArray(platform?.images) ? platform.images : [];
  const imagesWithUrls = images
    .filter((image) => image?.id)
    .map((image) => ({
      ...image,
      url: LibraryApi.buildPlatformImageUrl(platform.id, image.id, cacheVersion),
    }));
  const featuredImage =
    imagesWithUrls.find((image) => image.type === "MAIN") ||
    imagesWithUrls.find((image) => image.type === "OTHER") ||
    null;
  const carouselImages = imagesWithUrls
    .filter((image) => image.id !== featuredImage?.id)
    .slice(0, 5);
  return { featuredImage, carouselImages };
}

function buildPlatformFields(platform) {
  if (!platform) {
    return [];
  }
  return [
    ["Constructeur", formatCellValue("Texte", platform.manufacturer)],
    ["Date de sortie", formatCellValue("Date", platform.release_date)],
    ["Date de fin", formatCellValue("Date", platform.end_date)],
    ["Jeux associes", formatCellValue("Nombre", platform.total_games)],
    ["Description", formatDescription(platform.description)],
  ];
}

function formatDescription(description) {
  if (!description) {
    return "";
  }
  if (typeof description === "string") {
    return description;
  }
  return Object.values(description)
    .filter((value) => value !== null && value !== undefined && String(value).trim())
    .join(" - ");
}

function getAliasRegionClassName(region) {
  const normalizedRegion = String(region || "").toLowerCase();
  return normalizedRegion.includes("japon") || normalizedRegion.includes("japan")
    ? "platformAliasRegion platformAliasRegionHighlighted"
    : "platformAliasRegion";
}

export default LibraryPlatformDetailView;
